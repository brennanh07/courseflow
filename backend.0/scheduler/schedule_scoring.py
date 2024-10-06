import datetime
from collections import defaultdict
import logging
from itertools import groupby
from operator import attrgetter
from functools import lru_cache

# Setup logging
logging.basicConfig(level=logging.DEBUG, filename='scheduler.log', filemode='w')

# class ScheduleScorer:
#     def __init__(self, preferences):
#         self.preferences = preferences
#         self.preferred_days = set(preferences['preferred_days'])
#         self.preferred_time = preferences['preferred_time']
#         self.day_weight = preferences['day_weight']
#         self.time_weight = preferences['time_weight']
        
#     def score_schedule(self, schedule):
#         """
#         Score an entire schedule based on the user preferences.
        
#         Args:
#             schedule (list): List of SectionTime objects in the schedule
            
#         Returns:
#             float: Combined score of the schedule
#         """
#         grouped_sections = self.group_section_times_by_section(schedule) # Group SectionTime objects by Section objects
        
#         total_score = sum(self.score_section(section, section_times) for section, section_times in grouped_sections.items())
        
#         logging.debug(f"Schedule: {schedule}, Score: {total_score}")
        
#         return total_score
    
#     def group_section_times_by_section(self, section_times):
        
#         grouped_sections = defaultdict(list)
#         for section_time in section_times:
#             grouped_sections[section_time.crn].append(section_time)
#         return grouped_sections
    
#     def score_section(self, section, section_times):
#         """
#         """
#         total_score = sum(self.score_section_time(section_time) for section_time in section_times)
        
#         return total_score / len(section_times) if section_times else 0 # Average score across all SectionTime objects
    
#     def score_section_time(self, section_time):
#         """
#         """
#         # Handle edge case of "00:00:00" (online or arranged courses)
#         if section_time.begin_time == datetime.time(0, 0):
#             day_score = 1
#             time_score = 1
#             matching_days = "N/A"
            
#         else:
#             matching_days = set(section_time.days).intersection(self.preferred_days)
#             day_score = len(matching_days) / len(section_time.days)
#             time_score = self.score_time(section_time.begin_time)
        
#         return (day_score * self.day_weight) + (time_score * self.time_weight)
    
#     @lru_cache(maxsize=1440)
#     def score_time(self, begin_time):
#         """
#         """
#         time_ranges = {
#             'morning': (datetime.time(8, 0), datetime.time(12, 0)),  # 8:00 AM to 12:00 PM
#             'afternoon': (datetime.time(12, 0), datetime.time(16, 0)),  # 12:00 PM to 4:00 PM
#             'evening': (datetime.time(16, 0), datetime.time(20, 0)),  # 4:00 PM to 8:00 PM
#         }
        
#         if self.preferred_time not in time_ranges:
#             return None
        
#         preferred_start, preferred_end = time_ranges[self.preferred_time]
        
#         # Convert times to datetime on an arbitrary date for comparison
#         arbitrary_date = datetime.date(1, 1, 1)
#         begin_dt = datetime.datetime.combine(arbitrary_date, begin_time)
#         preferred_start_dt = datetime.datetime.combine(arbitrary_date, preferred_start)
#         preferred_end_dt = datetime.datetime.combine(arbitrary_date, preferred_end)
        
        
#         # Calculate the score based on the proximity to the preferred time
#         if begin_dt < preferred_start_dt:
#         # Calculate how far the class start time is before the preferred start time
#             score = max(0, 1 - (preferred_start_dt - begin_dt).seconds / 3600)
        
#         elif preferred_start_dt <= begin_dt <= preferred_end_dt:
#         # Perfect match if the class start time is within the preferred range
#             score = 1
        
#         else:
#         # Calculate how far the class start time is after the preferred end time
#             score = max(0, 1 - (begin_dt - preferred_end_dt).seconds / 3600)
        
#         return score
    
    # @lru_cache(maxsize=128)
    # def score_time(self, begin_time, end_time):
    #     preferred_time = self.preferences['preferred_time']
        
    #     # Convert times to datetime on an arbitrary date for comparison
    #     arbitrary_date = datetime.date(1, 1, 1)
    #     begin_dt = datetime.datetime.combine(arbitrary_date, begin_time)
    #     end_dt = datetime.datetime.combine(arbitrary_date, end_time)
        
    #     begin_score = self.continuous_time_score(begin_dt, preferred_time)
    #     end_score = self.continuous_time_score(end_dt, preferred_time)
        
    #     return (begin_score + end_score) / 2
    
    # def continuous_time_score(self, time, preferred_time):
    #     hours = time.hour + time.minute / 60
        
    #     # Define the center of each time range
    #     time_centers = {
    #         'morning': 8,  # 10:00 AM
    #         'afternoon': 14,  # 2:00 PM
    #         'evening': 18,  # 6:00 PM
    #     }
        
    #     center = time_centers.get(preferred_time, 12)  # Default to noon if invalid preference
        
    #     # Calculate score based on distance from preferred time center
    #     distance = abs(hours - center)
    #     max_distance = 12  # Maximum possible distance in a 24-hour clock
        
    #     return max(0, 1 - distance / max_distance)
    

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
