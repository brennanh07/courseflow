import React from 'react';

interface Schedule {
    courses: {
        courseName: string;
        day: string;
        startTime: string;
        endTime: string;
    }[];
}

// const ScheduleDisplay: React.FC<{ schedules: Schedule[] }> = ({ schedules }) => {
//     return (
//         <div>
//             {schedules.map((schedule, index) => (
//                 <div key={index}>
//                     <h2>Schedule {index + 1}</h2>\
//                     <ul

//         </div>
//     )