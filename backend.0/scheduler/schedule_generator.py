import django
import os
import heapq
from schedule_scoring import ScheduleScorer
from conflict_checker import is_valid_combination

# Setup Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'class_scheduler.settings')
django.setup()

from scheduler.models import Section, SectionTime

class ScheduleGenerator:
    def __init__(self, section_dict, section_time_dict, breaks, preferences, max_schedules=10):
        self.section_dict = section_dict
        self.section_time_dict = section_time_dict
        self.breaks = breaks
        self.preferences = preferences
        self.max_schedules = max_schedules
        self.valid_schedules = []
        self.heap = []
        
    def generate_schedules(self):
        self.generate_valid_schedules()
        
        # Sort the heap by score in descending order and return the schedules
        return [schedule for score, schedule in sorted(self.heap, reverse=True)]
    
    def generate_valid_schedules(self, current_combination=[], selected_courses=set(), cached_section_times=None):
        """
        Recursively generate all valid schedules with early pruning.
        
        Args:
            section_dict (dict): Dictionary mapping CRNs to Section objects
            section_time_dict (dict): Dictionary mapping CRNs to lists of SectionTime objects
            current_combination (list): The current combination of SectionTime objects being considered
            valid_schedules (list): List to store valid schedules
            selected_courses (set): Set to track courses that have already been added to the current combination
        """
        # Initialize cache of SectionTime objects if it's the first call
        if cached_section_times is None:
            cached_section_times = {} # Cache of SectionTime objects for each section
        
        # Base case: If all courses have been processed, score the current schedule
        if len(selected_courses) == len(set(section.course for section in self.section_dict.values())):
            
            scorer = ScheduleScorer(self.preferences) # Initialize the schedule scorer
            score = scorer.score_schedule(current_combination) # Score the current schedule
            
            # Use a heap to keep track of the top N schedules
            if len(self.heap) < self.max_schedules or score > self.heap[0][0]:
                if len(self.heap) == self.max_schedules: 
                    heapq.heappop(self.heap) # Remove the lowest scoring schedule
                heapq.heappush(self.heap, (score, current_combination)) # Add the new schedule to the heap
            
            return
        
        remaining_courses = [section.course for crn, section in self.section_dict.items() if section.course not in selected_courses]
        
        if not remaining_courses:
            return
        
        next_course = remaining_courses[0]
        
        # Iterate over all sections of the next course
        for crn, section in self.section_dict.items():
            if section.course == next_course:
                
                # Fetch and cache SectionTime objects if they are not already cached
                if crn not in cached_section_times:
                    cached_section_times[crn] = self.section_time_dict[crn]
                
                # Get all SectionTime objects for the section
                section_times = cached_section_times[crn]
                
                # Early prune: Check if adding this section's times causes any conflicts
                if not is_valid_combination(current_combination, section_times, self.breaks):
                    continue  # Prune this combination early if it leads to conflicts
                
                new_combination = current_combination + section_times
                
                # Recurse with the new combination and cace of SectionTime objects
                self.generate_valid_schedules(
                    new_combination,
                    selected_courses | {section.course},
                    cached_section_times,
                )
