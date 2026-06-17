from rest_framework import serializers
from lms.models import Course, Lesson, Subscription, Payment
from lms.validators import validate_youtube_url


class LessonSerializer(serializers.ModelSerializer):
    course_name = serializers.CharField(source="course.name", read_only=True)

    class Meta:
        model = Lesson
        fields = [
            "id",
            "name",
            "description",
            "preview",
            "video_url",
            "course",
            "course_name",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class LessonCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = ["name", "description", "preview", "video_url", "course"]

    def validate_video_url(self, value):
        validate_youtube_url(value)
        return value


class CourseSerializer(serializers.ModelSerializer):
    lessons_count = serializers.SerializerMethodField()
    lessons = LessonSerializer(many=True, read_only=True)
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = [
            "id",
            "name",
            "preview",
            "description",
            "price",
            "lessons_count",
            "lessons",
            "is_subscribed",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def get_lessons_count(self, obj):
        return obj.lessons.count()

    def get_is_subscribed(self, obj):
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            return Subscription.objects.filter(user=request.user, course=obj).exists()
        return False


class CourseCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ["name", "preview", "description", "price"]


class SubscriptionSerializer(serializers.ModelSerializer):
    course_name = serializers.CharField(source="course.name", read_only=True)

    class Meta:
        model = Subscription
        fields = ["id", "course", "course_name", "created_at"]


class PaymentSerializer(serializers.ModelSerializer):
    course_name = serializers.CharField(source="course.name", read_only=True)

    class Meta:
        model = Payment
        fields = [
            "id",
            "course",
            "course_name",
            "amount",
            "payment_url",
            "status",
            "created_at",
            "paid_at",
        ]
