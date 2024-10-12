// Import necessary dependencies and types
import React, { useState, useEffect } from "react";
import subjectData from "./subject_data.json" assert { type: "json" };

// Define types for the subject data and course structure
interface SubjectData {
  [key: string]: string[];
}

interface Course {
  subject: string;
  courseNumber: string;
}

// Define props for the CourseInputSection component
interface CourseInputSectionProps {
  courses: Course[];
  setCourses: React.Dispatch<React.SetStateAction<Course[]>>;
}

// Cast the imported subject data to the correct type
const typedSubjectData: SubjectData = subjectData;

/**
 * CourseInputSection Component
 *
 * This component allows users to input multiple courses by selecting a subject
 * and course number. It provides autocomplete suggestions for both fields and
 * allows adding/removing courses dynamically.
 *
 * @param {Course[]} courses - Array of current course selections
 * @param {Function} setCourses - Function to update the courses array
 */
export default function CourseInputSection({
  courses,
  setCourses,
}: CourseInputSectionProps) {
  // State for available subjects and course numbers
  const [subjects, setSubjects] = useState<string[]>(Object.keys(subjectData));
  const [courseNumbers, setCourseNumbers] = useState<string[]>([]);

  /**
   * Handle changes to course inputs
   * @param {number} index - Index of the course being modified
   * @param {"subject" | "courseNumber"} field - Field being changed
   * @param {string} value - New value for the field
   */
  const handleCourseChange = (
    index: number,
    field: "subject" | "courseNumber",
    value: string
  ) => {
    const newCourses = [...courses];
    newCourses[index] = { ...newCourses[index], [field]: value };

    // Reset course number when subject changes
    if (field === "subject") {
      newCourses[index].courseNumber = "";
    }

    setCourses(newCourses);
  };

  /**
   * Add a new empty course to the list
   */
  const addCourse = () => {
    if (courses.length < 8) {
      setCourses([...courses, { subject: "", courseNumber: "" }]);
    }
  };

  /**
   * Remove a course from the list
   * @param {number} index - Index of the course to remove
   */
  const removeCourse = (index: number) => {
    const newCourses = courses.filter((_, i) => i !== index);
    setCourses(newCourses);
  };

  // Update available course numbers when subject changes
  useEffect(() => {
    const lastCourse = courses[courses.length - 1];
    if (lastCourse && lastCourse.subject) {
      setCourseNumbers(typedSubjectData[lastCourse.subject] || []);
    } else {
      setCourseNumbers([]);
    }
  }, [courses]);

  return (
    <div className="flex justify-center items-center flex-col my-8 px-4">
      <div className="w-full max-w-4xl p-8 bg-neutral shadow-lg rounded-xl text-center">
        <h1 className="font-main text-5xl font-extrabold mb-6 text-primary">
          Course Input
        </h1>

        {/* Instructions for users */}
        <div className="space-y-4 mb-8">
          <p className="text-lg mt-2">
            Enter the subject and course number for each class you are taking
          </p>
          <p className="text-lg">Example: MATH-1225</p>
          <p className="text-sm mt-2 text-gray-600">
            If a course has both a lecture and lab, please specify the lab by
            adding a &quot;B&quot; to the course number.
            <br />
            Example: PHYS-2305 (Lecture) | PHYS-2305B (Lab)
          </p>
        </div>

        <div className="bg-primary shadow-xl rounded-lg p-6">
          <div className="grid grid-cols-1 gap-6">
            {/* Render input fields for each course */}
            {courses.map((course, index) => (
              <div
                key={index}
                className="flex items-center justify-center gap-x-4 ml-16"
              >
                {/* Subject input with autocomplete */}
                <div className="relative">
                  <input
                    type="text"
                    placeholder="Subject"
                    value={course.subject}
                    onChange={(e) =>
                      handleCourseChange(
                        index,
                        "subject",
                        e.target.value.toUpperCase()
                      )
                    }
                    className="text-transform: uppercase font-main bg-accent text-lg input input-bordered w-48 text-center focus:outline-none focus:ring-2 focus:ring-secondary"
                    list={`subjects-${index}`}
                  />
                  <datalist id={`subjects-${index}`}>
                    {subjects
                      .filter((subject) => subject.startsWith(course.subject))
                      .map((subject) => (
                        <option key={subject} value={subject} />
                      ))}
                  </datalist>
                </div>

                <span className="text-3xl text-neutral">-</span>

                {/* Course number input with autocomplete */}
                <div className="relative">
                  <input
                    type="text"
                    placeholder="Course NUM"
                    value={course.courseNumber}
                    onChange={(e) =>
                      handleCourseChange(
                        index,
                        "courseNumber",
                        e.target.value.toUpperCase()
                      )
                    }
                    className="text-transform: uppercase font-main bg-accent text-lg input input-bordered w-48 text-center focus:outline-none focus:ring-2 focus:ring-secondary"
                    list={`courseNumbers-${index}`}
                  />
                  <datalist id={`courseNumbers-${index}`}>
                    {courseNumbers
                      .filter((number) =>
                        number.startsWith(course.courseNumber)
                      )
                      .map((number) => (
                        <option key={number} value={number} />
                      ))}
                  </datalist>
                </div>

                {/* Remove course button (hidden for the first course) */}
                {courses.length > 1 && index > 0 ? (
                  <button
                    className="font-main btn btn-circle bg-accent text-xl ml-2 text-center border-none hover:bg-secondary hover:text-white"
                    onClick={() => removeCourse(index)}
                  >
                    <svg
                      xmlns="http://www.w3.org/2000/svg"
                      fill="none"
                      viewBox="0 0 24 24"
                      strokeWidth={1.5}
                      stroke="currentColor"
                      className="size-6"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        d="M5 12h14"
                      />
                    </svg>
                  </button>
                ) : (
                  <div className="ml-2" style={{ visibility: "hidden" }}>
                    <button className="font-main btn btn-circle">
                      <svg
                        xmlns="http://www.w3.org/2000/svg"
                        fill="none"
                        viewBox="0 0 24 24"
                        strokeWidth={1.5}
                        stroke="currentColor"
                        className="size-6"
                      >
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          d="M5 12h14"
                        />
                      </svg>
                    </button>
                  </div>
                )}
              </div>
            ))}
          </div>

          {/* Add course button (visible only if less than 8 courses) */}
          {courses.length < 8 && (
            <div className="flex justify-center mt-6 mr-2">
              <button
                className="font-main bg-accent btn btn-circle text-lg text-center border-none hover:bg-secondary hover:text-white"
                onClick={addCourse}
              >
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  fill="none"
                  viewBox="0 0 24 24"
                  strokeWidth={1.5}
                  stroke="currentColor"
                  className="size-6"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    d="M12 4.5v15m7.5-7.5h-15"
                  />
                </svg>
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
