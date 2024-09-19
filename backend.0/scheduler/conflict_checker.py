def check_conflict(time1, time2):
    """
    Check if two SectionTime objects conflict in terms of day and time.
    
    Args:
        time1, time2 (SectionTime): SectionTime objects to compare.
        
    Returns:
        bool: True if the two times conflict, False otherwise.
    """
    # check if the days of the two SectionTime objects overlap
    if set(time1.days).intersection(set(time2.days)):  # Overlapping days
        
        # check if the end time of time1 is greater than the begin time of time2
        if time1.end_time > time2.begin_time and time1.begin_time < time2.end_time: 
            # print(f"Conflict found: {time1} conflicts with {time2}")
            return True
    
    return False  


def is_valid_combination(current_combination, new_section_times, breaks):
    """
    Check if adding new SectionTime objects to the current combination results in any conflicts.
    
    Args:
        current_combination (list): The current combination of SectionTime objects.
        new_section_times (list): SectionTime objects to add to the combination.
        breaks (list): List of break times to avoid conflicts with.
        
    Returns:
        bool: True if the combination remains valid after adding the new SectionTime objects.
    """
    for new_time in new_section_times: # iterate through the new_section_times
        for existing_time in current_combination: # iterate through the current_combination
            
            # check if there is a conflict between the new_time and existing_time
            if check_conflict(new_time, existing_time):
                # print(f"Pruned due to conflict: {new_time} with existing {existing_time}")
                return False
        
        # Check for conflicts with the breaks
        for break_time in breaks:
            
            # check if the begin time of new_time is greater than or equal to the begin time of break_time and less than or equal to the end time of break_time
            if new_time.begin_time >= break_time['begin_time'] and new_time.begin_time <= break_time['end_time']:
                # print(f"Pruned due to break conflict: {new_time} with break {break_time}")
                return False

    return True