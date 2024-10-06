# new schedule_scoring.py
import datetime
from collections import defaultdict
import logging
from itertools import groupby
from operator import attrgetter
from functools import lru_cache

# Setup logging
logging.basicConfig(level=logging.DEBUG, filename='scheduler.log', filemode='w')

class ScheduleScorer:
    def __init__(self, preferences):
        self.preferences = preferences
        
    def score_schedule(self, schedule):
        """
        Score an entire schedule based on the user preferences.
        
        Args:
            schedule (list): List of SectionTime objects in the schedule
            
        Returns:
            float: Combined score of the schedule
        """
        grouped_sections = self.group_section_times_by_section(schedule) # Group SectionTime objects by Section objects
        
        total_score = sum(self.score_section(section, section_times) for section, section_times in grouped_sections.items())
        
        logging.debug(f"Schedule: {schedule}, Score: {total_score}")
        
        return total_score
    
    def group_section_times_by_section(self, section_times):
        
        grouped_sections = defaultdict(list)
        for section_time in section_times:
            grouped_sections[section_time.crn].append(section_time)
        return grouped_sections
    
    def score_section(self, section, section_times):
        """
        """
        total_score = sum(self.score_section_time(section_time) for section_time in section_times)
        
        return total_score / len(section_times) if section_times else 0 # Average score across all SectionTime objects
    
    def score_section_time(self, section_time):
        """
        """
        preferred_days = set(self.preferences['preferred_days'])
        preferred_time = self.preferences['preferred_time']
        
        # Handle edge case of "00:00:00" (online or arranged courses)
        if section_time.begin_time == datetime.time(0, 0):
            day_score = 1
            time_score = 1
            matching_days = "N/A"
            
        else:
            matching_days = set(section_time.days).intersection(preferred_days)
            day_score = len(matching_days) / len(section_time.days)
            time_score = self.score_time(section_time.begin_time)
        
        return (day_score * self.preferences['day_weight']) + (time_score * self.preferences['time_weight'])
    
    @lru_cache(maxsize=128)
    def score_time(self, begin_time):
        """
        """
        preferred_time = self.preferences['preferred_time']
        
        time_ranges = {
            'morning': (datetime.time(8, 0), datetime.time(12, 0)),  # 8:00 AM to 12:00 PM
            'afternoon': (datetime.time(12, 0), datetime.time(16, 0)),  # 12:00 PM to 4:00 PM
            'evening': (datetime.time(16, 0), datetime.time(20, 0)),  # 4:00 PM to 8:00 PM
        }
        
        if preferred_time not in time_ranges:
            return None
        
        preferred_start, preferred_end = time_ranges[preferred_time]
        
        # Convert times to datetime on an arbitrary date for comparison
        arbitrary_date = datetime.date(1, 1, 1)
        begin_dt = datetime.datetime.combine(arbitrary_date, begin_time)
        preferred_start_dt = datetime.datetime.combine(arbitrary_date, preferred_start)
        preferred_end_dt = datetime.datetime.combine(arbitrary_date, preferred_end)
        
        
        # Calculate the score based on the proximity to the preferred time
        if begin_dt < preferred_start_dt:
        # Calculate how far the class start time is before the preferred start time
            score = max(0, 1 - (preferred_start_dt - begin_dt).seconds / 3600)
        
        elif preferred_start_dt <= begin_dt <= preferred_end_dt:
        # Perfect match if the class start time is within the preferred range
            score = 1
        
        else:
        # Calculate how far the class start time is after the preferred end time
            score = max(0, 1 - (begin_dt - preferred_end_dt).seconds / 3600)
        
        return score
    
    
# New schedule_generator.py
import django
import os
import heapq
from schedule_scoring import ScheduleScorer
from conflict_checker import is_valid_combination
from logging_config import loggers
from itertools import product
from collections import defaultdict
from functools import lru_cache

logger = loggers['schedule_generator']

# Setup Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'class_scheduler.settings')
django.setup()

