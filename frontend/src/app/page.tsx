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

  const handleNext = () => {
    setStep(step + 1);
  };

  const handlePrevious = () => {
    setStep(step - 1);
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
          <button className="btn btn-secondary text-white" onClick={handleNext}>
            {step === 3 ? "Generate Schedules" : "Next"}
          </button>
        </div>
      )}

      {step === 4 && <div>{/* Display schedules */}</div>}
    </div>
  );
}
