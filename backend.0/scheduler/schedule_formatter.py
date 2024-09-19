from collections import defaultdict

class ScheduleFormatter:
    def __init__(self, date_format="%I:%M %p"):
        """
        Initialize the ScheduleFormatter object with optional formatting settings.
        
        Args:
            date_format (str): The format string to use for displaying dates and times
        """
        self.date_format = date_format
        
    def format_schedule(self, schedule):
        """
        Formats a schedule into a more readable string format.
        
        Args:
            schedule (list): A list of SectionTime objects representing a schedule
            
        Returns:
            dict: A formatted dictionary representation of the schedule including days and CRNs
        """
        day_schedule = defaultdict(list)
        crn_dict = {}
        
        for section_time in schedule:
            day_name = section_time.day.capitalize()
            class_info = f"{section_time.crn.course}: {section_time.begin.strftime(self.date_format)} - {section_time.end.strftime(self.date_format)}"
            day_schedule[day_name].append((section_time.begin_time, class_info))
            
            if section_time.crn.course not in crn_dict:
                crn_dict[section_time.crn.course] = section_time.crn.crn
                
        # Sort classes by start time    
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
        """
        Formats the top N schedules as a list of lists where each list contains strings representing each line of the schedule.

        Args:
            top_schedules (list): List of top N schedules to format.
            top_n (int): Number of top schedules to include in the output.

        Returns:
            list: A list of formatted schedules as dictionaries with names, days, and CRNs.
        """
        formatted_schedules_list = []
        
        # Format each schedule
        for i, schedule in enumerate(top_schedules[:top_n], 1):
            formatted_schedule_data = self.format_schedule(schedule)
            formatted_schedule = {
                "name": f"Schedule {i}",
                "days": formatted_schedule_data["days"],
                "crns": formatted_schedule_data["crns"]
            }
            formatted_schedules_list.append(formatted_schedule)
        
        return formatted_schedules_list
        