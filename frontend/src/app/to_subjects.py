import json

courses = """
"""

# Function to process the input into the desired format
def process_courses(course_list):
    course_dict = {}
    for line in course_list.strip().splitlines():
        subject, course_num = line.split('-')
        if subject in course_dict:
            course_dict[subject].append(course_num)
        else:
            course_dict[subject] = [course_num]
    return course_dict

# Convert courses to dictionary
course_dict = process_courses(courses)

# Save to JSON file
with open('subject_data.json', 'w') as json_file:
    json.dump(course_dict, json_file, indent=2)

print("Data successfully written to subject_data.json.")