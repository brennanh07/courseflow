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
    <div>
      <h2>Enter Your Breaks</h2>
      {breaks.map((breakPeriod, index) => (
        <div key={index}>
          <select
            value={breakPeriod.startTime}
            onChange={(e) =>
              handleBreakChange(index, "startTime", e.target.value)
            }
          >
            <option value="">Start Time</option>
            {generateTimeOptions().map((time) => (
              <option key={time} value={time}>
                {time}
              </option>
            ))}
          </select>
          <span className="mr-2">to</span>
          <select
            value={breakPeriod.endTime}
            onChange={(e) =>
              handleBreakChange(index, "endTime", e.target.value)
            }
          >
            <option value="">End Time</option>
            {generateTimeOptions().map((time) => (
              <option key={time} value={time}>
                {time}
              </option>
            ))}
          </select>
            {breaks.length > 1 && index > 0 && (
                <button onClick={() => removeBreak(index)} className="btn">
                    Remove
                </button>
            )}
        </div>
      ))}
      {breaks.length < 8 && (
        <button onClick={addBreak} className="btn">
          Add Break
        </button>
      )}
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
