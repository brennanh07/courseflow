from fetch_sections import SectionFetcher
from schedule_generator import ScheduleGenerator
from schedule_formatter import ScheduleFormatter

def process_schedule(courses, breaks, preferences, max_schedules=10):
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
    section_fetcher = SectionFetcher()
    section_dict, section_time_dict = section_fetcher.fetch_sections(courses)
    
    # Generate and score valid schedules dynamically
    schedule_generator = ScheduleGenerator(section_dict, section_time_dict, breaks, preferences, max_schedules)
    top_schedules = schedule_generator.generate_schedules()
    
    # Format the top N schedules for display
    formatter = ScheduleFormatter(date_format="%I:%M %p")
    
    return formatter.print_ranked_schedules(top_schedules, top_n=max_schedules)