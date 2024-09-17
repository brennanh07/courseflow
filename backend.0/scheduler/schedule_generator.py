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

# Example usage:
# courses = ["CS-1114", "MATH-1226", "CS-1014"]
# breaks = [{'begin_time': datetime.time(8, 0), 'end_time': datetime.time(9, 0)}]
# valid_schedules = get_valid_schedules(courses, breaks)
# print(valid_schedules)
