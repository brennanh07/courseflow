from collections import defaultdict

# from logging_config import loggers

# logger = loggers['schedule_formatter']


class ScheduleFormatter:
    """
    A class to format and present course schedules in a user-friendly manner.

    This class takes raw schedule data and converts it into a structured format
    suitable for display or further processing.
    """

    def __init__(self, date_format="%I:%M %p"):
        """
        Initialize the ScheduleFormatter with a specific date format.

        Args:
            date_format (str): The format string to use for displaying times. Defaults to "%I:%M %p".
        """
        self.date_format = date_format

    def format_schedule(self, schedule):
        """
        Format a single schedule into a structured dictionary.

        This method organizes the schedule by days and includes CRN information.

        Args:
            schedule (dict): A dictionary representing a course schedule.

        Returns:
            dict: A formatted schedule with 'days' and 'crns' keys.
        """
        day_schedule = defaultdict(list)
        crn_dict = {}
        location_dict = {}
        professor_dict = {}
        gpa_dict = {}

        for crn, section_times in schedule.items():
            for section_time in section_times:
                day_name = section_time.days

                # Handle different day name formats
                if isinstance(day_name, float):
                    day_name = str(int(day_name))
                elif isinstance(day_name, str):
                    day_name = day_name.capitalize()
                else:
                    day_name = "Unknown"

                try:
                    class_info = f"{section_time.crn.course}: {section_time.begin_time.strftime(self.date_format)} - {section_time.end_time.strftime(self.date_format)}"
                except AttributeError as e:
                    # logger.error(f"Error formatting class info: {e}")
                    class_info = "Error: Unable to format class info"

                day_schedule[day_name].append((section_time.begin_time, class_info))

                # Store CRN information
                if hasattr(section_time.crn, "course"):
                    if section_time.crn.course not in crn_dict:
                        crn_dict[section_time.crn.course] = section_time.crn.crn

                    location_dict[section_time.crn.course] = section_time.crn.location
                    professor_dict[section_time.crn.course] = section_time.crn.professor
                    gpa_dict[section_time.crn.course] = section_time.crn.avg_gpa

                else:
                    pass
                    # logger.error(f"section_time.crn does not have 'course' attribute: {section_time.crn}")

        # Create an ordered schedule
        ordered_schedule = {}
        for day in ["M", "T", "W", "R", "F", "S", "U"]:
            if day in day_schedule:
                ordered_schedule[day] = [
                    class_info for _, class_info in sorted(day_schedule[day])
                ]
            elif "Online" in day_schedule or "Arr" in day_schedule:
                ordered_schedule["Online/ARR"] = [
                    class_info
                    for _, class_info in sorted(
                        day_schedule.get("Online", []) + day_schedule.get("Arr", [])
                    )
                ]
            else:
                ordered_schedule[day] = []

        return {
            "days": ordered_schedule,
            "crns": crn_dict,
            "locations": location_dict,
            "professors": professor_dict,
            "gpas": gpa_dict,
        }

    def print_ranked_schedules(self, top_schedules, top_n=10):
        """
        Format and rank the top schedules.

        This method takes a list of scored schedules, formats them, and returns
        a list of the top N formatted schedules.

        Args:
            top_schedules (list): A list of tuples containing (score, schedule) pairs.
            top_n (int): The number of top schedules to return. Defaults to 10.

        Returns:
            list: A list of dictionaries, each representing a formatted schedule with rank, score, and details.
        """
        formatted_schedules_list = []

        for i, (score, schedule_equivalents_list) in enumerate(
            top_schedules[:top_n], 1
        ):
            try:
                # Initialize an empty list to hold all formatted schedules in the equivalence list
                formatted_schedule_variants = []

                for schedule in schedule_equivalents_list:
                    formatted_schedule_data = self.format_schedule(schedule)

                    non_null_gpas = [
                        gpa
                        for gpa in formatted_schedule_data["gpas"].values()
                        if gpa is not None
                    ]

                    formatted_schedule_variants.append(
                        {
                            "days": formatted_schedule_data["days"],
                            "crns": formatted_schedule_data["crns"],
                            "locations": formatted_schedule_data["locations"],
                            "professors": formatted_schedule_data["professors"],
                            "gpas": formatted_schedule_data["gpas"],
                            "schedule_total_avg_gpa": (
                                round((sum(non_null_gpas) / len(non_null_gpas)), 2)
                                if non_null_gpas
                                else None
                            ),
                        }
                    )

                formatted_schedules_list.append(
                    {
                        "name": f"Schedule {i}",
                        "score": score,
                        "variants": formatted_schedule_variants,  # Include all formatted schedule variants
                    }
                )

            except Exception as e:
                print(f"Error formatting schedule {i}: {e}")
                # logger.error(f"Error formatting schedule {i}: {e}")

        return formatted_schedules_list
