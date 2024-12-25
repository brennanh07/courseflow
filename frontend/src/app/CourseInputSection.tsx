// Import necessary dependencies and types
import React, { useState, useEffect, useCallback } from "react";
import subjectData from "./subject_data.json" assert { type: "json" };

// Define types for the subject data and course structure
interface SubjectData {
  [key: string]: string[];
}

interface Course {
  id: string; // Unique identifier for stable element relationships
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
 * Layout has been optimized to prevent shifting issues when entering similar subjects
 * across different rows. Each row maintains its own independent state for course numbers.
 *
 * The component uses unique IDs for each course to maintain stable relationships between
 * input fields and their associated datalists, preventing DOM update errors during
 * course removal operations.
 *
 * @param {Course[]} courses - Array of current course selections
 * @param {Function} setCourses - Function to update the courses array
 */
export default function CourseInputSection({
  courses,
  setCourses,
}: CourseInputSectionProps) {
  // State for available subjects (remains constant after initialization)
  const [subjects] = useState<string[]>(Object.keys(subjectData));

  /**
   * State for available course numbers, stored per course ID to prevent interference
   * between different input rows. Each key is a course ID corresponding to a course row.
   * @type {{ [key: string]: string[] }}
   */
  const [availableCourseNumbers, setAvailableCourseNumbers] = useState<{
    [key: string]: string[];
  }>({});

  /**
   * Handle changes to course inputs
   * Updates the course data and manages the available course numbers for autocomplete
   *
   * @param {string} courseId - Unique identifier of the course being modified
   * @param {"subject" | "courseNumber"} field - Field being changed
   * @param {string} value - New value for the field
   */
  const handleCourseChange = useCallback(
    (courseId: string, field: "subject" | "courseNumber", value: string) => {
      setCourses((prevCourses) => {
        return prevCourses.map((course) => {
          if (course.id !== courseId) return course;

          const updatedCourse = { ...course, [field]: value };

          // Reset course number when subject changes and update available course numbers
          if (field === "subject") {
            updatedCourse.courseNumber = "";
            // Update available course numbers for this specific course ID
            if (value && typedSubjectData[value]) {
              setAvailableCourseNumbers((prev) => ({
                ...prev,
                [courseId]: typedSubjectData[value],
              }));
            } else {
              setAvailableCourseNumbers((prev) => {
                const updated = { ...prev };
                delete updated[courseId];
                return updated;
              });
            }
          }

          return updatedCourse;
        });
      });
    },
    []
  );

  /**
   * Add a new empty course to the list
   * Limited to maximum of 8 courses
   * Generates a unique ID for the new course using timestamp and random string
   */
  const addCourse = useCallback(() => {
    if (courses.length < 8) {
      const newCourse: Course = {
        id: `course-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
        subject: "",
        courseNumber: "",
      };
      setCourses((prevCourses) => [...prevCourses, newCourse]);
    }
  }, [courses.length]);

  /**
   * Remove a course from the list
   * Also cleans up the associated course numbers in state
   * Uses course ID instead of index for stable removal operations
   *
   * @param {string} courseId - Unique identifier of the course to remove
   */
  const removeCourse = useCallback((courseId: string) => {
    // First, remove the course numbers from state
    setAvailableCourseNumbers((prev) => {
      const updated = { ...prev };
      delete updated[courseId];
      return updated;
    });

    // Then, update the courses array
    setCourses((prevCourses) =>
      prevCourses.filter((course) => course.id !== courseId)
    );
  }, []);

  /**
   * Cleanup effect to remove stale course numbers when courses are removed
   * Ensures synchronization between courses and their associated data
   */
  useEffect(() => {
    const currentCourseIds = new Set(courses.map((course) => course.id));
    setAvailableCourseNumbers((prev) => {
      const updated = { ...prev };
      Object.keys(updated).forEach((id) => {
        if (!currentCourseIds.has(id)) {
          delete updated[id];
        }
      });
      return updated;
    });
  }, [courses]);

  return (
    <div className="flex justify-center items-center flex-col my-8 px-4">
      <div className="w-full max-w-4xl p-4 sm:p-6 md:p-8 bg-neutral shadow-lg rounded-xl text-center">
        <h1 className="font-main text-3xl sm:text-4xl md:text-5xl font-extrabold mb-4 sm:mb-6 text-primary">
          Course Input
        </h1>

        <div className="space-y-2 sm:space-y-4 mb-6 sm:mb-8">
          <p className="text-base sm:text-lg mt-2">
            Enter the subject and course number for each class you are taking
          </p>
          <p className="text-base sm:text-lg">Example: MATH-1225</p>
          <p className="text-xs sm:text-sm mt-2 text-gray-600">
            If a course has both a lecture and lab, please specify the lab by
            adding a &quot;B&quot; to the course number.
            <br />
            Example: PHYS-2305 (Lecture) | PHYS-2305B (Lab)
          </p>
        </div>

        <div className="bg-primary shadow-xl rounded-lg p-4 sm:p-6">
          <div className="grid grid-cols-1 gap-4 sm:gap-6">
            {courses.map((course) => (
              <div key={course.id} className="relative flex justify-center">
                {/* Center container for SUBJECT-COURSENUM */}
                <div className="flex items-center justify-center">
                  <div className="w-40 sm:w-48">
                    <input
                      type="text"
                      placeholder="Subject"
                      value={course.subject}
                      onChange={(e) =>
                        handleCourseChange(
                          course.id,
                          "subject",
                          e.target.value.toUpperCase()
                        )
                      }
                      className="text-transform: uppercase font-main bg-accent text-base sm:text-lg input input-bordered w-full text-center focus:outline-none focus:ring-2 focus:ring-secondary"
                      list={`subjects-${course.id}`}
                    />
                    <datalist id={`subjects-${course.id}`}>
                      {subjects
                        .filter((subject) =>
                          subject
                            .toUpperCase()
                            .startsWith(course.subject.toUpperCase())
                        )
                        .map((subject) => (
                          <option key={subject} value={subject} />
                        ))}
                    </datalist>
                  </div>

                  <span className="text-2xl sm:text-3xl text-neutral mx-4">
                    -
                  </span>

                  <div className="w-40 sm:w-48">
                    <input
                      type="text"
                      placeholder="Course NUM"
                      value={course.courseNumber}
                      onChange={(e) =>
                        handleCourseChange(
                          course.id,
                          "courseNumber",
                          e.target.value.toUpperCase()
                        )
                      }
                      className="text-transform: uppercase font-main bg-accent text-base sm:text-lg input input-bordered w-full text-center focus:outline-none focus:ring-2 focus:ring-secondary"
                      list={`courseNumbers-${course.id}`}
                    />
                    <datalist id={`courseNumbers-${course.id}`}>
                      {availableCourseNumbers[course.id]?.map((number) => (
                        <option key={number} value={number} />
                      ))}
                    </datalist>
                  </div>
                </div>

                {/* Absolutely positioned remove button - only show for non-initial courses when there's more than one */}
                {courses.length > 1 && !course.id.includes("initial") && (
                  <button
                    type="button"
                    className="absolute right-0 top-1/2 -translate-y-1/2 font-main btn btn-circle bg-accent text-xl text-center border-none hover:bg-secondary hover:text-white ml-4"
                    onClick={() => removeCourse(course.id)}
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
                )}
              </div>
            ))}
          </div>

          {courses.length < 8 && (
            <div className="flex justify-center mt-4 sm:mt-6">
              <button
                type="button"
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
