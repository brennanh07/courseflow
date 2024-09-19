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
        
        return total_score
    
    def group_section_times_by_section(self, section_times):
        
        grouped_sections = defaultdict(list)
        for section_time in section_times:
            grouped_sections[section_time.crn].append
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
            day_score = len(set(section_time.days).intersection(preferred_days)) / len(section_time.days)
            time_score = self.score_time(section_time.begin_time, preferred_time)
        
        return (day_score * self.preferences['day_weight']) + (time_score * self.preferences['time_weight'])
    
    def score_time(self, begin_time, preferred_time):
        """
        """
        time_ranges = {
            'morning': (datetime.time(8, 0), datetime.time(12, 0)),  # 8:00 AM to 12:00 PM
            'afternoon': (datetime.time(12, 0), datetime.time(16, 0)),  # 12:00 PM to 4:00 PM
            'evening': (datetime.time(16, 0), datetime.time(20, 0)),  # 4:00 PM to 8:00 PM
        }
        
        if preferred_time not in time_ranges:
            return 0.0
        
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
