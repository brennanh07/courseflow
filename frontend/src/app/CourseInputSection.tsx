import React from "react";
// import './globals.css';

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
    <div className="flex justify-center items-center flex-col gap-y-2 my-4">
      <h1 className="font-main text-6xl">Courses</h1>
      <h4 className="font-main text-xl">
        Enter the subject and course number for each class you are taking
      </h4>
      <h5 className="font-main">Example: MATH - 1225</h5>
      <h4 className="font-main text-xl">
        If a course has both a lecture and lab, please specify by adding the
        corresponding letter to the end of the course number (L = Lecture, B =
        Lab)
      </h4>
      <h5 className="font-main">Example: PHYS - 2305L -or- PHYS - 2305B</h5>

      <div className="border bg-red-800 rounded-xl w-fit object-center flex flex-col p-3.5 gap-y-2.5 my-4">
        {courses.map((course, index) => (
          <div className="flex justify-center items-center" key={index}>
            <input
              type="text"
              placeholder="Subject"
              value={course.subject}
              onChange={(e) =>
                handleCourseChange(index, "subject", e.target.value)
              }
              className="font-main bg-accent text-lg input input-bordered max-w-xs text-center w-44 focus:outline-none focus:ring-2 focus:ring-secondary"
            />
            <span className="mx-4 text-3xl text-white">-</span>
            <input
              type="text"
              placeholder="Course Number"
              value={course.courseNumber}
              onChange={(e) =>
                handleCourseChange(index, "courseNumber", e.target.value)
              }
              className="font-main bg-accent text-lg input input-bordered max-w-xs text-center w-44 focus:outline-none focus:ring-2 focus:ring-secondary"
            />
            {courses.length > 1 && index > 0 ? (
              <button
                className="font-main btn bg-accent text-xl ml-2 text-center border-none hover:bg-secondary hover:text-white"
                onClick={() => removeCourse(index)}
              >
                -
              </button>
            ) : (
              <div className="ml-2" style={{ visibility: "hidden" }}>
                <button className="font-main btn">-</button>
              </div>
            )}
          </div>
        ))}
        {courses.length < 8 && (
          <div className="flex justify-center">
            <button
              className="font-main bg-accent btn mr-12 text-lg text-center border-none hover:bg-secondary hover:text-white"
              onClick={addCourse}
            >
              +
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
