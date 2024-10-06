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
                schedules[i] = {crn: times for crn, times in schedule}  # Convert tuple to dict
            elif score > -heap[0][0]:
                _, old_index = heapq.heappushpop(heap, (-score, i))
                schedules[i] = {crn: times for crn, times in schedule}  # Convert tuple to dict
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