import scrapy
from scrapy.http import FormRequest
from scheduler.models import Subject, Section, SectionTime
import os
import django
from asgiref.sync import sync_to_async
import asyncio

# Setup Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'class_scheduler.settings')
django.setup()


class SectionsSpider(scrapy.Spider):
    name = "sections"
    allowed_domains = ["apps.es.vt.edu"]
    start_urls = ["https://apps.es.vt.edu/ssb/HZSKVTSC.P_ProcRequest"]
    
    def start_requests(self):
        subjects = asyncio.run(self.get_subjects())
        return self.make_requests(subjects)
    
    async def get_subjects(self):
        subjects = await sync_to_async(list)(Subject.objects.values_list('abbreviation', flat=True))
        return subjects
        
    def make_requests(self, subjects):
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
                    'BTN_PRESSED': 'FIND class sections',
                    'disp_comments_in' : 'N'
                },
                callback=self.parse,
                meta={"subject": subject}
            )
                

    def parse(self, response):
        rows = response.xpath("//table[@class='dataentrytable']/tr[position()>1]")
        for row in rows:
            cells = row.xpath(".//td")
            if len(cells) == 10:
                yield from self.parse_additional_time(cells)
            elif len(cells) == 12 and cells[4].xpath(".//text()").get().strip() == "Online: Asynchronous":
                yield from self.parse_online_asynchronous(cells)
            elif len(cells) == 13:
                yield from self.parse_regular(cells)
            else:
                yield from self.parse_arranged(cells)
                
    def parse_additional_time(self, cells):
        crn = getattr(self, "current_crn", None)
        days = cells[5].xpath(".//text()").get().strip()
        begin_time = cells[6].xpath(".//text()").get().strip()
        end_time = cells[7].xpath(".//text()").get().strip()
        
        section_time_data = {
            "CRN": crn,
            "Days": days,
            "Begin_Time": begin_time,
            "End_Time": end_time
        }
        
        yield section_time_data
                
    def parse_regular(self, cells):
        self.current_crn = int(cells[0].xpath(".//b/text()").get().strip())  # Extract CRN from <b> tag
        course = cells[1].xpath(".//font/text()").get().strip()  # Extract Course from <font> tag
        title = cells[2].xpath(".//text()").get().strip()
        class_type = cells[3].xpath(".//text()").get().strip()
        modality = cells[4].xpath(".//text()").get().strip()
        credit_hours = int(cells[5].xpath(".//text()").get().strip())
        capacity = int(cells[6].xpath(".//text()").get().strip())
        professor = cells[7].xpath(".//text()").get().strip()
        days = cells[8].xpath(".//text()").get().strip()
        begin_time = cells[9].xpath(".//text()").get().strip()
        end_time = cells[10].xpath(".//text()").get().strip()
        location = cells[11].xpath(".//text()").get().strip()
        exam_code = cells[12].xpath(".//a/text()").get().strip()
        
        section_data = {
            "CRN": self.current_crn,
            "Course": course,
            "Title": title,
            "Class_Type": class_type,
            "Modality": modality,
            "Credit_Hours": credit_hours,
            "Capacity": capacity,
            "Professor": professor,
            "Location": location,
            "Exam_Code": exam_code
        }     
        
        section_time_data = {
            "CRN": self.current_crn,
            "Days": days,
            "Begin_Time": begin_time,
            "End_Time": end_time
        }
        
        yield section_data
        yield section_time_data
                
    def parse_online_asynchronous(self, cells):
        self.current_crn = int(cells[0].xpath(".//b/text()").get().strip())  
        course = cells[1].xpath(".//font/text()").get().strip()  
        title = cells[2].xpath(".//text()").get().strip()
        class_type = cells[3].xpath(".//text()").get().strip()
        modality = cells[4].xpath(".//text()").get().strip()
        credit_hours = int(cells[5].xpath(".//text()").get().strip())
        capacity = int(cells[6].xpath(".//text()").get().strip())
        professor = cells[7].xpath(".//text()").get().strip()
        days = "ONLINE"
        begin_time = "ONLINE"
        end_time = "ONLINE"
        location = cells[10].xpath(".//text()").get().strip()
        exam_code = cells[11].xpath(".//a/text()").get().strip()
        
        section_data = {
            "CRN": self.current_crn,
            "Course": course,
            "Title": title,
            "Class_Type": class_type,
            "Modality": modality,
            "Credit_Hours": credit_hours,
            "Capacity": capacity,
            "Professor": professor,
            "Location": location,
            "Exam_Code": exam_code
        }
        
        section_time_data = {
            "CRN": self.current_crn,
            "Days": days,
            "Begin_Time": begin_time,
            "End_Time": end_time
        }
        
        yield section_data
        yield section_time_data
                
    def parse_arranged(self, cells):
        self.current_crn = int(cells[0].xpath(".//b/text()").get().strip())  
        course = cells[1].xpath(".//font/text()").get().strip()  
        title = cells[2].xpath(".//text()").get().strip()
        class_type = cells[3].xpath(".//text()").get().strip()
        modality = cells[4].xpath(".//text()").get().strip()
        credit_hours = int(cells[5].xpath(".//text()").get().strip())
        capacity = int(cells[6].xpath(".//text()").get().strip())
        professor = cells[7].xpath(".//text()").get().strip()
        days = "ARR"
        begin_time = "ARR"
        end_time = "ARR"
        location = cells[10].xpath(".//text()").get().strip()
        exam_code = cells[11].xpath(".//a/text()").get().strip()
        
        section_data = {
            "CRN": self.current_crn,
            "Course": course,
            "Title": title,
            "Class_Type": class_type,
            "Modality": modality,
            "Credit_Hours": credit_hours,
            "Capacity": capacity,
            "Professor": professor,
            "Location": location,
            "Exam_Code": exam_code
        }
        
        section_time_data = {
            "CRN": self.current_crn,
            "Days": days,
            "Begin_Time": begin_time,
            "End_Time": end_time
        }
        
        yield section_data
        yield section_time_data
                
                
    # def save_to_db(self, item):
    #     # Delete all existing data in section and section_time tables
    #     Section.objects.all().delete()
    #     SectionTime.objects.all().delete()
        
    #     # Bulk create new data
    #     Section.objects.bulk_create(self.sections_data)
    #     SectionTime.objects.bulk_create(self.section_times_data)
        

                
