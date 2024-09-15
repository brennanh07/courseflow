import React from "react";

interface BreakPeriod {
  startTime: string;
  endTime: string;
}

interface BreaksInputSectionProps {
  breaks: BreakPeriod[];
  setBreaks: React.Dispatch<React.SetStateAction<BreakPeriod[]>>;
}

export default function BreaksInputSection({
  breaks,
  setBreaks,
}: BreaksInputSectionProps) {
  const handleBreakChange = (
    index: number,
    field: "startTime" | "endTime",
    value: string
  ) => {
    const newBreaks = [...breaks];
    newBreaks[index] = { ...newBreaks[index], [field]: value };
    setBreaks(newBreaks);
  };

  const addBreak = () => {
    if (breaks.length < 8) {
      setBreaks([...breaks, { startTime: "", endTime: "" }]);
    }
  };

  const removeBreak = (index: number) => {
    const newBreaks = breaks.filter((_, i) => i !== index);
    setBreaks(newBreaks);
  };

  return (
    <div className="flex justify-center items-center flex-col my-8 px-4">
      <div className="w-full max-w-4xl p-8 bg-gray-100 shadow-lg rounded-xl text-center">
        {/* Section Header */}
        <h1 className="font-main text-5xl font-extrabold mb-6 text-primary">
          Breaks
        </h1>

        {/* Instructions */}
        <div className="space-y-4 mb-8">
          <p className="text-lg mt-2">
            Set break times for when you don&apos;t want classes
          </p>
          <p className="text-sm mt-2 text-gray-600">
            If no breaks are needed, leave the default start and end times
          </p>
        </div>

        {/* Break Input Form */}
        <div className="bg-primary shadow-xl rounded-lg p-6">
          <div className="grid grid-cols-1 gap-6">
            {breaks.map((breakPeriod, index) => (
              <div
                className="flex justify-center items-center gap-x-4 ml-16"
                key={index}
              >
                <select
                  className="btn bg-accent font-main text-center border-none focus:outline-none focus:ring-2 focus:ring-white hover:bg-secondary hover:text-white focus:bg-secondary focus:text-white w-48 text-lg"
                  value={breakPeriod.startTime}
                  onChange={(e) =>
                    handleBreakChange(index, "startTime", e.target.value)
                  }
                >
                  <option
                    className="font-main bg-accent text-black text-lg"
                    value=""
                  >
                    Start Time
                  </option>
                  {generateTimeOptions().map((time) => (
                    <option
                      className="font-main bg-accent text-black text-lg"
                      key={time}
                      value={time}
                    >
                      {time}
                    </option>
                  ))}
                </select>
                <span className="text-neutral text-xl mx-2">to</span>
                <select
                  className="btn bg-accent font-main text-center border-none focus:outline-none focus:ring-2 focus:ring-white hover:bg-secondary hover:text-white focus:bg-secondary focus:text-white w-48 text-lg"
                  value={breakPeriod.endTime}
                  onChange={(e) =>
                    handleBreakChange(index, "endTime", e.target.value)
                  }
                >
                  <option
                    className="font-main bg-accent text-black text-lg"
                    value=""
                  >
                    End Time
                  </option>
                  {generateTimeOptions().map((time) => (
                    <option
                      className="font-main bg-accent text-black text-lg"
                      key={time}
                      value={time}
                    >
                      {time}
                    </option>
                  ))}
                </select>
                {breaks.length > 1 && index > 0 ? (
                  <button
                    onClick={() => removeBreak(index)}
                    className="font-main btn btn-circle bg-accent text-xl ml-2 text-center border-none hover:bg-secondary hover:text-white"
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

          {/* Add Break Button */}
          {breaks.length < 8 && (
            <div className="flex justify-center mt-6 mr-2">
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