# class ScheduleGenerator:
#     def __init__(self, section_dict, section_time_dict, breaks, preferences, max_schedules=10):
#         self.section_dict = section_dict
#         self.section_time_dict = section_time_dict
#         self.breaks = breaks
#         self.preferences = preferences
#         self.max_schedules = max_schedules
#         self.valid_schedules = []
#         self.heap = []
#         self.scorer = ScheduleScorer(self.preferences)
        
#     def generate_schedules(self):
#         logger.info("Starting schedule generation")
        
#         self.generate_valid_schedules() # Generate all valid schedules, populating the heap
        
#         logger.info(f"Generated {len(self.heap)} valid schedules")
        
#         top_schedules = [schedule for _, schedule in sorted(self.heap, key=lambda x: -x[0])] # Top schedules sorted by score
        
#         # Detailed logging for each schedule
#         for i, schedule in enumerate(top_schedules):
#             logger.debug(f"Schedule {i + 1}:")
#             logger.debug(f" {schedule}")
#             for section_time in schedule[1]:
#                 logger.debug(f"  Section: {section_time.crn.course}, Days: {section_time.days}, Time: {section_time.begin_time} - {section_time.end_time}")
        
#         return top_schedules
    
#     def generate_valid_schedules(self, current_combination=[], selected_courses=set(), cached_section_times=None):
#         """
#         Recursively generate all valid schedules with early pruning.
        
#         Args:
#             section_dict (dict): Dictionary mapping CRNs to Section objects
#             section_time_dict (dict): Dictionary mapping CRNs to lists of SectionTime objects
#             current_combination (list): The current combination of SectionTime objects being considered
#             valid_schedules (list): List to store valid schedules
#             selected_courses (set): Set to track courses that have already been added to the current combination
#         """
#         # Initialize cache of SectionTime objects if it's the first call
#         if cached_section_times is None:
#             cached_section_times = {} # Cache of SectionTime objects for each section
        
#         # Base case: If all courses have been processed, score the current schedule
#         if len(selected_courses) == len(set(section.course for section in self.section_dict.values())): # If all courses have been added
            
            
#             score = self.scorer.score_schedule(current_combination) # Score the current schedule
#             schedule_tuple = (score, tuple(current_combination)) # Create a tuple of the score and schedule
            
#             logger.debug(f"Scoring schedule: {current_combination}, Score: {score}")
            
#             if len(self.heap) < self.max_schedules: # If the heap is not full
#                 heapq.heappush(self.heap, (score, schedule_tuple)) # Push the score and schedule to the heap
#             elif score > -self.heap[0][0]: # If the score is better than the worst score in the heap
#                 heapq.heappushpop(self.heap, (-score, schedule_tuple))  # Push the score and schedule to the heap, and pop the worst score
            
#             return
        
#         remaining_courses = [section.course for crn, section in self.section_dict.items() if section.course not in selected_courses]
        
#         if not remaining_courses:
#             logger.warning("No remaining courses to process")
#             return
        
#         next_course = remaining_courses[0]
#         logger.debug(f"Processing next course: {next_course}")
        
#         # Iterate over all sections of the next course
#         for crn, section in self.section_dict.items():
#             if section.course == next_course:
                
#                 # Fetch and cache SectionTime objects if they are not already cached
#                 if crn not in cached_section_times:
#                     cached_section_times[crn] = self.section_time_dict[crn]
                
#                 # Get all SectionTime objects for the section
#                 section_times = cached_section_times[crn]
                
#                 # Early prune: Check if adding this section's times causes any conflicts
#                 if not is_valid_combination(current_combination, section_times, self.breaks):
#                     logger.debug(f"Pruned invalid combination for course {next_course}, CRN {crn}")
#                     continue  # Prune this combination early if it leads to conflicts
                
#                 new_combination = current_combination + section_times
                
#                 if self.heap and len(self.heap) == self.max_schedules:
#                     partial_score = self.scorer.score_schedule(new_combination)
#                     if partial_score < -self.heap[0][0]:
#                         logger.debug(f"Pruned low-scoring partial schedule. Score: {partial_score}")
#                         continue
                
