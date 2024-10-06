import django
import os
from logging_config import loggers

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'class_scheduler.settings')
django.setup()

from scheduler.models import Section, SectionTime

logger = loggers['fetch_sections']

class SectionFetcher:
    def __init__(self, courses):
        self.courses = courses
        self.section_dict = {}
        self.section_time_dict = {}
        
    def fetch_sections(self):
        """
        Fetch all sections and their corresponding times for the given courses using batch fetching.
        
        Args:
            courses (list): A list of courses to fetch sections for.
            
        Returns:
            section_dict (dict): Dictionary mapping CRNs to Section objects.
            section_time_dict (dict): Dictionary mapping CRNs to lists of SectionTime objects.
        """
        logger.info(f"Fetching sections for courses: {self.courses}")
        sections = Section.objects.filter(course__in=self.courses).prefetch_related('sectiontime_set')
        logger.debug(f"Found {len(sections)} sections")
        
        self.section_dict = {section.crn: section for section in sections}
        self.section_time_dict = {section.crn: list(section.sectiontime_set.all()) for section in sections}
        
        logger.debug(f"Fetched sections: {self.section_dict}")
        logger.debug(f"Fetched section times: {self.section_time_dict}")
        
        if not self.section_dict:
            logger.warning(f"No sections found for courses: {self.courses}")
        
        return self.section_dict, self.section_time_dict
    
    
