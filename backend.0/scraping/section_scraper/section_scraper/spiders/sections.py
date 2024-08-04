import scrapy
from scrapy.http import FormRequest
import environ
from scheduler.models import Subject
import os
import django
from asgiref.sync import sync_to_async
import asyncio

# Setup Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'class_scheduler.settings')
django.setup()

# Load environment variables
env = environ.Env()
environ.Env.read_env()

# subjects = Subject.objects.all()
# for subject in subjects:
#     print(subject.abbreviation)

# connection = connect(
#     host=env('DB_HOST'),
#     user=env('DB_USER'),
#     password=env('DB_PASSWORD'),
#     database=env('DB_NAME')
# )


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
