from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.views import APIView
from scheduler.models import Subject, Professor, Section, SectionTime, User, Preference, Weight, Schedule, ScheduleLog
from scheduler.serializers import (
    SubjectSerializer, ProfessorSerializer, SectionSerializer, SectionTimeSerializer, UserSerializer, PreferenceSerializer, 
    WeightSerializer, ScheduleSerializer, ScheduleLogSerializer, ScheduleInputSerializer, BreakSerializer
)
from . import schedule_scoring

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
    def post(self, request):
        serializer = ScheduleInputSerializer(data=request.data)
        if serializer.is_valid():
            user_input = serializer.validated_data
            generated_schedules = schedule_scoring(user_input)
            return Response({"schedules": generated_schedules}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
