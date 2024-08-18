import React from "react";

interface Course {
  subject: string;
  courseNumber: string;
}

interface CourseInputSectionProps {
  courses: Course[];
  setCourses: React.Dispatch<React.SetStateAction<Course[]>>;
}

export default function CourseInputSection({
  courses,
  setCourses,
}: CourseInputSectionProps) {
  const handleCourseChange = (
    index: number,
    field: "subject" | "courseNumber",
    value: string
  ) => {
    const newCourses = [...courses];
    newCourses[index] = { ...newCourses[index], [field]: value };
    setCourses(newCourses);
  };

  const addCourse = () => {
    if (courses.length < 8) {
      setCourses([...courses, { subject: "", courseNumber: "" }]);
    }
  };

  const removeCourse = (index: number) => {
    const newCourses = courses.filter((_, i) => i !== index);
    setCourses(newCourses);
  };

  return (
    <div>
      <h1>Courses</h1>
      <h4>Enter the subject and course number for each class you are taking</h4>
      <h5>Example: MATH-1225</h5>
      <h4>
        If a course has both a lecture and lab, please specify by adding the
        corresponding letter to the end of the course number (L = Lecture, B =
        Lab)
      </h4>
      <h5>Example: PHYS-2305L | PHYS-2305B</h5>
      {courses.map((course, index) => (
        <div key={index}>
          <input
            type="text"
            placeholder="Subject"
            value={course.subject}
            onChange={(e) =>
              handleCourseChange(index, "subject", e.target.value)
            }
            className="input"
          />
          <span className="mx-2">-</span>
          <input
            type="text"
            placeholder="Course Number"
            value={course.courseNumber}
            onChange={(e) =>
              handleCourseChange(index, "courseNumber", e.target.value)
            }
            className="input"
          />
          {courses.length > 1 && index > 0 && (
            <button onClick={() => removeCourse(index)}>Remove</button>
          )}
        </div>
      ))}
      {courses.length < 8 && <button onClick={addCourse}>Add Course</button>}
    </div>
  );
}
