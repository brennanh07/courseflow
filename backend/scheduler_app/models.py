from django.db import models


# Create your models here.

class Sections(models.Model):
    crn = models.IntegerField()
    class_id = models.IntegerField(foreign_key=True)
    class_type = models.CharField(max_length=100)
    modality = models.CharField(max_length=100)
    credit_hours = models.IntegerField()
    capacity = models.IntegerField()
    professor_id = models.IntegerField(foreign_key=True)
    days = models.CharField(max_length=100)
    begin_time = models.TimeField()
    end_time = models.TimeField()
    location = models.CharField(max_length=100)
    exam_code = models.CharField(max_length=100)
    
    class Meta:
        ordering = ['begin_time']  # Orders by begin_time in ascending order
        verbose_name = 'Class Section'  # Singular name
        verbose_name_plural = 'Class Sections'  # Plural name

    def __str__(self):
        return f"{self.course} - {self.title} by {self.instructor}"

    
class Subjects(models.Model):
    subject_id = models.IntegerField(primary_key=True)
    abbreviation = models.CharField(max_length=100)
    title = models.CharField(max_length=100)
    
    class Meta:
        ordering = ['abbreviation']
        verbose_name = 'Subject'
        verbose_name_plural = 'Subjects'
        
    def __str__(self):
        return f"{self.abbreviation} - {self.title}"
    
    
class Professors(models.Model):
    professor_id = models.IntegerField(primary_key=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    department = models.CharField(max_length=100)
    rating = models.FloatField()
    difficulty_level = models.FloatField()
    would_take_again = models.FloatField()
    
    class Meta:
        ordering = ['last_name']
        verbose_name = 'Professor'
        verbose_name_plural = 'Professors'\
            
    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    
    
# class Courses(models.Model):
#     id = models.IntegerField(primary_key=True)
#     title = models.CharField(max_length=100)
    
#     class Meta:
#         ordering = ['title']
#         verbose_name = 'Course'
#         verbose_name_plural = 'Courses'
    
#     def __str__(self):
#         return f"{self.title}"
    
    
class Users(models.Model):
    user_id = models.IntegerField(primary_key=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    password = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['last_name']
        verbose_name = 'User'
        verbose_name_plural = 'Users'
    
    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    
    
class Preferences(models.Model):
    preferences_id = models.IntegerField(primary_key=True)
    user_id = models.IntegerField(foreign_key=True)
    tod_preference = models.CharField(max_length=100)
    dow_preference = models.CharField(max_length=100)
    
    class Meta:
        verbose_name = 'Preference'
        verbose_name_plural = 'Preferences'
        
    def __str__(self):
        return f"{self.user_id} - {self.tod_preference} - {self.dow_preference}"
    
    
class Weights(models.Model):
    user_id = models.IntegerField(foreign_key=True)
    tod_weight = models.FloatField()
    dow_weight = models.FloatField()
    prof_weight = models.FloatField()
    
    class Meta:
        verbose_name = 'Weight'
        verbose_name_plural = 'Weights'
        
    def __str__(self):
        return f"{self.user_id} - {self.tod_weight} - {self.dow_weight} - {self.prof_weight}"
    
    
class Schedules(models.Model):
    schedule_id = models.IntegerField(primary_key=True)
    user_id = models.IntegerField(foreign_key=True)
    crns = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)
    score = models.FloatField()
    
    class Meta:
        verbose_name = 'Schedule'
        verbose_name_plural = 'Schedules'
        
    def __str__(self):
        return f"{self.user_id} - {self.created_at}"
    
    
class ScheduleLogs(models.Model):
    log_id = models.IntegerField(primary_key=True)
    user_id = models.IntegerField(foreign_key=True)
    crns = models.JSONField()
    score = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Schedule Log'
        verbose_name_plural = 'Schedule Logs'
        
    def __str__(self):
        return f"{self.user_id} - {self.created_at}"
    
    
    
    

    
    
    