#                 # Recurse with the new combination and cace of SectionTime objects
#                 self.generate_valid_schedules(
#                     new_combination,
#                     selected_courses | {section.course},
#                     cached_section_times,
#                 )


class ScheduleGenerator:
    def __init__(self, section_dict, section_time_dict, breaks, preferences, max_schedules=10):
        self.section_dict = section_dict
        self.section_time_dict = section_time_dict
        self.breaks = breaks
        self.preferences = preferences
        self.max_schedules = max_schedules
        self.scorer = ScheduleScorer(self.preferences)
        
        # Group section times by course
        self.course_sections = defaultdict(list)
        for crn, section in section_dict.items():
            self.course_sections[section.course].append((crn, section_time_dict[crn]))

    def generate_schedules(self):
        courses = list(self.course_sections.keys())
        all_combinations = product(*self.course_sections.values())
        
        heap = []
        schedules = {}
        
        for i, combination in enumerate(all_combinations):
            schedule = {crn: times for crn, times in combination}
            flat_schedule = [time for times in schedule.values() for time in times]
            
            if not self.is_valid_combination(flat_schedule):
                continue
            
            score = self.scorer.score_schedule(flat_schedule)
            
            if len(heap) < self.max_schedules:
                heapq.heappush(heap, (-score, i))
                schedules[i] = schedule
            elif score > -heap[0][0]:
                _, old_index = heapq.heappushpop(heap, (-score, i))
                schedules[i] = schedule
                schedules.pop(old_index, None)
        
        return [(abs(score), schedules[i]) for score, i in sorted(heap, key=lambda x: x[0])]

    def is_valid_combination(self, combination):
        for i, time1 in enumerate(combination):
            for time2 in combination[i+1:]:
                if self.check_conflict(time1, time2):
                    return False
            for break_time in self.breaks:
                if (time1.begin_time >= break_time['begin_time'] and 
                    time1.begin_time <= break_time['end_time']):
                    return False
        return True

    def check_conflict(self, time1, time2):
        if set(time1.days) & set(time2.days):
            return (time1.begin_time < time2.end_time and time2.begin_time < time1.end_time)
        return False
                


                
# conflict_checker.py
def check_conflict(time1, time2):
    """
    Check if two SectionTime objects conflict in terms of day and time.
    
    Args:
        time1, time2 (SectionTime): SectionTime objects to compare.
        
    Returns:
        bool: True if the two times conflict, False otherwise.
    """
    # check if the days of the two SectionTime objects overlap
    if set(time1.days).intersection(set(time2.days)):  # Overlapping days
        
        # check if the end time of time1 is greater than the begin time of time2
        if time1.end_time > time2.begin_time and time1.begin_time < time2.end_time: 
            # print(f"Conflict found: {time1} conflicts with {time2}")
            return True
    
    return False  


def is_valid_combination(current_combination, new_section_times, breaks):
    """
    Check if adding new SectionTime objects to the current combination results in any conflicts.
    
    Args:
        current_combination (list): The current combination of SectionTime objects.
        new_section_times (list): SectionTime objects to add to the combination.
        breaks (list): List of break times to avoid conflicts with.
        
    Returns:
        bool: True if the combination remains valid after adding the new SectionTime objects.
    """
    for new_time in new_section_times: # iterate through the new_section_times
        for existing_time in current_combination: # iterate through the current_combination
            
            # check if there is a conflict between the new_time and existing_time
            if check_conflict(new_time, existing_time):
                # print(f"Pruned due to conflict: {new_time} with existing {existing_time}")
                return False
        
        # Check for conflicts with the breaks
        for break_time in breaks:
            
            # check if the begin time of new_time is greater than or equal to the begin time of break_time and less than or equal to the end time of break_time
            if new_time.begin_time >= break_time['begin_time'] and new_time.begin_time <= break_time['end_time']:
                # print(f"Pruned due to break conflict: {new_time} with break {break_time}")
                return False

    return True

# fetch_sections.py
import logging
import django
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'class_scheduler.settings')
django.setup()

