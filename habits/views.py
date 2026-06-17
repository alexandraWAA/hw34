from rest_framework import generics, permissions

from habits.models import Habit
from habits.pagination import HabitPagination
from habits.permissions import IsOwner
from habits.serializers import (HabitCreateUpdateSerializer, HabitSerializer,
                                PublicHabitSerializer)


class HabitListCreateView(generics.ListCreateAPIView):
    serializer_class = HabitSerializer
    pagination_class = HabitPagination

    def get_queryset(self):
        return Habit.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.request.method == "POST":
            return HabitCreateUpdateSerializer
        return HabitSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class HabitRetrieveUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Habit.objects.all()
    permission_classes = [permissions.IsAuthenticated, IsOwner]

    def get_serializer_class(self):
        if self.request.method in ["PUT", "PATCH"]:
            return HabitCreateUpdateSerializer
        return HabitSerializer


class PublicHabitListView(generics.ListAPIView):
    serializer_class = PublicHabitSerializer
    pagination_class = HabitPagination
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Habit.objects.filter(is_public=True)
