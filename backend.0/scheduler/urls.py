from django.urls import path, include
# from rest_framework import DefaultRouter
from . import views
from scheduler.views import (
    SubjectViewSet, ProfessorViewSet, SectionViewSet, SectionTimeViewSet, UserViewSet, PreferenceViewSet, 
    WeightViewSet, ScheduleViewSet, ScheduleLogViewSet, GenerateScheduleView
)


# router = DefaultRouter()
# router.register(r'subjects', SubjectViewSet)


urlpatterns = [
    path('generate-schedules/', GenerateScheduleView.as_view(), name='generate-schedules'),
]