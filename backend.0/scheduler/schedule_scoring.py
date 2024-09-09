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


# Example usage
# preferences = {
#     'preferred_days': ['M', 'T', 'W', 'R'],
#     'preferred_time': 'morning',
#     'day_weight': 1.0,
#     'time_weight': 0.0
# }

# courses = ["CS-1114", "MATH-1226", "CS-1014", "ENGE-1216", "ACIS-1504"]

# breaks = [
#     {'begin_time': datetime.time(8, 0), 'end_time': datetime.time(9, 0)},
#     {'begin_time': '18:00:00', 'end_time': '19:00:00'}
# ]

# valid_schedules = get_valid_schedules(courses, breaks)

# ranked_schedules = rank_schedules(valid_schedules, preferences)

# print_ranked_schedules(ranked_schedules)
