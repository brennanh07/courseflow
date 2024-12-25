import React from "react";
import { Dialog } from "@headlessui/react";

interface ResultsModalProps {
  isOpen: boolean;
  onClose: () => void;
  totalSchedules: number;
  onViewSchedules: () => void;
}

export const ResultsModal: React.FC<ResultsModalProps> = ({
  isOpen,
  onClose,
  totalSchedules,
  onViewSchedules,
}) => {
  return (
    <Dialog open={isOpen} onClose={onClose} className="relative z-10">
      <div className="fixed inset-0 bg-black/30" aria-hidden="true" />
      <div className="fixed inset-0 flex items-center justify-center p-4">
        <Dialog.Panel className="w-full max-w-md rounded-xl bg-white p-6 shadow-xl">
          <Dialog.Title className="text-3xl font-extrabold mb-6 text-primary font-main text-center">
            Schedules Generated!
          </Dialog.Title>
          <p className="mb-4 text-lg text-center text-secondary">
            Based on your courses, we generated
          </p>
          <p className="text-4xl font-semibold text-center text-black mb-3">
            {totalSchedules}
          </p>
          <p className="mb-6 text-2xl text-center text-primary">
            Possible Schedules
          </p>
          <p className="mb-8 text-md text-center text-gray-600">
            All ranked to match your preferences
          </p>
          <div className="flex justify-end gap-4">
            <button
              className="btn btn-primary px-6 py-2 text-white rounded-lg shadow-lg hover:bg-primary-dark transition duration-150 ease-in-out"
              onClick={() => {
                onViewSchedules();
                onClose();
              }}
            >
              View My Top 10 Schedules
            </button>
          </div>
        </Dialog.Panel>
      </div>
    </Dialog>
  );
};
