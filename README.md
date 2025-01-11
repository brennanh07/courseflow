# CourseFlow
A full-stack web application that helps Virginia Tech students create optimized class schedules. The system automatically generates conflict-free schedules based on selected courses, break preferences, and preferred class times and days. It scrapes real-time course data from VT's Timetable of Classes and uses an intelligent scoring algorithm to rank schedules according to user preferences. 

Built with NextJS/TypeScript frontend and Django/MySQL backend.

![CourseInput](https://github.com/brennanh07/SmartClass-Scheduler/blob/main/Images/CourseFlow_Course_Input.png?raw=true)

![CourseInputFilter](https://github.com/brennanh07/SmartClass-Scheduler/blob/main/Images/CourseFlow_Course_Input_Filter.png?raw=true)

![BreaksInput](https://github.com/brennanh07/SmartClass-Scheduler/blob/main/Images/CourseFlow_Breaks_Input.png?raw=true)

![PreferencesInput](https://github.com/brennanh07/SmartClass-Scheduler/blob/main/Images/CourseFlow_Preferences_Input.png?raw=true)

## **Frontend**

### **Features**
- **Course Selection:** Input multiple courses using subject codes and course numbers with autocomplete suggestions

- **Break Scheduling:** Add multiple break periods to block out times when you don't want classes

- **Preference Setting:** Set preferred class days and times with customizable weights

- **Interactive calendar:** View generated schedules in a weekly calendar format with detailed class information

- **Schedule navigation:** Browse through multiple generated schedules

- **Real-time Progress Tracking:** Monitor schedule generation progress

### **Tech Stack**
- **NextJS with TypeScript**

- **@fullcalendar/react for calendar visualization**

- **UI Components:**
    - @headlessui/react
    - DaisyUI 

- **Tailwind CSS for styling**

### **Main Components**
1. **Home (page.tsx)**
    - Main application container
    - Manages global state and navigation
    - Handles schedule generation and API communication

2. **CourseInputSection**
    - Manages course input with autocomplete for subjects and course numbers
    - Supports adding/removing courses
    - Validates course inputs

3. **BreaksInputSection**
    - Handles break period inputs
    - Supports multiple break slots
    - Time range selection with validation

4. **PreferencesInputSection**
    - Manages day and time preferences
    - Handles preference weighting
    - Input validation for weights

5. **Layout**
    - Manages the overall theme and layout of every section
    - Handles the header and footer
    - Manages metadata

### Sub Components
1. **NavButton**
    - Turns the logo/icon into a clickable button
    - Reloads the page on click

2. **ProgressBar**
    - Displays the "progress" of schedule generation
    - Activates after clicking the "generate schedules" button

3. **ResultsModal**
    - Modal that displays the total amount of schedules generated based on user input
    - Shows the top "x" that will be shown after filtering
    - Activates after:
        - The GET request comes back from the API
        - The progress bar component finishes loading\

## **Backend**
A Django-based backend system for generating optimized schedules based on user preferences and constraints. The system scrapes course data from Virginia Tech's Banner system, processes it, and provides an API for generating conflict-free schedules that align with user preferences.

### **Features**
- **Course Data Management**
    - Automated scraping of course sections from VT Timetable of Classes
    - Storage of course sections, professors, and grade distributions
    - Tracking of both open and closed sections

- **Schedule Generation**
    - Intelligent schedule generation using depth-first search
    - Conflict detection and resolution
    - Support for break periods and time constraints
    - Customizable scheduling preferences
    - Schedule scoring based on:
        - Time preferences (morning/afternoon/evening)
        - Day preferences
        - Grade distributions
    
- **API Endpoints**
    - Schedule generation endpoint
    - Course and section information retrieval
    - Support for user preferences and constraints

### Tech Stack
- **Django with Python**

- **MySQL Database**

- **Scrapy for web crawling**

### **Main Components**

#### **Schedule Generator**
- Implements depth-first search for schedule generation
- Uses a heap-based priority queue for maintaining top schedules
- Handles time conflicts and break periods
- Supports various scheduling constraints

#### **Schedule Scorer**
- Scores schedules based on user preferences
- Implements sophisticated time-based scoring
- Considers day distribution
- Uses exponential decay for time preference scoring

#### **Section Fetcher**
- Efficiently fetches course sections from the database
- Handles section time relationships
- Optimizes database queries using Django's ORM

#### **Sections Spider**
- Scrapes course data from the VT Timetable of Classes
- Handles multiple section types
- Processes and stores class grade distribution history
- Updates database efficiently using batch operations