from mip import Model, xsum, BINARY, maximize, OptimizationStatus
from collections import defaultdict
from schedule_scoring import ScheduleScorer
from logging_config import loggers
import datetime
import traceback

logger = loggers["schedule_generator"]

class ConstraintBasedScheduler:
    def __init__(
        self, section_dict, section_time_dict, breaks, preferences, max_schedules=10
    ):
        logger.info("Initializing ConstraintBasedScheduler")
        self.section_dict = section_dict
        self.section_time_dict = section_time_dict
        self.breaks = breaks
        self.preferences = preferences
        self.max_schedules = max_schedules
        self.valid_schedules = []
        self.scorer = ScheduleScorer(self.preferences)

        self.courses = list(set(section.course for section in section_dict.values()))
        self.time_slots = self.generate_time_slots()
        self.section_time_slots = self.map_section_times_to_time_slots()

        logger.info(
            f"Initialized ConstraintBasedScheduler with {len(self.courses)} courses and {len(self.time_slots)} time slots"
        )
        logger.debug(f"Courses: {self.courses}")
        logger.debug(f"Number of sections: {len(self.section_dict)}")
        logger.debug(f"Number of breaks: {len(self.breaks)}")

    def generate_time_slots(self):
        logger.info("Generating time slots")
        time_slots = []
        days = ["M", "T", "W", "R", "F", "S", "U"]
        for day in days:
            for hour in range(24):
                for minute in [0, 30]:
                    time_slots.append((day, datetime.time(hour, minute)))
        logger.debug(f"Generated {len(time_slots)} time slots")
        return time_slots

    def map_section_times_to_time_slots(self):
        logger.info("Mapping section times to time slots")
        section_time_slots = defaultdict(list)

        for crn, times in self.section_time_dict.items():
            for time in times:
                if time.begin_time == datetime.time(0, 0) and time.end_time == datetime.time(0, 0):
                    section_time_slots[crn].append(self.time_slots.index(()))
                else:
                    for day in time.days:
                        start = datetime.datetime.combine(datetime.date.today(), time.begin_time)
                        end = datetime.datetime.combine(datetime.date.today(), time.end_time)
                        while start < end:
                            if (day, start.time()) in self.time_slots:
                                section_time_slots[crn].append(self.time_slots.index((day, start.time())))
                            start += datetime.timedelta(minutes=5)

        logger.debug(f"Mapped section times to time slots for {len(section_time_slots)} sections")
        return section_time_slots

    def generate_schedules(self):
        logger.info("Entering generate_schedules method")
        try:
            logger.info("Generating schedules using constraint-based optimization")

            # Creating MIP model
            model = Model()
            logger.info("Created MIP model")

            # Log the solver being used
            logger.info(f"Using solver: {model.solver}")

            # Set verbose logging for solver to get detailed output
            model.verbose = 3

            # Decision variables
            logger.info("Creating decision variables")
            x = {}
            var_count = 0
            for crn in self.section_dict:
                for t in range(len(self.time_slots)):
                    try:
                        x[crn, t] = model.add_var(var_type=BINARY)
                        var_count += 1
                        if var_count % 1000 == 0:
                            logger.info(f"Created {var_count} variables")
                    except Exception as e:
                        logger.error(f"Error creating variable for CRN {crn}, time slot {t}: {str(e)}")
                        raise
            logger.info(f"Created {len(x)} decision variables")

            # Constraints
            logger.info("Adding constraints to the model")
            constraint_count = 0

            # Course constraints
            logger.info("Adding course constraints")
            for course in self.courses:
                try:
                    logger.debug(f"Adding constraint for course {course}")
                    model += (
                        xsum(
                            x[crn, 0]
                            for crn in self.section_dict
                            if self.section_dict[crn].course == course
                        )
                        == 1
                    )
                    constraint_count += 1
                except Exception as e:
                    logger.error(f"Error adding course constraint for {course}: {str(e)}")
                    raise
            logger.info(f"Added {constraint_count} course constraints")

            # Section time constraints
            logger.info("Adding section time constraints")
            for crn, slots in self.section_time_slots.items():
                for t in slots:
                    try:
                        model += x[crn, t] == x[crn, 0]
                        constraint_count += 1
                    except Exception as e:
                        logger.error(f"Error adding section time constraint for CRN {crn}, time slot {t}: {str(e)}")
                        raise
            logger.info(f"Added {constraint_count} section time constraints")

            # Time slot constraints
            logger.info("Adding time slot constraints")
            for t in range(len(self.time_slots)):
                try:
                    model += xsum(x[crn, t] for crn in self.section_dict) <= 1
                    constraint_count += 1
                except Exception as e:
                    logger.error(f"Error adding time slot constraint for time slot {t}: {str(e)}")
                    raise
            logger.info(f"Added {constraint_count} time slot constraints")

            # Break constraints
            logger.info("Adding break constraints")
            for break_time in self.breaks:
                break_slots = [
                    i
                    for i, (_, time) in enumerate(self.time_slots)
                    if break_time["begin_time"] <= time <= break_time["end_time"]
                ]
                for t in break_slots:
                    try:
                        model += xsum(x[crn, t] for crn in self.section_dict) == 0
                        constraint_count += 1
                    except Exception as e:
                        logger.error(f"Error adding break constraint for time slot {t}: {str(e)}")
                        raise
            logger.info(f"Added {constraint_count} total constraints")

            # Objective function
            logger.info("Setting up objective function")
            try:
                model.objective = maximize(
                    xsum(
                        x[crn, t]
                        for crn in self.section_dict
                        for t in range(len(self.time_slots))
                    )
                )
                logger.info("Objective function set up successfully")
            except Exception as e:
                logger.error(f"Error setting up objective function: {str(e)}")
                raise

            # Optimization
            logger.info(f"Starting optimization for {self.max_schedules} schedules")
            solutions = []
            for i in range(self.max_schedules):
                logger.info(f"Optimizing for solution {i+1}/{self.max_schedules}")
                try:
                    status = model.optimize(max_seconds=600)  # Increased time limit
                    logger.info(f"Optimization status: {status}")
                    if status == OptimizationStatus.OPTIMAL:
                        logger.info("Optimal solution found")
                        # Extract solution values and process them
                        for crn, t in x:
                            if x[crn, t].x >= 0.99:  # Extract the selected decision variables
                                logger.info(f"CRN {crn} scheduled at time slot {t}")
                        # Add logic to store and process the solution
                    elif status == OptimizationStatus.FEASIBLE:
                        logger.info("Feasible solution found")
                    elif status == OptimizationStatus.INFEASIBLE:
                        logger.warning(f"Solution {i+1} is infeasible")
                        break
                    else:
                        logger.warning(f"No optimal or feasible solution found for iteration {i+1}")
                        break
                except Exception as e:
                    logger.error(f"Error optimizing for solution {i+1}: {str(e)}")
                    logger.error(traceback.format_exc())
                    break

            logger.info(f"Generated {len(solutions)} valid schedules")
            return sorted(solutions, key=lambda x: x[0], reverse=True)

        except Exception as e:
            logger.error(f"Unexpected error in generate_schedules: {str(e)}")
            logger.error(traceback.format_exc())
            return []

    def convert_solution_to_section_times(self, solution):
        logger.info("Converting solution to section times")
        section_times = []

        for crn, times in solution.items():
            if times:
                section = self.section_dict[crn]
                original_times = self.section_time_dict[crn]

                for original_time in original_times:
                    section_times.append(original_time)

        logger.debug(f"Converted solution to {len(section_times)} section times")
        return section_times