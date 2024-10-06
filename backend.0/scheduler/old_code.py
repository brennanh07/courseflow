# Old schedule_generator.py:
import django
import os
import datetime

# Setup Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'class_scheduler.settings')
django.setup()

from scheduler.models import Section, SectionTime

def fetch_sections(courses):
    """
    Fetch all sections and their corresponding times for the given courses using batch fetching.
    
    Args:
        courses (list): A list of courses to fetch sections for.
        
    Returns:
        section_dict (dict): Dictionary mapping CRNs to Section objects.
        section_time_dict (dict): Dictionary mapping CRNs to lists of SectionTime objects.
    """
    # print(f"Fetching sections for courses: {courses}")
    sections = Section.objects.filter(course__in=courses).prefetch_related('sectiontime_set')

    section_dict = {section.crn: section for section in sections}
    section_time_dict = {section.crn: list(section.sectiontime_set.all()) for section in sections}

    # print(f"Fetched {len(section_dict)} sections")
    return section_dict, section_time_dict

def check_conflict(time1, time2):
    """
    Check if two SectionTime objects conflict in terms of day and time.
    
    Args:
        time1, time2 (SectionTime): SectionTime objects to compare.
        
    Returns:
        bool: True if the two times conflict, False otherwise.
    """
    if set(time1.days).intersection(set(time2.days)):  # Overlapping days
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
    for new_time in new_section_times:
        for existing_time in current_combination:
            if check_conflict(new_time, existing_time):
                # print(f"Pruned due to conflict: {new_time} with existing {existing_time}")
                return False
        
        # Check for conflicts with the breaks
        for break_time in breaks:
            if new_time.begin_time >= break_time['begin_time'] and new_time.begin_time <= break_time['end_time']:
                # print(f"Pruned due to break conflict: {new_time} with break {break_time}")
                return False

    return True

def generate_valid_schedules(section_dict, section_time_dict, current_combination=[], valid_schedules=[], selected_courses=set(), breaks=[]):
    """
    Recursively generate all valid schedules with early pruning.
    
    Args:
        section_dict (dict): Dictionary mapping CRNs to Section objects
        section_time_dict (dict): Dictionary mapping CRNs to lists of SectionTime objects
        current_combination (list): The current combination of SectionTime objects being considered
        valid_schedules (list): List to store valid schedules
        selected_courses (set): Set to track courses that have already been added to the current combination
    """
    # print(f"Current combination: {current_combination}")
    # print(f"Selected courses: {selected_courses}")
    
    # Base case: If all courses have been processed, check if the current combination is valid
    if len(selected_courses) == len(set(section.course for section in section_dict.values())):
        # print(f"Valid schedule found: {current_combination}")
        valid_schedules.append(current_combination)
        return

    # Get the next course that hasn't been selected yet
    remaining_courses = [section.course for crn, section in section_dict.items() if section.course not in selected_courses]
    
    if not remaining_courses:
        # print("No remaining courses.")
        return
    
    next_course = remaining_courses[0]
    # print(f"Processing next course: {next_course}")

    # Iterate over all sections of the next course
    for crn, section in section_dict.items():
        if section.course == next_course:
            # print(f"Trying section: {section}")
            
            # Get all SectionTime objects for the section
            section_times = section_time_dict[crn]
            # print(f"Section times: {section_times}")
            
            # Early prune: Check if adding this section's times causes any conflicts
            if not is_valid_combination(current_combination, section_times, breaks):
                # print(f"Pruned section {section.crn} due to conflicts.")
                continue  # Prune this combination early if it leads to conflicts
            
            # Add this section to the current combination
            new_combination = current_combination + section_times
            # print(f"New combination: {new_combination}")
            
            # Continue generating schedules recursively
            generate_valid_schedules(
                section_dict,
                section_time_dict,
                new_combination,
                valid_schedules,
                selected_courses | {section.course}, 
                breaks
            )

def get_valid_schedules(courses, breaks=[]):
    """
    Main function to generate all valid schedules for the given list of courses.
    
    Args:
        courses (list): A list of course codes to generate schedules for
        
    Returns:
        List: List of valid schedules, where each schedule is a list of SectionTime objects
    """
    # print("Starting schedule generation...")
    # Fetch sections and their times for the given courses
    section_dict, section_time_dict = fetch_sections(courses)
    
    # List to store valid schedules
    valid_schedules = []
    
    # Generate all valid schedules with early pruning
    generate_valid_schedules(section_dict, section_time_dict, valid_schedules=valid_schedules, breaks=breaks)
    
    print(f"Total valid schedules: {len(valid_schedules)}")
    
    return valid_schedules

