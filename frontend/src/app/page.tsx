"use client";
import { Metadata } from "next";
import { useState } from "react";
import CourseInputSection from "./CourseInputSection";
import BreaksInputSection from "./BreaksInputSection";
import PreferencesInputSection from "./PreferencesInputSection";

interface Course {
  subject: string;
  courseNumber: string;
}

interface BreakPeriod {
  startTime: string;
  endTime: string;
}

interface Preferences {
  days: string[];
  timesOfDay: string;
  dayWeight: number;
  timeWeight: number;
}

// export const metadata: Metadata = {
//   title: "Home Page",
// };

export default function Home() {
  const [step, setStep] = useState<number>(1);
  const [courses, setCourses] = useState<Course[]>([
    { subject: "", courseNumber: "" },
  ]);
  const [breaks, setBreaks] = useState<BreakPeriod[]>([
    { startTime: "", endTime: "" },
  ]);
  const [preferences, setPreferences] = useState<Preferences>({
    days: [],
    timesOfDay: "",
    dayWeight: 0.5,
    timeWeight: 0.5,
  });
  const [schedules, setSchedules] = useState<any[]>([]);

  const handleNext = () => {
    setStep(step + 1);
  };

  const handlePrevious = () => {
    setStep(step - 1);
  };

  const handleGenerateSchedules = () => {
    const payload = {
      courses: courses.map(
        (course) => `${course.subject}-${course.courseNumber}`
      ),
      breaks: breaks
        .filter((breakPeriod) => breakPeriod.startTime && breakPeriod.endTime) // Filter out empty break periods
        .map((breakPeriod) => ({
          begin_time: breakPeriod.startTime,
          end_time: breakPeriod.endTime,
        })),
      preferred_days: preferences.days,
      preferred_time: preferences.timesOfDay,
      day_weight: preferences.dayWeight,
      time_weight: preferences.timeWeight,
    };

    fetch("http://127.0.0.1:8000/class_scheduler/generate-schedules/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(payload),
    })
      .then((response) => response.json())
      .then((data) => {
        console.log("API Response Data:", data);
        setSchedules(Array.isArray(data) ? data : []);
        setStep(step + 1);
      })
      .catch((error) => {
        console.error("Error:", error);
      });
  };

  return (
    <div>
      <div className="flex justify-center">
        {step === 1 && (
          <CourseInputSection courses={courses} setCourses={setCourses} />
        )}
        {step === 2 && (
          <BreaksInputSection breaks={breaks} setBreaks={setBreaks} />
        )}
        {step === 3 && (
          <PreferencesInputSection
            preferences={preferences}
            setPreferences={setPreferences}
          />
        )}
      </div>

      {step < 4 && (
        <div className="flex justify-end m-5 space-x-3">
          {step > 1 && (
            <button
              className="btn btn-primary text-white font-main"
              onClick={handlePrevious}
            >
              Previous
            </button>
          )}
          <button
            className="btn btn-secondary text-white"
            onClick={step === 3 ? handleGenerateSchedules : handleNext}
          >
            {step === 3 ? "Generate Schedules" : "Next"}
          </button>
        </div>
      )}

      {step === 4 && (
        <div className="flex flex-col items-center">
          <h2 className="text-3xl font-main font-bold">Generated Schedules</h2>
          <ul className="list-disc mt-4">
            {schedules.map((schedule, index) => (
              <li key={index} className="text-lg font-main">
                {schedule}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
