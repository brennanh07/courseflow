import React from "react";

/**
 * Represents a break period with start and end times.
 */
interface BreakPeriod {
  startTime: string;
  endTime: string;
}

/**
 * Props for the BreaksInputSection component.
 */
interface BreaksInputSectionProps {
  breaks: BreakPeriod[];
  setBreaks: React.Dispatch<React.SetStateAction<BreakPeriod[]>>;
}

/**
 * BreaksInputSection component allows users to input and manage break periods.
 *
 * @param {BreaksInputSectionProps} props - The component props
 * @returns {JSX.Element} The rendered BreaksInputSection component
 */
export default function BreaksInputSection({
  breaks,
  setBreaks,
}: BreaksInputSectionProps) {
  /**
   * Handles changes to break period input fields.
   *
   * @param {number} index - The index of the break period being modified
   * @param {"startTime" | "endTime"} field - The field being modified
   * @param {string} value - The new value for the field
   */
  const handleBreakChange = (
    index: number,
    field: "startTime" | "endTime",
    value: string
  ) => {
    const newBreaks = [...breaks];
    newBreaks[index] = { ...newBreaks[index], [field]: value };
    setBreaks(newBreaks);
  };

  /**
   * Adds a new empty break period to the list.
   */
  const addBreak = () => {
    if (breaks.length < 8) {
      setBreaks([...breaks, { startTime: "", endTime: "" }]);
    }
  };

  /**
   * Removes a break period from the list.
   *
   * @param {number} index - The index of the break period to remove
   */
  const removeBreak = (index: number) => {
    const newBreaks = breaks.filter((_, i) => i !== index);
    setBreaks(newBreaks);
  };

  return (
    <div className="flex justify-center items-center flex-col my-8 px-4">
      <div className="w-full max-w-4xl p-4 sm:p-6 md:p-8 bg-gray-100 shadow-lg rounded-xl text-center">
        {/* Section Header */}
        <h1 className="font-main text-3xl sm:text-4xl md:text-5xl font-extrabold mb-4 sm:mb-6 text-primary">
          Breaks
        </h1>

        {/* Instructions */}
        <div className="space-y-2 sm:space-y-4 mb-6 sm:mb-8">
          <p className="text-base sm:text-lg mt-2">
            Set break times for when you don&apos;t want classes
          </p>
          <p className="text-xs sm:text-sm mt-2 text-gray-600">
            If no breaks are needed, leave the default start and end times
          </p>
        </div>

        {/* Break Input Form */}
        <div className="bg-primary shadow-xl rounded-lg p-4 sm:p-6">
          <div className="grid grid-cols-1 gap-4 sm:gap-6">
            {breaks.map((breakPeriod, index) => (
              <div
                className="flex justify-center items-center gap-x-4 ml-16 sm:flex-row flex-col sm:gap-4"
                key={index}
              >
                {/* Start time select */}
                <select
                  className="btn bg-accent font-main text-center border-none focus:outline-none focus:ring-2 focus:ring-white hover:bg-secondary hover:text-white focus:bg-secondary focus:text-white w-full sm:w-40 md:w-48 text-base sm:text-lg"
                  value={breakPeriod.startTime}
                  onChange={(e) =>
                    handleBreakChange(index, "startTime", e.target.value)
                  }
                >
                  <option
                    className="font-main bg-accent text-black text-base sm:text-lg"
                    value=""
                  >
                    Start Time
                  </option>
                  {generateTimeOptions().map((time) => (
                    <option
                      className="font-main bg-accent text-black text-base sm:text-lg"
                      key={time}
                      value={time}
                    >
                      {time}
                    </option>
                  ))}
                </select>
                <span className="text-neutral text-lg sm:text-xl">to</span>
                {/* End time select */}
                <select
                  className="btn bg-accent font-main text-center border-none focus:outline-none focus:ring-2 focus:ring-white hover:bg-secondary hover:text-white focus:bg-secondary focus:text-white w-full sm:w-40 md:w-48 text-base sm:text-lg"
                  value={breakPeriod.endTime}
                  onChange={(e) =>
                    handleBreakChange(index, "endTime", e.target.value)
                  }
                >
                  <option
                    className="font-main bg-accent text-black text-base sm:text-lg"
                    value=""
                  >
                    End Time
                  </option>
                  {generateTimeOptions().map((time) => (
                    <option
                      className="font-main bg-accent text-black text-base sm:text-lg"
                      key={time}
                      value={time}
                    >
                      {time}
                    </option>
                  ))}
                </select>
                {/* Remove Break Button */}
                {breaks.length > 1 && index > 0 ? (
                  <button
                    onClick={() => removeBreak(index)}
                    className="font-main btn btn-circle bg-accent text-xl text-center border-none hover:bg-secondary hover:text-white mt-2 sm:mt-0"
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
                  <div className="mt-2 sm:mt-0" style={{ visibility: "hidden" }}>
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

          {/* Add Break Button */}
          {breaks.length < 8 && (
            <div className="flex justify-center mt-4 sm:mt-6">
              <button
                onClick={addBreak}
                className="font-main bg-accent btn btn-circle text-lg text-center border-none hover:bg-secondary hover:text-white"
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

/**
 * Generates an array of time options for the time select dropdowns.
 *
 * @returns {string[]} An array of formatted time strings
 */
function generateTimeOptions() {
  const times = [];
  const startHour = 8; // 8 AM
  const endHour = 22; // 10 PM
  for (let hour = startHour; hour <= endHour; hour++) {
    for (let minute = 0; minute < 60; minute += 15) {
      const formattedHour = hour > 12 ? hour - 12 : hour;
      const period = hour >= 12 ? "PM" : "AM";
      const formattedMinute = minute < 10 ? `0${minute}` : minute;
      const time = `${formattedHour}:${formattedMinute} ${period}`;
      times.push(time);
    }
  }
  return times;
}