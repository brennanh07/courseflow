from rest_framework import serializers
from .models import Subject, Professor, Section, SectionTime, User, Preference, Weight, Schedule, ScheduleLog

class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = '__all__'
        
class ProfessorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Professor
        fields = '__all__'
        
class SectionSerializer(serializers.ModelSerializer):
    professor = ProfessorSerializer()
    
    class Meta:
        model = Section
        fields = '__all__'
        
class SectionTimeSerializer(serializers.ModelSerializer):
    class Meta:
        model = SectionTime
        fields = '__all__'
        
        
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'
        
        
class PreferenceSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    
    class Meta:
        model = Preference
        fields = '__all__'
        
        
class WeightSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    
    class Meta:
        model = Weight
        fields = '__all__'
        
        
class ScheduleSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    
    class Meta:
        model = Schedule
        fields = '__all__'
        
        
class ScheduleLogSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    
    class Meta:
        model = ScheduleLog
        fields = '__all__'