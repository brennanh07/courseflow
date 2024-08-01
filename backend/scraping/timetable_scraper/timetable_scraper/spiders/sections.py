import scrapy
from scrapy.http import FormRequest
import logging
from scheduler_app.models import Section
from django.utils.dateparse import parse_time
# import os
# import django
# from django.utils.decorators import sync_to_async

# os.environ["DJANGO_SETTINGS_MODULE"] = "backend.class_scheduler.settings"
# django.setup()


class SectionsSpider(scrapy.Spider):
    name = "sections"
    allowed_domains = ["apps.es.vt.edu"]
    start_urls = ["https://apps.es.vt.edu/ssb/HZSKVTSC.P_ProcRequest"]
    
    def start_requests(self):
        # example subjects for testing
        subjects = ["CS", "MATH"]
        
        for subject in subjects:
            yield FormRequest(
                url=self.start_urls[0],
                formdata={
                    'CAMPUS': '0',
                    'TERMYEAR': '202409',
                    'CORE_CODE': '%',
                    'subj_code': subject,
                    'SCHDTYPE': '%',
                    'CRSE_NUMBER': '',
                    'crn': '',
                    'open_only': 'on',
                    'sess_code': '%',
                    'BTN_PRESSED': 'FIND class sections'
                },
                callback=self.parse,
                meta={"subject": subject}
            )
                

    def parse(self, response):
        rows = response.xpath("//table[@class='dataentrytable']/tr[position()>1]")
        classes = []
        for row in rows:
            cells = row.xpath(".//td")
            if len(cells) >= 13:
                crn = int(cells[0].xpath(".//b/text()").get().strip())  # Extract CRN from <b> tag
                course = cells[1].xpath(".//font/text()").get().strip()  # Extract Course from <font> tag
                title = cells[2].xpath(".//text()").get().strip()
                schedule_type = cells[3].xpath(".//text()").get().strip()
                modality = cells[4].xpath(".//text()").get().strip()
                credit_hours = int(cells[5].xpath(".//text()").get().strip())
                capacity = int(cells[6].xpath(".//text()").get().strip())
                professor = cells[7].xpath(".//text()").get().strip()
                days = cells[8].xpath(".//text()").get().strip()
                begin_time = cells[9].xpath(".//text()").get().strip()
                end_time = cells[10].xpath(".//text()").get().strip()
                location = cells[11].xpath(".//text()").get().strip()
                exam_code = cells[12].xpath(".//a/text()").get().strip()
                
                yield {
                    "CRN": crn,
                    "Course": course,
                    "Title": title,
                    "Schedule_Type": schedule_type,
                    "Modality": modality,
                    "Credit_Hours": credit_hours,
                    "Capacity": capacity,
                    "Professor": professor,
                    "Location": location,
                    "Exam_Code": exam_code
                }
                
                # Section.objects.update_or_create(
                #     crn=crn,
                #     course=course,
                #     title=title,
                #     schedule_type=schedule_type,
                #     modality=modality,
                #     credit_hours=credit_hours,
                #     capacity=capacity,
                #     professor=professor,
                #     location=location,
                #     exam_code=exam_code
                # )
                
        #         class_info = {
        #             'CRN': crn,
        #             'Course': course,
        #             'Title': title,
        #             'Schedule_Type': schedule_type,
        #             'Modality': modality,
        #             'Credit_Hours': credit_hours,
        #             'Capacity': capacity,
        #             'Instructor': instructor,
        #             'Days': days,
        #             'Begin_Time': begin_time,
        #             'End_Time': end_time,
        #             'Location': location,
        #             'Exam_Code': exam_code
        #         }
        #         classes.append(class_info)
                
        # print(classes)
            # if "Online: Asynchronous" in class_type:
            #     days, begin_time, end_time, location = "Online", "Online", "Online", "Online"
            # elif days == "(ARR)":
            #     days, begin_time, end_time = "ARR", "ARR", "ARR"
                
            # self.print_section(
            #     crn, course, title, class_type, modality, credit_hours, capacity, professor, days, begin_time, end_time, location, exam_code
            # )
            # self.print_section_time(crn, days, begin_time, end_time)
            
            
    # def print_section(self, crn, course, title, class_type, modality, credit_hours, capacity, professor, location, exam_code):
    #     print({
    #         "CRN": crn,
    #         "Course": course,
    #         "Title": title,
    #         "Class Type": class_type,
    #         "Modality": modality,
    #         "Credit Hours": credit_hours,
    #         "Capacity": capacity,
    #         "Professor": professor,
    #         "Location": location,
    #         "Exam Code": exam_code,
    #     })
        
    
    # def print_section_time(self, crn, days, begin_time, end_time):
    #     print({
    #         "CRN": crn,
    #         "Days": days,
    #         "Begin Time": begin_time,
    #         "End Time": end_time,
    #     })
        
        

