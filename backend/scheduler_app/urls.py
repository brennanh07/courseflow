from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SubjectViewSet, ProfessorViewSet, SectionViewSet, UserViewSet, PreferenceViewSet, WeightViewSet, ScheduleViewSet, ScheduleLogViewSet

router = DefaultRouter()
router.register(r'subjects', SubjectViewSet)
router.register(r'professors', ProfessorViewSet)
router.register(r'sections', SectionViewSet)
router.register(r'users', UserViewSet)
router.register(r'preferences', PreferenceViewSet)
router.register(r'weights', WeightViewSet)
router.register(r'schedules', ScheduleViewSet)
router.register(r'schedule_logs', ScheduleLogViewSet)

urlpatterns = [
    path('', include(router.urls)),
]