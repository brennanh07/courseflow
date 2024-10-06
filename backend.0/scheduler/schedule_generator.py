from collections import defaultdict
import heapq
from typing import List, Dict, Tuple, Any
from schedule_scoring import ScheduleScorer


class ScheduleHeapElement:
    def __init__(self, score: float, schedule: Dict[str, List[Any]]):
        self.score = score
        self.schedule = schedule

    def __lt__(self, other):
        return self.score > other.score  # Note: We use > for a max-heap behavior

    def __eq__(self, other):
        return self.score == other.score


class ScheduleGenerator:
    def __init__(
        self, section_dict, section_time_dict, breaks, preferences, max_schedules=10
    ):
        self.section_dict = section_dict
        self.section_time_dict = section_time_dict
        self.breaks = breaks
        self.preferences = preferences
        self.max_schedules = max_schedules
        self.scorer = ScheduleScorer(self.preferences)

        # Group section times by course
        self.course_sections = defaultdict(list)
        for crn, section in section_dict.items():
            self.course_sections[section.course].append((crn, section_time_dict[crn]))

        # Sort courses by the number of sections (ascending)
        self.sorted_courses = sorted(
            self.course_sections.keys(), key=lambda c: len(self.course_sections[c])
        )

    def generate_schedules(self):
        heap = []
        self._dfs(0, {}, [], heap)
        return [
            (element.score, element.schedule) for element in sorted(heap)
        ]

    def _dfs(
        self,
        course_index: int,
        current_schedule: Dict[str, List[Any]],
        flat_schedule: List[Any],
        heap: List[ScheduleHeapElement],
    ):
        if course_index == len(self.sorted_courses):
            score = self.scorer.score_schedule(
                tuple(flat_schedule)
            )  # Convert list to tuple
            element = ScheduleHeapElement(score, current_schedule.copy())
            if len(heap) < self.max_schedules:
                heapq.heappush(heap, element)
            elif score > heap[0].score:
                heapq.heapreplace(heap, element)
            return

        course = self.sorted_courses[course_index]
        for crn, times in self.course_sections[course]:
            if self._is_valid_addition(flat_schedule, times):
                current_schedule[crn] = times
                self._dfs(
                    course_index + 1, current_schedule, flat_schedule + times, heap
                )
                current_schedule.pop(crn)

    def _is_valid_addition(
        self, current_schedule: List[Any], new_times: List[Any]
    ) -> bool:
        for new_time in new_times:
            # Check for conflicts with existing times
            for existing_time in current_schedule:
                if self._check_conflict(new_time, existing_time):
                    return False

            # Check for conflicts with breaks
            for break_time in self.breaks:
                if (
                    new_time.begin_time >= break_time["begin_time"]
                    and new_time.begin_time <= break_time["end_time"]
                ):
                    return False
        return True

    @staticmethod
    def _check_conflict(time1: Any, time2: Any) -> bool:
        return (
            set(time1.days) & set(time2.days)
            and time1.end_time > time2.begin_time
            and time1.begin_time < time2.end_time
        )
