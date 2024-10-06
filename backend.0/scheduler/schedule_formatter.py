from collections import defaultdict
from logging_config import loggers

logger = loggers['schedule_formatter']

class ScheduleFormatter:
    def __init__(self, date_format="%I:%M %p"):
        """
        Initialize the ScheduleFormatter object with optional formatting settings.
        
        Args:
            date_format (str): The format string to use for displaying dates and times
        """
        self.date_format = date_format
        
    # def format_schedule(self, schedule):
    #     """
    #     Formats a schedule into a more readable string format.
        
    #     Args:
    #         schedule (list): A list of SectionTime objects representing a schedule
            
    #     Returns:
    #         dict: A formatted dictionary representation of the schedule including days and CRNs
    #     """
    #     day_schedule = defaultdict(list)
    #     crn_dict = {}
        
    #     for section_time in schedule[1]:
    #         logger.info(f"Processing section_time: {section_time}")
    #         logger.info(f"section_time.days type: {type(section_time.days)}")
    #         logger.info(f"section_time.days value: {section_time.days}")
            
    #         if isinstance(section_time.days, float):
    #             logger.warning(f"Unexpected float value for days: {section_time.days}")
    #             day_name = str(int(section_time.days))  # Convert float to string
    #         elif isinstance(section_time.days, str):
    #             day_name = section_time.days.capitalize()
    #         else:
    #             logger.error(f"Unexpected type for days: {type(section_time.days)}")
    #             day_name = "Unknown"
            
    #         try:
    #             class_info = f"{section_time.crn.course}: {section_time.begin_time.strftime(self.date_format)} - {section_time.end_time.strftime(self.date_format)}"
    #         except AttributeError as e:
    #             logger.error(f"Error formatting class info: {e}")
    #             class_info = "Error: Unable to format class info"
            
    #         day_schedule[day_name].append((section_time.begin_time, class_info))
            
    #         if hasattr(section_time.crn, 'course'):
    #             if section_time.crn.course not in crn_dict:
    #                 crn_dict[section_time.crn.course] = section_time.crn.crn
    #         else:
    #             logger.error(f"section_time.crn does not have 'course' attribute: {section_time.crn}")

    #     # Sort classes by start time    
    #     ordered_schedule = {} 
    #     for day in ["M", "T", "W", "R", "F", "S", "U"]:
    #         if day in day_schedule:
    #             ordered_schedule[day] = [class_info for _, class_info in sorted(day_schedule[day])]
    #         elif "Online" in day_schedule or "Arr" in day_schedule:
    #             ordered_schedule["Online/ARR"] = [class_info for _, class_info in sorted(day_schedule.get("Online", []) + day_schedule.get("Arr", []))]
    #         else:
    #             ordered_schedule[day] = []
            
    #     return {
    #         "days": ordered_schedule,
    #         "crns": crn_dict
    #     }
        
    # def print_ranked_schedules(self, top_schedules, top_n=10):
    #     """
    #     Formats the top N schedules as a list of lists where each list contains strings representing each line of the schedule.

    #     Args:
    #         top_schedules (list): List of top N schedules to format.
    #         top_n (int): Number of top schedules to include in the output.

    #     Returns:
    #         list: A list of formatted schedules as dictionaries with names, days, and CRNs.
    #     """
    #     formatted_schedules_list = []
        
    #     for i, schedule in enumerate(top_schedules[:top_n], 1):
    #         try:
    #             formatted_schedule_data = self.format_schedule(schedule)
    #             formatted_schedule = {
    #                 "name": f"Schedule {i}",
    #                 "days": formatted_schedule_data["days"],
    #                 "crns": formatted_schedule_data["crns"]
    #             }
    #             formatted_schedules_list.append(formatted_schedule)
    #         except Exception as e:
    #             logger.error(f"Error formatting schedule {i}: {e}")
        
    #     return formatted_schedules_list
        
        
    def format_schedule(self, schedule):
        day_schedule = defaultdict(list)
        crn_dict = {}
        
        for crn, section_times in schedule.items():
            for section_time in section_times:
                day_name = section_time.days
                
                if isinstance(day_name, float):
                    day_name = str(int(day_name))
                elif isinstance(day_name, str):
                    day_name = day_name.capitalize()
                else:
                    day_name = "Unknown"
                
                try:
                    class_info = f"{section_time.crn.course}: {section_time.begin_time.strftime(self.date_format)} - {section_time.end_time.strftime(self.date_format)}"
                except AttributeError as e:
                    logger.error(f"Error formatting class info: {e}")
                    class_info = "Error: Unable to format class info"
                
                day_schedule[day_name].append((section_time.begin_time, class_info))
                
                if hasattr(section_time.crn, 'course'):
                    if section_time.crn.course not in crn_dict:
                        crn_dict[section_time.crn.course] = section_time.crn.crn
                else:
                    logger.error(f"section_time.crn does not have 'course' attribute: {section_time.crn}")

        ordered_schedule = {} 
        for day in ["M", "T", "W", "R", "F", "S", "U"]:
            if day in day_schedule:
                ordered_schedule[day] = [class_info for _, class_info in sorted(day_schedule[day])]
            elif "Online" in day_schedule or "Arr" in day_schedule:
                ordered_schedule["Online/ARR"] = [class_info for _, class_info in sorted(day_schedule.get("Online", []) + day_schedule.get("Arr", []))]
            else:
                ordered_schedule[day] = []
            
        return {
            "days": ordered_schedule,
            "crns": crn_dict
        }
        
    def print_ranked_schedules(self, top_schedules, top_n=10):
        formatted_schedules_list = []
        
        for i, (score, schedule) in enumerate(top_schedules[:top_n], 1):
            try:
                formatted_schedule_data = self.format_schedule(schedule)
                formatted_schedule = {
                    "name": f"Schedule {i}",
                    "score": score,
                    "days": formatted_schedule_data["days"],
                    "crns": formatted_schedule_data["crns"]
                }
                formatted_schedules_list.append(formatted_schedule)
            except Exception as e:
                logger.error(f"Error formatting schedule {i}: {e}")
        
        return formatted_schedules_list