# Old schedule_scoring.py:
import datetime
from schedule_generator import get_valid_schedules
from collections import defaultdict
import heapq
import logging
from itertools import groupby
from operator import attrgetter
import json
from functools import lru_cache

# Setup logging
logging.basicConfig(level=logging.INFO)


def group_section_times_by_section(section_times):
    """
    Groups SectionTime objects by their associated Section objects.
    
    Args:
        section_times (list): List of SectionTime objects
        
    Returns:
        dict: Dictionary where keys are Section objects and values are lists of SectionTime objects
    """
    # section_times.sort(key=attrgetter('crn')) # Sort SectionTime objects by CRN
    
    grouped_sections = {section: list(times) for section, times in groupby(section_times, key=attrgetter('crn'))}
    
    logging.debug(f"Grouped sections: {grouped_sections}")
    
    return grouped_sections


def score_time(begin_time, preferred_time):
    """
    Calculate a time score based on the proximity to the preferred time.
    
    Args:
        begin_time (datetime.time): Start time of the class
        preferences (dict): User preferences, including preferred time of day
        
    Returns:
        float: Score between 0 and 1, where 1 is a perfect match and 0 is no match
    """
    # Convert preferred time of day for classes to a range of times
    if preferred_time == 'morning':
        preferred_start, preferred_end = datetime.time(8, 0), datetime.time(12, 0)  # 8:00 AM to 12:00 PM
    elif preferred_time == 'afternoon':
        preferred_start, preferred_end = datetime.time(12, 0), datetime.time(16, 0)  # 12:00 PM to 4:00 PM
    elif preferred_time == 'evening':
        preferred_start, preferred_end = datetime.time(16, 0), datetime.time(20, 0)  # 4:00 PM to 8:00 PM
    else:
        return None
    
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
    

@lru_cache(maxsize=None)
def score_section_time_cached(section_time, preferred_time, preferred_days, day_weight, time_weight):
    """
    Scores a single SecionTime object based on user preferences, with normalization.
    
    Args:
        section_time (SectionTime): SectionTime object to score
        preferences (dict): User preferences, including preferred days and time of day and weights
        
    Returns:
        float: Normalized score of the SectionTime object
    """
    # Handle edge case of "00:00:00" (online or arranged courses)
    if section_time.begin_time == datetime.time(0, 0):
        day_score = 1
        time_score = 1
        matching_days = "N/A"
    
    else:
        # Calculate the day score based on the proportion of matching days
        matching_days = set(section_time.days).intersection(set(preferred_days))
        day_score = len(matching_days) / len(section_time.days)
        
        # Time score based on proximity to preferred time of day
        time_score = score_time(section_time.begin_time, preferred_time)
        
    
    # Apply weights
    weighted_day_score = day_score * day_weight
    weighted_time_score = time_score * time_weight
    
    # Combined score for this SectionTime
    section_time_score = weighted_day_score + weighted_time_score
    
    # Debugging output
    # logging.debug(f"Scoring SectionTime: {section_time}")
    # logging.debug(f"Matching Days: {matching_days}")
    # logging.debug(f"Day Score: {day_score}, Time Score: {time_score}")
    # logging.debug(f"Total SectionTime Score: {section_time_score}")
    
    return section_time_score

def score_section_time(section_time, preferences):
    return score_section_time_cached(
        section_time, 
        preferences['preferred_time'],
        tuple(preferences['preferred_days']),
        preferences['day_weight'],
        preferences['time_weight']
    )


def score_section(section, section_times, preferences):
    """
    Scores a Section object by averaging the score of its associated SectionTime objects.
    
    Args:
        section (Section): Section object to score
        section_times (list): List of SectionTime objects associated with the Section
        preferences (dict): User preferences for day, time of day, and weights
        
    Returns:
        float: Combined score of the Section object
    """
    # Sum of scores of all SectionTime objects
    total_score = sum(score_section_time(section_time, preferences) for section_time in section_times)
    
    # Average score across all SectionTime objects
    average_score = total_score / len(section_times) if section_times else 0
    
    # Debugging output
    logging.debug(f"Scoring Section: {section}")
    logging.debug(f"Total Section Score: {total_score}, Average Section Score: {average_score}")

    # Return the average score
    return average_score


