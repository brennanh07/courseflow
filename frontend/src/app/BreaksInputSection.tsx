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
    <div className="flex justify-center items-center flex-col gap-y-2 my-4">
      <h1 className="font-main text-6xl">Breaks</h1>
      <h4 className="font-main text-xl">
        Set the start and end times for breaks during the day when you
        don&apos;t want classes
      </h4>
      <h4 className="font-main text-xl">
        If no breaks are needed, leave the default start and end times
      </h4>
      <div className="border bg-primary rounded-xl w-fit object-center flex flex-col p-3.5 gap-y-2.5 my-4">
        {breaks.map((breakPeriod, index) => (
          <div className="flex justify-center items-center" key={index}>
            <select
              className="btn bg-accent font-main text-center border-none focus:outline-none focus:ring-2 focus:ring-white hover:bg-secondary hover:text-white focus:bg-secondary focus:text-white"
              value={breakPeriod.startTime}
              onChange={(e) =>
                handleBreakChange(index, "startTime", e.target.value)
              }
            >
              <option className="font-main bg-accent text-black" value="">
                Start Time
              </option>
              {generateTimeOptions().map((time) => (
                <option
                  className="font-main bg-accent text-black"
                  key={time}
                  value={time}
                >
                  {time}
                </option>
              ))}
            </select>
            <span className="mx-4 text-white">to</span>
            <select
              className="btn bg-accent font-main text-center border-none focus:outline-none focus:ring-2 focus:ring-white hover:bg-secondary hover:text-white focus:bg-secondary focus:text-white"
              value={breakPeriod.endTime}
              onChange={(e) =>
                handleBreakChange(index, "endTime", e.target.value)
              }
            >
              <option className="font-main bg-accent text-black" value="">
                End Time
              </option>
              {generateTimeOptions().map((time) => (
                <option
                  className="font-main bg-accent text-black"
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
                className="font-main btn bg-accent text-xl ml-2 text-center border-none hover:bg-secondary hover:text-white"
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
        {breaks.length < 8 && (
          <div className="flex justify-center">
            <button
              onClick={addBreak}
              className="font-main bg-accent btn mr-10 text-lg text-center border-none hover:bg-secondary hover:text-white"
            >
              +
            </button>
          </div>
        )}
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
