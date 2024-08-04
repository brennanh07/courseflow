from scheduler_app.models import Subject
from django.conf import settings

def get_subjects():
    subjects = Subject.objects.values_list("abbreviation", flat=True)

    return subjects

print(get_subjects())


