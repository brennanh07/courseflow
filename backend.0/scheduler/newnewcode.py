# schedule_scoring.py
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
        self.preferred_days = tuple(preferences['preferred_days'])
        
    @lru_cache(maxsize=1024)
    def score_schedule(self, schedule):
        return sum(self.score_section_time(section_time) for section_time in schedule)
    
    @lru_cache(maxsize=1024)
    def score_section_time(self, section_time):
        if section_time.begin_time == datetime.time(0, 0):
            day_score = 1
            time_score = 1
        else:
            matching_days = len(set(section_time.days) & set(self.preferred_days))
            day_score = matching_days / len(section_time.days)
            time_score = self.score_time(section_time.begin_time)
        
        return (day_score * self.preferences['day_weight']) + (time_score * self.preferences['time_weight'])
    
    @lru_cache(maxsize=128)
    def score_time(self, begin_time):
        preferred_time = self.preferences['preferred_time']
        
        time_ranges = {
            'morning': (datetime.time(8, 0), datetime.time(12, 0)),
            'afternoon': (datetime.time(12, 0), datetime.time(16, 0)),
            'evening': (datetime.time(16, 0), datetime.time(20, 0)),
        }
        
        if preferred_time not in time_ranges:
            return 0
        
        preferred_start, preferred_end = time_ranges[preferred_time]
        
        if begin_time < preferred_start:
            score = max(0, 1 - (preferred_start.hour - begin_time.hour + (preferred_start.minute - begin_time.minute) / 60) / 4)
        elif preferred_start <= begin_time <= preferred_end:
            score = 1
        else:
            score = max(0, 1 - (begin_time.hour - preferred_end.hour + (begin_time.minute - preferred_end.minute) / 60) / 4)
        
        return score

# schedule_generator.py
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

class ScheduleGenerator:
    def __init__(self, section_dict, section_time_dict, breaks, preferences, max_schedules=10):
        self.section_dict = section_dict
        self.section_time_dict = {crn: tuple(times) for crn, times in section_time_dict.items()}
        self.breaks = tuple(breaks)
        self.preferences = preferences
        self.max_schedules = max_schedules
        self.scorer = ScheduleScorer(self.preferences)
        
        self.course_sections = defaultdict(list)
        for crn, section in section_dict.items():
            self.course_sections[section.course].append((crn, self.section_time_dict[crn]))

    def generate_schedules(self):
        courses = list(self.course_sections.keys())
        all_combinations = product(*self.course_sections.values())
        
        heap = []
        schedules = {}
        
        for i, combination in enumerate(all_combinations):
            schedule = tuple((crn, times) for crn, times in combination)
            flat_schedule = tuple(time for _, times in schedule for time in times)
            
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

    @lru_cache(maxsize=1024)
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

    @staticmethod
    @lru_cache(maxsize=1024)
    def check_conflict(time1, time2):
        if set(time1.days) & set(time2.days):
            return (time1.begin_time < time2.end_time and time2.begin_time < time1.end_time)
        return False
    
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
        day_schedule = defaultdict(list)
        crn_dict = {}
        
        for crn, section_times in schedule.items():
            for section_time in section_times:
                day_name = section_time.days
                
                if isinstance(day_name, float):
                    day_name = str(int(day_name))
                elif isinstance(day_name, str):
                    day_name = day_name.capitalize()
                else:
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
        formatted_schedules_list = []
        
        for i, (score, schedule) in enumerate(top_schedules[:top_n], 1):
            try:
                formatted_schedule_data = self.format_schedule(schedule)
                formatted_schedule = {
                    "name": f"Schedule {i}",
                    "score": score,
                    "days": formatted_schedule_data["days"],
                    "crns": formatted_schedule_data["crns"]
                }
                formatted_schedules_list.append(formatted_schedule)
            except Exception as e:
                logger.error(f"Error formatting schedule {i}: {e}")
        
        return formatted_schedules_list