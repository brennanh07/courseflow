import unittest
from unittest.mock import MagicMock, patch
from schedule_generator import ScheduleGenerator

class TestScheduleGenerator(unittest.TestCase):
    @patch('schedule_generator.ScheduleScorer')
    @patch('schedule_generator.is_valid_combination')
    def test_generate_schedules(self, mock_is_valid_combination, MockScheduleScorer):
        # Mock the behavior of is_valid_combination
        mock_is_valid_combination.return_value = True
        
        # Mock the behavior of ScheduleScorer
        mock_scorer = MockScheduleScorer.return_value
        mock_scorer.score_schedule.return_value = 10
        
        # Define test inputs
        section_dict = {
            'crn1': MagicMock(course='course1'),
            'crn2': MagicMock(course='course2')
        }
        section_time_dict = {
            'crn1': [MagicMock(begin_time='09:00', days='MWF')],
            'crn2': [MagicMock(begin_time='10:00', days='TR')]
        }
        breaks = []
        preferences = {
            'preferred_days': ['M', 'T', 'W', 'R', 'F'],
            'preferred_time': 'morning',
            'day_weight': 0.5,
            'time_weight': 0.5
        }
        max_schedules = 2
        
        # Create an instance of ScheduleGenerator
        generator = ScheduleGenerator(section_dict, section_time_dict, breaks, preferences, max_schedules)
        
        # Call the method under test
        top_schedules = generator.generate_schedules()
        
        # Verify the result
        self.assertEqual(len(top_schedules), 1)
        self.assertEqual(top_schedules[0], [MagicMock(begin_time='09:00', days='MWF'), MagicMock(begin_time='10:00', days='TR')])
        
        # Verify that the mocks were called as expected
        mock_is_valid_combination.assert_called()
        mock_scorer.score_schedule.assert_called()

if __name__ == '__main__':
    unittest.main()