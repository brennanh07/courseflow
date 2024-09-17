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
import { Description, Dialog, DialogPanel, DialogTitle, Button } from '@headlessui/react'
import MyModal from "./EventInfoModal";

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
  info: string;
  // crn: string;
  // location: string;
  // instructor: string;

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
  const [events, setEvents] = useState<ClassEvent[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [isGenerateButtonPressed, setIsGenerateButtonPressed] =
    useState<boolean>(false);
  const [errorMessage, setErrorMessage] = useState<string>("");

  const [isModalOpen, setIsModalOpen] = useState<boolean>(false);
  const [selectedEvent, setSelectedEvent] = useState<ClassEvent | null>(null);

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

  type DayOfWeek = "M" | "T" | "W" | "R" | "F";

  function convertToISODate(day: DayOfWeek, time: string): string {
    const daysOfWeek : Record<DayOfWeek, string> = {
      M: "2099-01-05",
      T: "2099-01-06",
      W: "2099-01-07",
      R: "2099-01-08",
      F: "2099-01-09",
    };
    return `${daysOfWeek[day]}T${convertTo24Hour(time)}`;
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
    // testing with the first schedule returned only
    .then((response) => response.json())
    .then((data) => {
      console.log("API Response Data:", data);
      setSchedules(Array.isArray(data) ? data : []);
      const newEvents: ClassEvent[] = [];
      const firstSchedule = data.schedules[0]; // Extract the first schedule
      Object.keys(firstSchedule.days).forEach((day) => {
        const dayOfWeek = day as DayOfWeek;
        firstSchedule.days[dayOfWeek].forEach((classInfo: string) => {
          const [title, timeRange] = classInfo.split(": ");
          const [startTime, endTime] = timeRange.split(" - ");
          newEvents.push({
            title,
            start: convertToISODate(dayOfWeek, startTime),
            end: convertToISODate(dayOfWeek, endTime),
            info: `CRN: ${firstSchedule.crns[title.split(": ")[0]]}`,
          });
        });
      });
      setEvents(newEvents);
      setStep(step + 1);
      setIsLoading(false);
    })
    .catch((error) => {
      console.error("Error:", error);
      setIsLoading(false);
    });
  };
  //     .then((response) => response.json())
  //     .then((data) => {
  //       console.log("API Response Data:", data);
  //       setSchedules(Array.isArray(data) ? data : []);
  //       const newEvents: ClassEvent[] = [];
  //       data.schedules.forEach((schedule: any) => {
  //         Object.keys(schedule.days).forEach((day) => {
  //           const dayOfWeek = day as DayOfWeek;
  //           schedule.days[day].forEach((classInfo: string) => {
  //             const [title, timeRange] = classInfo.split(": ");
  //             const [startTime, endTime] = timeRange.split(" - ");
  //             newEvents.push({
  //               title, 
  //               start: convertToISODate (dayOfWeek, startTime),
  //               end: convertToISODate(dayOfWeek, endTime),
  //               info: `CRN: ${schedule.crns[title.split("-")[0]]}`,
  //             });
  //           });
  //         });
  //       });
  //       setEvents(newEvents);
  //       setStep(step + 1);
  //       setIsLoading(false);
  //     })
  //     .catch((error) => {
  //       console.error("Error:", error);
  //       setIsLoading(false);
  //     });
  // };

  const handleEventClick = (info: any) => {
    setSelectedEvent({
      title: info.event.title,
      start: info.event.start,
      end: info.event.end,
      info: info.event.extendedProps.info,
    });
    setIsModalOpen(true);
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
        <div className="flex flex-col p-10 min-h-screen">
          <div className="bg-white shadow-xl rounded rounded-xl">
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
              // events={[
              //   {
              //     title: "Example Class 1",
              //     start: "2099-01-05T08:00:00",
              //     end: "2099-01-05T08:50:00",
              //     info: "This is a test event",
              //   },
              //   {
              //     title: "Example Class 2",
              //     start: "2099-01-05T09:05:00",
              //     end: "2099-01-05T09:55:00",
              //     info: "This is a test event",
              //   },
              //   {
              //     title: "Example Class 3",
              //     start: "2099-01-06T09:05:00",
              //     end: "2099-01-06T09:55:00",
              //     info: "This is a test event",
              //   },
              // ]}
              nowIndicator={true}
              height="auto"
              allDayContent=""
              allDaySlot={false}
              slotMinTime={"08:00:00"}
              slotMaxTime={"23:00:00"}
              titleFormat={"MMMM D, YYYY"}
              dayHeaderFormat={"ddd"}
              eventClick={handleEventClick}
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

      {/* Modal */}
      {isModalOpen && selectedEvent && (
        <>
        <Dialog
          open={isModalOpen}
          as="div"
          className="relative z-10 focus:outline-none"
          onClose={close}
        >
          <div className="fixed inset-0 z-10 w-screen overflow-y-auto">
            <div className="flex min-h-full items-center justify-center p-4">
              <DialogPanel
                transition
                className="w-full max-w-md rounded-xl bg-neutral shadow-xl p-6 backdrop-blur-2xl duration-300 ease-out data-[closed]:transform-[scale(95%)] data-[closed]:opacity-0"
              >
                <DialogTitle
                  as="h2"
                  className="font-main text-2xl font-bold mb-4 text-primary"
                >
                  {selectedEvent.title}
                </DialogTitle>
                <p>
                  <strong>Start:</strong> {selectedEvent.start.toString()}
                </p>
                <p>
                  <strong>End:</strong> {selectedEvent.end.toString()}
                </p>
                <p>
                  <strong>Info:</strong> {selectedEvent.info}
                </p>
                <div className="mt-4">
                  <Button
                    className="inline-flex items-center gap-2 rounded-md bg-gray-700 py-1.5 px-3 text-sm/6 font-semibold text-white shadow-inner shadow-white/10 focus:outline-none data-[hover]:bg-gray-600 data-[focus]:outline-1 data-[focus]:outline-white data-[open]:bg-gray-700"
                    onClick={() => setIsModalOpen(false)}
                  >
                    Close
                  </Button>
                </div>
              </DialogPanel>
            </div>
          </div>
        </Dialog>
      </>
      )}
    </div>
  );
}
