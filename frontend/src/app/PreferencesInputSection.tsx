import React, { ChangeEvent } from "react";

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
    setPreferences((prev) => ({
      ...prev,
      timesOfDay: event.target.value,
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
    <div>
      <h2>Preferences</h2>

      <div>
        <h3>Preferred Days</h3>
        {["M", "T", "W", "R", "F"].map((day) => (
          <label key={day}>
            <input
              type="checkbox"
              checked={preferences.days.includes(day)}
              onChange={(e) => handleDayChange(day, e.target.checked)}
              className="checkbox"
            />
            {day}
          </label>
        ))}
      </div>

      <div>
        <h3>Preferred Time of Day</h3>
        <select value={preferences.timesOfDay} onChange={handleTimeChange}>
          <option value="Morning">Morning</option>
          <option value="Afternoon">Afternoon</option>
          <option value="Evening">Evening</option>
        </select>
      </div>

      <div>
        <h2>Weights</h2>
        <div>
          <label>Day Weight</label>
          <input
            type="number"
            value={preferences.dayWeight}
            min="0"
            max="1"
            step="0.05"
            onChange={(e) => handleDayWeightChange(parseFloat(e.target.value))}
            className="input input-bordered w-full max-w-xs"
          />
        </div>
        <div>
          <label>Time Weight</label>
          <input
            type="number"
            value={preferences.timeWeight}
            min="0"
            max="1"
            step="0.05"
            onChange={(e) => handleTimeWeightChange(parseFloat(e.target.value))}
            className="input input-bordered w-full max-w-xs"
          />
        </div>
      </div>
    </div>
  );
}
