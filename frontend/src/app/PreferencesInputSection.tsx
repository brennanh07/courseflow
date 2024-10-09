import React, { ChangeEvent, useEffect } from "react";

interface Preferences {
  days: string[];
  timesOfDay: string;
  dayWeight: number;
  timeWeight: number;
}

interface PreferencesInputSectionProps {
  preferences: Preferences;
  setPreferences: React.Dispatch<React.SetStateAction<Preferences>>;
}

export default function PreferencesInputSection({
  preferences,
  setPreferences,
}: PreferencesInputSectionProps) {
  useEffect(() => {
    if (!preferences.timesOfDay) {
      setPreferences((prev) => ({
        ...prev,
        timesOfDay: "morning",
      }));
    }
  }, [preferences.timesOfDay, setPreferences]);
  const handleDayChange = (day: string, checked: boolean) => {
    const updatedDays = checked
      ? [...preferences.days, day]
      : preferences.days.filter((d) => d !== day);

    setPreferences((prev) => ({
      ...prev,
      days: updatedDays,
    }));
  };

  const handleTimeChange = (event: ChangeEvent<HTMLSelectElement>) => {
    const selectedValue = event.target.value;
    console.log("Selected Time of Day:", selectedValue); // Debugging line

    setPreferences((prev) => ({
      ...prev,
      timesOfDay: selectedValue,
    }));
  };

  const handleDayWeightChange = (weight: number) => {
    setPreferences((prev) => ({
      ...prev,
      dayWeight: weight,
    }));
  };

  const handleTimeWeightChange = (weight: number) => {
    setPreferences((prev) => ({
      ...prev,
      timeWeight: weight,
    }));
  };

  return (
    <div className="flex space-x-20 w-100 max-w-8xl p-8 bg-neutral shadow-lg rounded-xl text-center my-8">
      <div className="flex flex-col space-y-4">
        {/* Preferences Header */}
        <h1 className="font-main text-5xl font-extrabold mb-6 text-primary">
          Preferences
        </h1>

        <div className="flex flex-col gap-y-4 border bg-primary rounded-xl p-3.5">
          <div className="flex flex-col gap-y-2 items-center">
            <h2 className="text-3xl text-accent">Class Days</h2>
            <p className="text-sm mt-2 text-secondary">
              Which days of the week would you prefer to have class on?
            </p>
            <div className="flex flex-col text-accent">
              {["M", "T", "W", "R", "F"].map((day) => (
                <label className="flex items-center my-1 text-2xl" key={day}>
                  <input
                    type="checkbox"
                    checked={preferences.days.includes(day)}
                    onChange={(e) => handleDayChange(day, e.target.checked)}
                    className="checkbox checkbox-lg checkbox-secondary [--chkfg:white]"
                  />
                  <span className="ml-2">{day}</span>
                </label>
              ))}
            </div>
          </div>

          <div className="flex flex-col gap-y-2">
            <h2 className="text-3xl text-center text-accent">Time of Day</h2>
            <p className="text-sm mt-2 text-secondary">
              What time of day would you prefer to have class?
            </p>
            <select
              className="btn w-full bg-accent text-center border-none focus:outline-none focus:ring-2 focus:ring-white hover:bg-secondary hover:text-white focus:bg-secondary focus:text-white text-lg my-2"
              value={preferences.timesOfDay}
              onChange={handleTimeChange}
            >
              <option
                className="font-main bg-accent text-black text-center"
                value="morning"
              >
                Morning (8:00 AM - 12:00 PM)
              </option>
              <option
                className="font-main bg-accent text-black"
                value="afternoon"
              >
                Afternoon (12:00 PM - 4:00 PM)
              </option>
              <option
                className="font-main bg-accent text-black"
                value="evening"
              >
                Evening (4:00 PM - 8:00 PM)
              </option>
            </select>
          </div>
        </div>
      </div>

      <div className="flex flex-col space-y-4">
        <h1 className="font-main text-5xl font-extrabold mb-6 text-primary">
          Weighting
        </h1>
        <div className="flex flex-col gap-y-4 border bg-primary rounded-xl p-3.5 py-5">
          <p className="text-secondary text-center">
            Weighting determines how much each preference will factor into the
            schedule generation process
          </p>
          <p className="text-secondary text-center">
            If you want a preference to have no effect, set it to 0.0
          </p>
          <div className="flex flex-col gap-y-2 items-center">
            <h2 className="text-accent text-3xl my-2">Class Days Weight</h2>
            <input
              type="number"
              value={preferences.dayWeight}
              min="0"
              max="1"
              step="0.05"
              onChange={(e) =>
                handleDayWeightChange(parseFloat(e.target.value))
              }
              className="input w-full max-w-xs text-center text-xl border-none focus:outline-none focus:ring-4 focus:ring-secondary"
            />
          </div>
          <div className="flex flex-col gap-y-2 items-center my-2">
            <h2 className="text-accent text-3xl my-2">Time of Day Weight</h2>
            <input
              type="number"
              value={preferences.timeWeight}
              min="0"
              max="1"
              step="0.05"
              onChange={(e) =>
                handleTimeWeightChange(parseFloat(e.target.value))
              }
              className="input w-full max-w-xs text-center text-xl border-none focus:outline-none focus:ring-4 focus:ring-secondary"
            />
          </div>
          <p className="text-secondary text-center">*WEIGHTS MUST ADD TO 1.0</p>
        </div>
      </div>
    </div>
  );
}