from scheduler.models import Section, SectionTime

logging.basicConfig(level=logging.DEBUG, filename='fetch_sections.log', filemode='w')

class SectionFetcher:
    def __init__(self, courses):
        self.courses = courses
        self.section_dict = {}
        self.section_time_dict = {}
        
    def fetch_sections(self):
        """
        Fetch all sections and their corresponding times for the given courses using batch fetching.
        
        Args:
            courses (list): A list of courses to fetch sections for.
            
        Returns:
            section_dict (dict): Dictionary mapping CRNs to Section objects.
            section_time_dict (dict): Dictionary mapping CRNs to lists of SectionTime objects.
        """
        sections = Section.objects.filter(course__in=self.courses).prefetch_related('sectiontime_set')
        self.section_dict = {section.crn: section for section in sections}
        self.section_time_dict = {section.crn: list(section.sectiontime_set.all()) for section in sections}
        
        logging.debug(f"Fetched sections: {self.section_dict}")
        logging.debug(f"Fetched section times: {self.section_time_dict}")
        
        return self.section_dict, self.section_time_dict
    
    
# main.py
from fetch_sections import SectionFetcher
from schedule_generator import ScheduleGenerator
from schedule_formatter import ScheduleFormatter

def process_schedules(courses, breaks, preferences, max_schedules=10):
    """
    Main function to generate and format schedules for the given list of courses and input.
    
    Args:
        courses (list): A list of course codes to generate schedules for
        breaks (list): A list of break times to exclude from schedules
        preferences (dict): A dictionary of user preferences for scheduling
        max_schedules (int): The maximum number of schedules to return
        
    Returns:
        list: A list of formatted schedules as dictionaries with names, days, and CRNs
    """
    # Fetch sections from the database
    section_fetcher = SectionFetcher(courses)
    section_dict, section_time_dict = section_fetcher.fetch_sections()
    
    # Generate and score valid schedules dynamically
    schedule_generator = ScheduleGenerator(section_dict, section_time_dict, breaks, preferences, max_schedules)
    top_schedules = schedule_generator.generate_schedules()
    
    # Format the top N schedules for display
    formatter = ScheduleFormatter(date_format="%I:%M %p")
    
    return formatter.print_ranked_schedules(top_schedules, top_n=max_schedules)

# New views.py
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from scheduler.models import Subject, Professor, Section, SectionTime, User, Preference, Weight, Schedule, ScheduleLog
from scheduler.serializers import (
    SubjectSerializer, ProfessorSerializer, SectionSerializer, SectionTimeSerializer, UserSerializer, PreferenceSerializer, 
    WeightSerializer, ScheduleSerializer, ScheduleLogSerializer, ScheduleInputSerializer, BreakSerializer
)

import logging
from django.http import JsonResponse

