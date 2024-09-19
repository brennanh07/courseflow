import logging
import django
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'class_scheduler.settings')
django.setup()

from scheduler.models import Section, SectionTime

logging.basicConfig(level=logging.DEBUG, filename='fetch_sections.log', filemode='w')

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
        sections = Section.objects.filter(course__in=self.courses).prefetch_related('sectiontime_set')
        self.section_dict = {section.crn: section for section in sections}
        self.section_time_dict = {section.crn: list(section.sectiontime_set.all()) for section in sections}
        
        logging.debug(f"Fetched sections: {self.section_dict}")
        logging.debug(f"Fetched section times: {self.section_time_dict}")
        
        return self.section_dict, self.section_time_dict
    
    
