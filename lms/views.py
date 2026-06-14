from rest_framework import viewsets, generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema, extend_schema_view
from lms.models import Course, Lesson, Subscription, Payment
from lms.serializers import (
    CourseSerializer, CourseCreateUpdateSerializer,
    LessonSerializer, LessonCreateUpdateSerializer,
    SubscriptionSerializer, PaymentSerializer
)
from lms.paginators import CoursePaginator, LessonPaginator
from lms.services import sync_course_with_stripe, create_checkout_session
from lms.tasks import send_course_update_notification
from users.permissions import IsModerator, IsOwner


class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    pagination_class = CoursePaginator

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return CourseCreateUpdateSerializer
        return CourseSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user
        if not user.is_authenticated:
            return qs.none()
        if user.groups.filter(name='Модераторы').exists():
            return qs
        return qs.filter(owner=user)

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.IsAuthenticated()]
        elif self.action == 'create':
            return [permissions.IsAuthenticated(), ~IsModerator()]
        elif self.action in ['update', 'partial_update']:
            return [permissions.IsAuthenticated(), IsOwner() | IsModerator()]
        elif self.action == 'destroy':
            return [permissions.IsAuthenticated(), IsOwner(), ~IsModerator()]
        return [permissions.IsAuthenticated()]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def perform_update(self, serializer):
        instance = self.get_object()
        old_data = {'name': instance.name, 'description': instance.description, 'price': instance.price}
        serializer.save()
        updated_fields = [f for f in ['name', 'description', 'price'] if getattr(instance, f) != old_data.get(f)]
        if updated_fields:
            send_course_update_notification.delay(instance.id, updated_fields)


class LessonListCreateView(generics.ListCreateAPIView):
    queryset = Lesson.objects.select_related('course', 'owner').all()
    pagination_class = LessonPaginator

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return LessonCreateUpdateSerializer
        return LessonSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user
        if not user.is_authenticated:
            return qs.none()
        if user.groups.filter(name='Модераторы').exists():
            return qs
        return qs.filter(owner=user)

    def get_permissions(self):
        if self.request.method == 'POST':
            return [permissions.IsAuthenticated(), ~IsModerator()]
        return [permissions.IsAuthenticated()]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class LessonRetrieveUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Lesson.objects.select_related('course', 'owner').all()

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return LessonCreateUpdateSerializer
        return LessonSerializer

    def get_permissions(self):
        if self.request.method == 'GET':
            return [permissions.IsAuthenticated()]
        elif self.request.method in ['PUT', 'PATCH']:
            return [permissions.IsAuthenticated(), IsOwner() | IsModerator()]
        elif self.request.method == 'DELETE':
            return [permissions.IsAuthenticated(), IsOwner(), ~IsModerator()]
        return [permissions.IsAuthenticated()]


class LessonsByCourseView(generics.ListAPIView):
    serializer_class = LessonSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = LessonPaginator

    def get_queryset(self):
        course_id = self.kwargs.get('course_id')
        user = self.request.user
        qs = Lesson.objects.filter(course_id=course_id).select_related('course', 'owner')
        if user.groups.filter(name='Модераторы').exists():
            return qs
        return qs.filter(owner=user)


class SubscriptionView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        course_id = request.data.get('course_id')
        if not course_id:
            return Response({'error': 'Необходимо указать course_id'}, status=status.HTTP_400_BAD_REQUEST)
        course = get_object_or_404(Course, pk=course_id)
        subscription = Subscription.objects.filter(user=request.user, course=course)
        if subscription.exists():
            subscription.delete()
            message = 'Подписка удалена'
            subscribed = False
        else:
            Subscription.objects.create(user=request.user, course=course)
            message = 'Подписка добавлена'
            subscribed = True
        return Response({'message': message, 'is_subscribed': subscribed, 'course_id': course.id, 'course_name': course.name})

    def get(self, request):
        subscriptions = Subscription.objects.filter(user=request.user).select_related('course')
        serializer = SubscriptionSerializer(subscriptions, many=True)
        return Response(serializer.data)


class CoursePaymentView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk=None):
        course = get_object_or_404(Course, pk=pk)
        if course.price <= 0:
            return Response({'error': 'У данного курса нет установленной цены'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            course = sync_course_with_stripe(course)
            session = create_checkout_session(
                course.stripe_price_id, course.name,
                request.data.get('success_url', 'http://localhost:8000/api/docs/'),
                request.data.get('cancel_url', 'http://localhost:8000/api/docs/')
            )
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        Payment.objects.create(user=request.user, course=course, amount=course.price, stripe_session_id=session.id, payment_url=session.url, status='pending')
        return Response({'payment_url': session.url, 'session_id': session.id}, status=status.HTTP_201_CREATED)


class PaymentListView(generics.ListAPIView):
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Payment.objects.filter(user=self.request.user).select_related('course')