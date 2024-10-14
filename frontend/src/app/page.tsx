"use client";
import { useState, useEffect } from "react";
import CourseInputSection from "./CourseInputSection";
import BreaksInputSection from "./BreaksInputSection";
import PreferencesInputSection from "./PreferencesInputSection";
import FullCalendar from "@fullcalendar/react";
import dayGridPlugin from "@fullcalendar/daygrid";
import timeGridPlugin from "@fullcalendar/timegrid";
import interactionPlugin from "@fullcalendar/interaction";
import momentPlugin from "@fullcalendar/moment";
import { Button, Dialog, DialogPanel, DialogTitle } from "@headlessui/react";
import "./globals.css";

// Define interfaces for data structures
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

interface ClassEvent {
  title: string;
  start: Date | string;
  end: Date | string;
  crn: string;
}

export default function Home() {
  // State variables
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
  const [events, setEvents] = useState<ClassEvent[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [isGenerateButtonPressed, setIsGenerateButtonPressed] =
    useState<boolean>(false);
  const [errorMessage, setErrorMessage] = useState<string>("");
  const [isModalOpen, setIsModalOpen] = useState<boolean>(false);
  const [selectedEvent, setSelectedEvent] = useState<ClassEvent | null>(null);
  const [isTimeout, setIsTimeout] = useState<boolean>(false);
  const [schedules, setSchedules] = useState<ClassEvent[][]>([]);
  const [currentScheduleIndex, setCurrentScheduleIndex] = useState<number>(0);
  const [isCRNModalOpen, setIsCRNModalOpen] = useState<boolean>(false);
  const [copiedCRN, setCopiedCRN] = useState<string | null>(null);

  // Navigation functions
  const handleNext = () => setStep(step + 1);
  const handlePrevious = () => setStep(step - 1);

  // Time conversion functions
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

  type DayOfWeek = "M" | "T" | "W" | "R" | "F";

  function convertToISODate(day: DayOfWeek, time: string): string {
    const daysOfWeek: Record<DayOfWeek, string> = {
      M: "2099-01-05",
      T: "2099-01-06",
      W: "2099-01-07",
      R: "2099-01-08",
      F: "2099-01-09",
    };
    return `${daysOfWeek[day]}T${convertTo24Hour(time)}`;
  }

  function convertFromISODate(isoDate: string): string {
    const date = new Date(isoDate);
    let hours = date.getHours();
    const minutes = date.getMinutes();
    const ampm = hours >= 12 ? "PM" : "AM";
    hours = hours % 12;
    hours = hours ? hours : 12;
    const minutesStr = minutes < 10 ? "0" + minutes : minutes;
    return `${hours}:${minutesStr} ${ampm}`;
  }

  // Function to handle schedule generation
  const handleGenerateSchedules = () => {
    // Validation check for weights
    if (preferences.dayWeight + preferences.timeWeight !== 1.0) {
      setErrorMessage("Day and Time Weights must add up to 1.0");
      return;
    }

    setIsLoading(true);
    setIsGenerateButtonPressed(true);
    setErrorMessage("");
    setIsTimeout(false);

    // Format breaks for API request
    const formattedBreaks = breaks
      .filter((breakPeriod) => breakPeriod.startTime && breakPeriod.endTime)
      .map((breakPeriod) => ({
        begin_time: convertTo24Hour(breakPeriod.startTime),
        end_time: convertTo24Hour(breakPeriod.endTime),
      }));

    // Prepare payload for API request
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

    // Make API request to generate schedules
    fetch("http://127.0.0.1:8000/api/v1/generate-schedules/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(payload),
    })
      .then((response) => response.json())
      .then((data) => {
        console.log("API Response Data:", data);

        if (data.schedules.length === 0) {
          setErrorMessage(
            "No schedules found. Please remove one or more breaks."
          );
          setIsLoading(false);
          return;
        }

        if (data.schedules[0] === "timeout") {
          setIsTimeout(true);
          setIsLoading(false);
          return;
        }

        // Process and format the received schedules
        const allSchedules: ClassEvent[][] = [];

        data.schedules.forEach((schedule: any) => {
          const scheduleEvents: ClassEvent[] = [];
          Object.keys(schedule.days).forEach((day) => {
            const dayOfWeek = day as DayOfWeek;
            schedule.days[dayOfWeek].forEach((classInfo: string) => {
              const [title, timeRange] = classInfo.split(": ");
              const [startTime, endTime] = timeRange.split(" - ");
              scheduleEvents.push({
                title,
                start: convertToISODate(dayOfWeek, startTime),
                end: convertToISODate(dayOfWeek, endTime),
                crn: `${schedule.crns[title.split(": ")[0]]}`,
              });
            });
          });
          allSchedules.push(scheduleEvents);
        });

        setSchedules(allSchedules);
        setEvents(allSchedules[0]);
        setCurrentScheduleIndex(0);
        setStep(step + 1);
        setIsLoading(false);
      })
      .catch((error) => {
        console.error("Error:", error);
        setIsLoading(false);
        setIsTimeout(true);
      });
  };

  // Functions to navigate between generated schedules
  const handleNextSchedule = () => {
    const nextIndex = (currentScheduleIndex + 1) % schedules.length;
    setCurrentScheduleIndex(nextIndex);
    setEvents(schedules[nextIndex]);
  };

  const handlePreviousSchedule = () => {
    const previousIndex =
      (currentScheduleIndex - 1 + schedules.length) % schedules.length;
    setCurrentScheduleIndex(previousIndex);
    setEvents(schedules[previousIndex]);
  };

  // Function to handle calendar event clicks
  const handleEventClick = (info: any) => {
    setSelectedEvent({
      title: info.event.title,
      start: info.event.start,
      end: info.event.end,
      crn: info.event.extendedProps.crn,
    });
    setIsModalOpen(true);
  };

  // Function to handle CRN button click
  const handleCRNButtonClick = () => {
    setIsCRNModalOpen(true);
  };

  // Function to copy CRN to clipboard
  const handleCopyCRN = (crn: string) => {
    navigator.clipboard.writeText(crn).then(() => {
      setCopiedCRN(crn);
      setTimeout(() => setCopiedCRN(null), 2000);
    });
  };

  // Function to get CRNs of the current schedule
  const getCurrentScheduleCRNs = () => {
    if (
      schedules.length === 0 ||
      currentScheduleIndex < 0 ||
      currentScheduleIndex >= schedules.length
    ) {
      console.log("No schedules available or invalid index");
      return [];
    }

    const currentSchedule = schedules[currentScheduleIndex];
    if (!currentSchedule || !Array.isArray(currentSchedule)) {
      console.log("Current schedule is not an array");
      return [];
    }

    const uniqueClassesAndCRNs = new Map();

    currentSchedule.forEach((event) => {
      const className = event.title.split(": ")[0];
      if (!uniqueClassesAndCRNs.has(className)) {
        uniqueClassesAndCRNs.set(className, event.crn);
      }
    });

    return Array.from(uniqueClassesAndCRNs, ([className, crn]) => ({
      className,
      crn,
    }));
  };

  const handleReturnToCourseInput = () => {
    setStep(1);
    setIsGenerateButtonPressed(false);
    setErrorMessage("");
    setIsTimeout(false);
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
      {isTimeout && (
        <div className="flex justify-center">
          <span className="text-lg font-main text-red-500">
            Too many possible schedules. Please add breaks.
          </span>
        </div>
      )}
      {errorMessage && (
        <div className="flex justify-center">
          <span className="text-lg font-main text-red-500">{errorMessage}</span>
        </div>
      )}

      {/* Step 4 - Generated Schedules */}
      {step === 4 && (
        <div className="flex flex-col items-center p-4 -mt-10 -mb-20 w-full">
          <div className="flex justify-between items-center w-full mb-4">
            <div className="w-1/3">
              <button
                className="btn btn-primary text-white font-main ml-16"
                onClick={handleReturnToCourseInput}
              >
                Return to Course Input
              </button>{" "}
              {/* This empty div helps with centering */}
            </div>
            <span className="text-lg font-main text-center w-1/3 font-bold">
              Schedule {currentScheduleIndex + 1} of {schedules.length}
            </span>
            <div className="w-1/3 flex justify-end">
              <button
                className="btn btn-secondary text-white font-main mr-16"
                onClick={handleCRNButtonClick}
              >
                Copy CRNs
              </button>
            </div>
          </div>
          <div className="flex items-center justify-center w-full">
            <button
              className="btn btn-secondary btn-circle text-white font-main mr-4"
              onClick={handlePreviousSchedule}
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
            <div className="bg-white shadow-xl rounded rounded-xl flex-grow">
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
                  left: "",
                  center: "",
                  right: "",
                }}
                events={events}
                nowIndicator={true}
                height="auto"
                allDayContent=""
                allDaySlot={false}
                slotMinTime={"08:00:00"}
                slotMaxTime={"23:00:00"}
                titleFormat={"MMMM D, YYYY"}
                dayHeaderFormat={"ddd"}
                eventClick={handleEventClick}
                eventColor="#861F41"
              />
            </div>
            <button
              className="btn btn-secondary btn-circle text-white font-main ml-4"
              onClick={handleNextSchedule}
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
          </div>
        </div>
      )}

      {/* Steps Indicator UI*/}
      {step !== 4 && (
        <ul className="steps w-1/2 mb-5 font-main font-bold">
          <li className={`step ${step >= 1 ? "step-primary" : ""}`}>Courses</li>
          <li className={`step ${step >= 2 ? "step-primary" : ""}`}>Breaks</li>
          <li className={`step ${step >= 3 ? "step-primary" : ""}`}>
            Preferences
          </li>
        </ul>
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

      {/* Event Info Modal */}
      {isModalOpen && selectedEvent && (
        <Dialog
          open={isModalOpen}
          as="div"
          className="relative z-10"
          onClose={() => setIsModalOpen(false)}
        >
          <div className="fixed inset-0 bg-black/30" aria-hidden="true" />
          <div className="fixed inset-0 z-10 w-screen overflow-y-auto">
            <div className="flex min-h-full items-center justify-center p-4">
              <DialogPanel className="w-full max-w-md rounded-xl bg-white p-6 shadow-xl">
                <DialogTitle
                  as="h2"
                  className="font-main text-2xl font-bold mb-4 text-primary"
                >
                  {selectedEvent.title}
                </DialogTitle>
                <p className="mb-2">
                  <strong>Start:</strong>{" "}
                  {convertFromISODate(selectedEvent.start.toString())}
                </p>
                <p className="mb-2">
                  <strong>End:</strong>{" "}
                  {convertFromISODate(selectedEvent.end.toString())}
                </p>
                <p>
                  <strong>CRN:</strong> {selectedEvent.crn}
                </p>
                <div className="mt-4">
                  <Button
                    className="inline-flex items-center gap-2 rounded-md bg-primary py-1.5 px-3 text-sm/6 font-semibold text-white shadow-inner shadow-white/10 focus:outline-none data-[hover]:bg-gray-600 data-[focus]:outline-1 data-[focus]:outline-white data-[open]:bg-gray-700"
                    onClick={() => setIsModalOpen(false)}
                  >
                    Close
                  </Button>
                </div>
              </DialogPanel>
            </div>
          </div>
        </Dialog>
      )}

      {/* CRN Modal */}
      <Dialog
        open={isCRNModalOpen}
        onClose={() => setIsCRNModalOpen(false)}
        className="relative z-10"
      >
        <div className="fixed inset-0 bg-black/30" aria-hidden="true" />
        <div className="fixed inset-0 flex items-center justify-center p-4">
          <DialogPanel className="w-full max-w-md rounded-xl bg-white p-6 shadow-xl">
            <DialogTitle className="text-xl font-bold mb-4 text-primary font-main">
              CRNs for Current Schedule
            </DialogTitle>
            <div className="space-y-2">
              {getCurrentScheduleCRNs().length > 0 ? (
                getCurrentScheduleCRNs().map(({ className, crn }) => (
                  <div key={crn} className="flex justify-between items-center">
                    <span className="font-medium">
                      {className}: <span className="font-bold">{crn}</span>
                    </span>
                    <button
                      onClick={() => handleCopyCRN(crn)}
                      className="btn btn-sm btn-secondary text-white ml-4"
                    >
                      {copiedCRN === crn ? "Copied!" : "Copy"}
                    </button>
                  </div>
                ))
              ) : (
                <p>No CRNs available for the current schedule.</p>
              )}
            </div>
            <div className="mt-4">
              <button
                onClick={() => setIsCRNModalOpen(false)}
                className="btn btn-primary text-white"
              >
                Close
              </button>
              <div className="mt-4 text-center">
                <p className="text-sm">
                  Add CRNs in{" "}
                  <a
                    href="https://vt.collegescheduler.com/"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-blue-500 underline"
                  >
                    Hokie Scheduler
                  </a>
                </p>
              </div>
            </div>
          </DialogPanel>
        </div>
      </Dialog>
    </div>
  );
}
