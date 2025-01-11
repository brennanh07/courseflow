import React, { useEffect, useState } from "react";

interface ProgressBarProps {
  onComplete: () => void;
}

export const ProgressBar: React.FC<ProgressBarProps> = ({ onComplete }) => {
  const [progress, setProgress] = useState(0);
  const [message, setMessage] = useState(
    "Generating all possible schedules..."
  );

  const messages = [
    { percentage: 0, text: "Generating all possible schedules..." },
    { percentage: 25, text: "Applying break constraints..." },
    { percentage: 50, text: "Applying day and time preferences..." },
    { percentage: 75, text: "Optimizing and ranking schedules..." },
    { percentage: 90, text: "Finalizing your top personalized schedules..." },
  ];

  useEffect(() => {
    const duration = 20000; // 20 seconds
    const interval = 50; // Update every 50ms for smooth animation
    const steps = duration / interval;
    const incrementPerStep = 100 / steps;

    const timer = setInterval(() => {
      setProgress((prev) => {
        const newProgress = Math.min(prev + incrementPerStep, 100);

        // Update message based on progress
        const currentMessage = messages.findLast(
          (m) => newProgress >= m.percentage
        );
        if (currentMessage && currentMessage.text !== message) {
          setMessage(currentMessage.text);
        }

        if (newProgress >= 100) {
          clearInterval(timer);
          setTimeout(onComplete, 500); // Small delay before showing modal
        }

        return newProgress;
      });
    }, interval);

    return () => clearInterval(timer);
  }, [onComplete, message, messages]);

  return (
    <div className="w-full flex flex-col items-center gap-4">
      <progress
        className="progress progress-primary w-96"
        value={progress}
        max="100"
      />
      <p className="text-lg font-main text-gray-700 animate-fade-in">
        {message}
      </p>
    </div>
  );
};
