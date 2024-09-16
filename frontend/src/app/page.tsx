"use client";
import { Metadata } from "next";
import { useState } from "react";
import CourseInputSection from "./CourseInputSection";
import BreaksInputSection from "./BreaksInputSection";
import PreferencesInputSection from "./PreferencesInputSection";
import FullCalendar from "@fullcalendar/react";
import dayGridPlugin from "@fullcalendar/daygrid";
import timeGridPlugin from "@fullcalendar/timegrid";
import interactionPlugin from "@fullcalendar/interaction";
import momentPlugin from "@fullcalendar/moment";


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
    days: ["M", "T", "W", "R", "F"],
    timesOfDay: "",
    dayWeight: 0.5,
    timeWeight: 0.5,
  });
  const [schedules, setSchedules] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [isGenerateButtonPressed, setIsGenerateButtonPressed] =
    useState<boolean>(false);
  const [errorMessage, setErrorMessage] = useState<string>("");

  const handleNext = () => {
    setStep(step + 1);
  };

  const handlePrevious = () => {
    setStep(step - 1);
  };

  function convertTo24Hour(time: string): string {
    const [timePart, period] = time.split(" ");
    let [hours, minutes] = timePart.split(":").map(Number);

    if (period === "PM" && hours < 12) {
      hours += 12;
    } else if (period === "AM" && hours === 12) {
      hours = 0;
    }

    return `${hours.toString().padStart(2, "0")}:${minutes
      .toString()
      .padStart(2, "0")}:00`;
  }

  const handleGenerateSchedules = () => {
    if (preferences.dayWeight + preferences.timeWeight !== 1.0) {
      setErrorMessage("Day and Time Weights must add up to 1.0");
      return;
    }

    setIsLoading(true);
    setIsGenerateButtonPressed(true);
    setErrorMessage("");

    const formattedBreaks = breaks
      .filter((breakPeriod) => breakPeriod.startTime && breakPeriod.endTime)
      .map((breakPeriod) => ({
        begin_time: convertTo24Hour(breakPeriod.startTime),
        end_time: convertTo24Hour(breakPeriod.endTime),
      }));

    const payload = {
      courses: courses.map(
        (course) => `${course.subject}-${course.courseNumber}`
      ),
      breaks: formattedBreaks,
      preferred_days: preferences.days,
      preferred_time: preferences.timesOfDay,
      day_weight: preferences.dayWeight,
      time_weight: preferences.timeWeight,
    };

    console.log("Payload:", payload);

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
        setIsLoading(false);
      })
      .catch((error) => {
        console.error("Error:", error);
        setIsLoading(false);
      });
  };

  return (
    <div
      className="flex flex-col items-center bg-cover bg-center bg-no-repeat bg-slate-200 min-h-screen"
      // style={{
      //   backgroundImage: "url('/background-image.jpg')",
      // }}
    >
      <div className="flex justify-center items-center w-full">
        {/* Navigation Buttons on the Left */}
        {step > 1 && step < 4 ? (
          <button
            className="btn btn-secondary btn-circle text-white font-main"
            onClick={handlePrevious}
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
                d="M15.75 19.5 8.25 12l7.5-7.5"
              />
            </svg>
          </button>
        ) : (
          <div className="" style={{ visibility: "hidden" }}>
            <button className="btn btn-secondary btn-circle text-white font-main">
              Hidden
            </button>
          </div>
        )}

        {/* Input Sections */}
        <div className="flex flex-col items-center justify-center text-center">
          {/* Step 1 - Course Input */}
          <div
            className={`transition-opacity duration-500 ${
              step === 1 ? "opacity-100" : "opacity-0"
            }`}
            style={{ display: step === 1 ? "block" : "none" }}
          >
            <CourseInputSection courses={courses} setCourses={setCourses} />
          </div>

          {/* Step 2 - Breaks Input */}
          <div
            className={`transition-opacity duration-500 ${
              step === 2 ? "opacity-100" : "opacity-0"
            }`}
            style={{ display: step === 2 ? "block" : "none" }}
          >
            <BreaksInputSection breaks={breaks} setBreaks={setBreaks} />
          </div>

          {/* Step 3 - Preferences Input */}
          <div
            className={`transition-opacity duration-500 ${
              step === 3 ? "opacity-100" : "opacity-0"
            }`}
            style={{
              display: step === 3 ? "block" : "none",
              marginLeft: "1rem",
            }}
          >
            <PreferencesInputSection
              preferences={preferences}
              setPreferences={setPreferences}
            />
          </div>
        </div>

        {/* Navigation Buttons on the Right */}
        {step < 3 ? (
          <button
            className="btn btn-secondary btn-circle text-white font-main"
            onClick={handleNext}
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
                d="m8.25 4.5 7.5 7.5-7.5 7.5"
              />
            </svg>
          </button>
        ) : (
          <div className="" style={{ visibility: "hidden" }}>
            <button className="btn btn-secondary btn-circle text-white font-main">
              Hidden
            </button>
          </div>
        )}
      </div>

      {/* Loading Spinner */}
      {isLoading && (
        <div className="flex justify-center">
          <span className="loading loading-lg text-6xl"></span>
        </div>
      )}

      {/* Step 4 - Generated Schedules */}
      {step === 4 && (
        <div>
          <div>
            <FullCalendar 
              plugins={[
                dayGridPlugin,
                timeGridPlugin,
                interactionPlugin,
                momentPlugin, 
              ]}
              initialView="timeGridWeek"
              initialDate={"2099-01-05"}
              weekends={false}
              headerToolbar={{
                left: "prev,next",
                center: "",
                right: "",
              }}
              events={[
                { title: 'Example Class 1', start: '2099-01-05T08:00:00', end: '2099-01-05T08:50:00' },
                { title: 'Example Class 2', start: '2099-01-05T09:05:00', end: '2099-01-05T09:55:00' },
                { title: 'Example Class 3', start: '2099-01-06T09:05:00', end: '2099-01-06T09:55:00' },
              ]}
              nowIndicator={true}
              height="auto"
              allDayContent=""
              allDaySlot={false}
              slotMinTime={"08:00:00"}
              slotMaxTime={"23:00:00"}
              titleFormat={"MMMM D, YYYY"}
              dayHeaderFormat={"ddd"}
              expandRows={true}
              
              
    
              
              
            
            />         
          </div>
        </div>
        // <div className="flex flex-col items-center">
        //   <h2 className="text-3xl font-main font-bold">Generated Schedules</h2>
        //   <ul className="list-disc mt-4">
        //     {schedules.map((schedule, index) => (
        //       <li key={index} className="text-lg font-main">
        //         {schedule}
        //       </li>
        //     ))}
        //   </ul>
        // </div>
      )}

      {/* Generate Schedules Button at the Bottom */}
      {step === 3 && !isGenerateButtonPressed && (
        <div className="w-full flex flex-col items-center mb-5">
          <button
            className="btn btn-secondary text-white font-main text-xl mb-2"
            onClick={handleGenerateSchedules}
          >
            Generate Schedules
          </button>
          {errorMessage && (
            <div className="text-red-500 text-lg font-main">{errorMessage}</div>
          )}
        </div>
      )}
    </div>
  );
}
