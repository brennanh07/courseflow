from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from scheduler.models import Subject, Professor, Section, SectionTime, User, Preference, Weight, Schedule, ScheduleLog
from scheduler.serializers import (
    SubjectSerializer, ProfessorSerializer, SectionSerializer, SectionTimeSerializer, UserSerializer, PreferenceSerializer, 
    WeightSerializer, ScheduleSerializer, ScheduleLogSerializer, ScheduleInputSerializer, BreakSerializer
)
from .schedule_scoring import process_input
from .schedule_generator import get_valid_schedules
import logging
from django.http import JsonResponse

logger = logging.getLogger(__name__)

class SubjectViewSet(viewsets.ModelViewSet):
    queryset = Subject.objects.all()
    serializer_class = SubjectSerializer
    
class ProfessorViewSet(viewsets.ModelViewSet):
    queryset = Professor.objects.all()
    serializer_class = ProfessorSerializer
    
class SectionViewSet(viewsets.ModelViewSet):
    queryset = Section.objects.all()
    serializer_class = SectionSerializer
    
class SectionTimeViewSet(viewsets.ModelViewSet):
    queryset = SectionTime.objects.all()
    serializer_class = SectionTimeSerializer
    
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    
class PreferenceViewSet(viewsets.ModelViewSet):
    queryset = Preference.objects.all()
    serializer_class = PreferenceSerializer
    
class WeightViewSet(viewsets.ModelViewSet):
    queryset = Weight.objects.all()
    serializer_class = WeightSerializer
    
class ScheduleViewSet(viewsets.ModelViewSet):
    queryset = Schedule.objects.all()
    serializer_class = ScheduleSerializer
    
class ScheduleLogViewSet(viewsets.ModelViewSet):
    queryset = ScheduleLog.objects.all()
    serializer_class = ScheduleLogSerializer
    
class GenerateScheduleView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        logger.info(f"Request data: {request.data}")
        serializer = ScheduleInputSerializer(data=request.data)
        if serializer.is_valid():
            user_input = serializer.validated_data
            courses = user_input.get("courses")
            breaks = user_input.get("breaks")
            preferences = {
                "preferred_days": user_input.get("preferred_days"),
                "preferred_time": user_input.get("preferred_time"),
                "day_weight": user_input.get("day_weight"),
                "time_weight": user_input.get("time_weight"),
            }
            generated_schedules = process_input(courses=courses, breaks=breaks, preferences=preferences)
            return JsonResponse({"schedules": generated_schedules}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