def score_schedule(schedule, preferences):
    """
    Score an entire schedule by summing the scores of all Section objects.
    
    Args:
        schedule (list): List of Section objects in the schedule
        preferences (dict): User preferences for day, time of day, and weights
        
    Returns:
        float: Combined score of the schedule
    """
    grouped_sections = group_section_times_by_section(schedule) # Group SectionTime objects by Section objects
    
    total_schedule_score = sum(
        score_section(section, section_times, preferences) 
        for section, section_times in grouped_sections.items()
    )
    
    # Debugging output
    logging.debug(f"Scoring Schedule: {schedule}")
    logging.debug(f"Total Schedule Score: {total_schedule_score}")
    
    # Return the total score of the schedule
    return total_schedule_score


def rank_schedules(schedules, preferences, top_n=10):
    """
    Rank all valid schedules based on their scores.
    
    Args:
        schedules (list): List of valid schedules, where each schedule is a list of Section objects
        preferences (dict): User preferences for day, time of day, and weights
        top_n (int): Number of top schedules to return
        
    Returns:
        list: A list of schedules sorted by their scores in descending order
    """
    # Score each schedule
    scored_schedules = [(schedule, score_schedule(schedule, preferences)) for schedule in schedules] # List of (schedule, score) tuples
    top_schedules = heapq.nlargest(top_n, scored_schedules, key=lambda x: x[1]) # Get the top N schedules by score, using a heap
    
    # Debugging output
    for i, (schedule, score) in enumerate(top_schedules):
        logging.debug(f"Top Schedule {i} Score: {score}")
    
    return [schedule for schedule, score in top_schedules]


def format_schedule(schedule):
    """
    Formats a schedule into a more readable string format.
    
    Args:
        schedule (list): List of SectionTime objects representing a schedule.
        
    Returns:
        str: A formatted string representing the schedule.
    """
    day_schedule = defaultdict(list)
    crn_dict = {}
    
    for section_time in schedule:
        day_name = section_time.days.capitalize()
        class_info = f"{section_time.crn.course}: {section_time.begin_time.strftime('%I:%M %p')} - {section_time.end_time.strftime('%I:%M %p')}"
        day_schedule[day_name].append((section_time.begin_time, class_info)) # Store tuples of (begin_time, class_info) for sorting
        
        if section_time.crn.course not in crn_dict:
            crn_dict[section_time.crn.course] = section_time.crn.crn
    
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


def print_ranked_schedules(ranked_schedules, top_n=10):
    """
    Formats the ranked schedules as a list of lists where each list contains strings representing each line of the schedule.
    
    Args:
        ranked_schedules (list): List of ranked schedules to format.
        top_n (int): Number of top schedules to include in the output.
        
    Returns:
        list: A list of formatted schedules as lists of strings.
    """
    formatted_schedules_list = [] # List of formatted schedules
    
    # Format each schedule
    for i, schedule in enumerate(ranked_schedules[:top_n], 1):
        formatted_schedule_data = format_schedule(schedule)
        formatted_schedule = {
            "name": f"Schedule {i}",
            "days": formatted_schedule_data["days"],
            "crns": formatted_schedule_data["crns"]
        }
        formatted_schedules_list.append(formatted_schedule)
    
    return formatted_schedules_list
        
def process_input(courses, breaks, preferences):
    """
    Process the input JSON data to extract the courses, breaks, and preferences.
    
    Args:
        json_input (dict): JSON data containing courses, breaks, and preferences
        
    Returns:
        tuple: A tuple containing the courses, breaks, and preferences
    """
    # data = json_input
    
    # courses = data.get("courses", [])
    # breaks = data.get("breaks", [])
    # preferences = {
    #     "preferred_days": data.get("preferred_days", []),
    #     "preferred_time": data.get("preferred_time", ""),
    #     "day_weight": data.get("day_weight", 1.0),
    #     "time_weight": data.get("time_weight", 0.0),
    # }
    
    valid_schedules = get_valid_schedules(courses, breaks)
    ranked_schedules = rank_schedules(valid_schedules, preferences, top_n=10)
    formatted_schedules = print_ranked_schedules(ranked_schedules, top_n=10)
    
    return formatted_schedules

# Old views.py:
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
    
