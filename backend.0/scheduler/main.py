from fetch_sections import SectionFetcher
from schedule_formatter import ScheduleFormatter
from logging_config import loggers
from schedule_generator import ScheduleGenerator

logger = loggers['main']

def process_schedules(courses, breaks, preferences, max_schedules=10):
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
    logger.info(f"Processing schedules for courses: {courses}")
    logger.debug(f"Preferences: {preferences}")
    logger.debug(f"Breaks: {breaks}")
    
    # Fetch sections from the database
    section_fetcher = SectionFetcher(courses)
    section_dict, section_time_dict = section_fetcher.fetch_sections()
    
    if not section_dict:
        logger.warning("No sections found. Aborting schedule generation.")
        return []
    
    # Generate and score valid schedules dynamically
    logger.info("Generating schedules")
    schedule_generator = ScheduleGenerator(section_dict, section_time_dict, breaks, preferences, max_schedules)
    top_schedules = schedule_generator.generate_schedules()
    
    logger.info(f"Generated {len(top_schedules)} schedules")
    
    # Format the top N schedules for display
    formatter = ScheduleFormatter(date_format="%I:%M %p")
    formatted_schedules = formatter.print_ranked_schedules(top_schedules, top_n=max_schedules)
    
    logger.info("Schedule processing complete")
    return formatted_schedules