from fetch_sections import SectionFetcher
from schedule_generator import ScheduleGenerator
from schedule_scoring import ScheduleScorer
from schedule_formatter import ScheduleFormatter
from main import process_schedules

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
            
            try:
                # Generate, score, and format schedules
                generated_schedules = process_schedules(
                    courses=courses,
                    breaks=breaks,
                    preferences=preferences,
                    max_schedules=10
                )
                return JsonResponse({"schedules": generated_schedules}, status=status.HTTP_200_OK)
            
            except Exception as e:
                logger.error(f"Error generating schedules: {str(e)}")
                return Response({"error": "Failed to generate schedules"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # If the input data is invalid, return a 400 error response
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# serializers.py
from rest_framework import serializers
from scheduler.models import Subject, Professor, Section, SectionTime, User, Preference, Weight, Schedule, ScheduleLog

class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = '__all__'

class ProfessorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Professor
        fields = '__all__'

class SectionSerializer(serializers.ModelSerializer):
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
    class Meta:
        model = Preference
        fields = '__all__'

class WeightSerializer(serializers.ModelSerializer):
    class Meta:
        model = Weight
        fields = '__all__'

class ScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Schedule
        fields = '__all__'

class ScheduleLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScheduleLog
        fields = '__all__'
        
class BreakSerializer(serializers.Serializer):
    begin_time = serializers.TimeField()
    end_time = serializers.TimeField()
        
class ScheduleInputSerializer(serializers.Serializer):
    courses = serializers.ListField(child=serializers.CharField())
    breaks = serializers.ListField(child=BreakSerializer(), allow_empty=True)
    preferred_days = serializers.ListField(child=serializers.CharField(), allow_empty=True)
    preferred_time = serializers.CharField()
    day_weight = serializers.FloatField()
    time_weight = serializers.FloatField()
    
    
# schedule_formatter.py
from collections import defaultdict
from logging_config import loggers

logger = loggers['schedule_formatter']

class ScheduleFormatter:
    def __init__(self, date_format="%I:%M %p"):
        """
        Initialize the ScheduleFormatter object with optional formatting settings.
        
        Args:
            date_format (str): The format string to use for displaying dates and times
        """
        self.date_format = date_format
        
    def format_schedule(self, schedule):
        """
        Formats a schedule into a more readable string format.
        
        Args:
            schedule (list): A list of SectionTime objects representing a schedule
            
        Returns:
            dict: A formatted dictionary representation of the schedule including days and CRNs
        """
        day_schedule = defaultdict(list)
        crn_dict = {}
        
        for section_time in schedule[1]:
            logger.info(f"Processing section_time: {section_time}")
            logger.info(f"section_time.days type: {type(section_time.days)}")
            logger.info(f"section_time.days value: {section_time.days}")
            
            if isinstance(section_time.days, float):
                logger.warning(f"Unexpected float value for days: {section_time.days}")
                day_name = str(int(section_time.days))  # Convert float to string
            elif isinstance(section_time.days, str):
                day_name = section_time.days.capitalize()
            else:
                logger.error(f"Unexpected type for days: {type(section_time.days)}")
                day_name = "Unknown"
            
            try:
                class_info = f"{section_time.crn.course}: {section_time.begin_time.strftime(self.date_format)} - {section_time.end_time.strftime(self.date_format)}"
            except AttributeError as e:
                logger.error(f"Error formatting class info: {e}")
                class_info = "Error: Unable to format class info"
            
            day_schedule[day_name].append((section_time.begin_time, class_info))
            
            if hasattr(section_time.crn, 'course'):
                if section_time.crn.course not in crn_dict:
                    crn_dict[section_time.crn.course] = section_time.crn.crn
            else:
                logger.error(f"section_time.crn does not have 'course' attribute: {section_time.crn}")

        # Sort classes by start time    
        ordered_schedule = {} 
        for day in ["M", "T", "W", "R", "F", "S", "U"]:
            if day in day_schedule:
                ordered_schedule[day] = [class_info for _, class_info in sorted(day_schedule[day])]
            elif "Online" in day_schedule or "Arr" in day_schedule:
                ordered_schedule["Online/ARR"] = [class_info for _, class_info in sorted(day_schedule.get("Online", []) + day_schedule.get("Arr", []))]
            else:
                ordered_schedule[day] = []
            
        return {
            "days": ordered_schedule,
            "crns": crn_dict
        }
        
    def print_ranked_schedules(self, top_schedules, top_n=10):
        """
        Formats the top N schedules as a list of lists where each list contains strings representing each line of the schedule.

        Args:
            top_schedules (list): List of top N schedules to format.
            top_n (int): Number of top schedules to include in the output.

        Returns:
            list: A list of formatted schedules as dictionaries with names, days, and CRNs.
        """
        formatted_schedules_list = []
        
        for i, schedule in enumerate(top_schedules[:top_n], 1):
            try:
                formatted_schedule_data = self.format_schedule(schedule)
                formatted_schedule = {
                    "name": f"Schedule {i}",
                    "days": formatted_schedule_data["days"],
                    "crns": formatted_schedule_data["crns"]
                }
                formatted_schedules_list.append(formatted_schedule)
            except Exception as e:
                logger.error(f"Error formatting schedule {i}: {e}")
        
        return formatted_schedules_list
        
        
        

