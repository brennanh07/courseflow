import datetime
from schedule_generator import get_valid_schedules
from collections import defaultdict


def group_section_times_by_section(section_times):
    """
    Groups SectionTime objects by their associated Section objects.
    
    Args:
        section_times (list): List of SectionTime objects
        
    Returns:
        dict: Dictionary where keys are Section objects and values are lists of SectionTime objects
    """
    grouped_sections = defaultdict(list) # Initialize an empty dictionary with default value as an empty list
    
    for section_time in section_times:
        section = section_time.crn
        grouped_sections[section].append(section_time)
        
    print(f"Grouped sections: {grouped_sections}")
        
    return grouped_sections


def score_section_time(section_time, preferences):
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
        matching_days = set(section_time.days).intersection(set(preferences['preferred_days']))
        day_score = len(matching_days) / len(section_time.days)
        
        # Time score based on preferred time of day
        time_score = 0
        if preferences['preferred_time'] == 'morning' and section_time.begin_time < datetime.time(12, 0):
            time_score = 1
        elif preferences['preferred_time'] == 'afternoon' and datetime.time(12, 0) <= section_time.begin_time < datetime.time(16, 0):
            time_score = 1
        elif preferences['preferred_time'] == 'evening' and section_time.begin_time >= datetime.time(16, 0):
            time_score = 1
    
    # Apply weight
    weighted_day_score = day_score * preferences['day_weight']
    weighted_time_score = time_score * preferences['time_weight']
    
    # Combined score for this SectionTime
    section_time_score = weighted_day_score + weighted_time_score
    
    # Debugging output
    print(f"Scoring SectionTime: {section_time}")
    print(f"Matching Days: {matching_days}")
    print(f"Day Score: {day_score}, Time Score: {time_score}")
    print(f"Weighted Day Score: {weighted_day_score}, Weighted Time Score: {weighted_time_score}")
    print(f"Total SectionTime Score: {section_time_score}")
    
    return section_time_score


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
    print(f"Scoring Section: {section}")
    print(f"Total Section Score: {total_score}, Average Section Score: {average_score}")

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
    
    total_schedule_score = sum(score_section(section, section_times, preferences) for section, section_times in grouped_sections.items())
    
    # Debugging output
    print(f"Scoring Schedule: {schedule}")
    print(f"Total Schedule Score: {total_schedule_score}")
    
    # Return the total score of the schedule
    return total_schedule_score

def rank_schedules(schedules, preferences):
    """
    Rank all valid schedules based on their scores.
    
    Args:
        schedules (list): List of valid schedules, where each schedule is a list of Section objects
        preferences (dict): User preferences for day, time of day, and weights
        
    Returns:
        list: A list of schedules sorted by their scores in descending order
    """
    # Score each schedule
    scored_schedules = [(schedule, score_schedule(schedule, preferences)) for schedule in schedules]
    scored_schedules.sort(key=lambda x: x[1], reverse=True)
    
    # Debugging output
    for i, (schedule, score) in enumerate(scored_schedules):
        print(f"Schedule {i} Score: {score}")
    
    return [schedule for schedule, score in scored_schedules]


def format_schedule(schedule):
    """
    Formats a schedule into a more readable string format.
    
    Args:
        schedule (list): List of SectionTime objects representing a schedule.
        
    Returns:
        str: A formatted string representing the schedule.
    """
    formatted_schedule = []
    
    for section_time in schedule:
        course_info = f"{section_time.crn.course}: {section_time.days} {section_time.begin_time.strftime('%I:%M %p')} - {section_time.end_time.strftime('%I:%M %p')}"
        formatted_schedule.append(course_info)
    
    return "\n".join(formatted_schedule)

def print_ranked_schedules(ranked_schedules, top_n=5):
    """
    Prints the ranked schedules in a readable format.
    
    Args:
        ranked_schedules (list): List of ranked schedules to print.
    """
    for i, schedule in enumerate(ranked_schedules, 1):
        print(f"Schedule {i}:")
        print(format_schedule(schedule))
        print("\n" + "="*40 + "\n")
        
    # Print the top N schedules again
    print(f"\nTop {top_n} Schedules:\n" + "="*40)
    for i, schedule in enumerate(ranked_schedules[:top_n], 1):
        print(f"Top {i} Schedule:")
        print(format_schedule(schedule))
        print("\n" + "="*40 + "\n")


# Example usage
preferences = {
    'preferred_days': ['M', 'T', 'W', 'R'],
    'preferred_time': 'morning',
    'day_weight': 1.0,
    'time_weight': 0.5
}

courses = ["CS-1114", "MATH-1226", "CS-1014", "ENGE-1216", "ACIS-1504"]

breaks = [
    {'begin_time': datetime.time(8, 0), 'end_time': datetime.time(9, 0)},
    # {'begin_time': '18:00:00', 'end_time': '19:00:00'}
]

valid_schedules = get_valid_schedules(courses, breaks)

ranked_schedules = rank_schedules(valid_schedules, preferences)

print_ranked_schedules(ranked_schedules)
