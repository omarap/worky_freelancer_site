from django.db import models
from accounts.models import CustomUser
from django.urls import reverse
from django.utils import timezone
from autoslug import AutoSlugField 
from django.core.validators import validate_email
from django.core.exceptions import ValidationError 
import os

CHOICES = (
    ("None", "None"), 
    ("UG-1", "UnderGraduate 1st year"), 
    ("UG-2","UnderGraduate 2nd year"), 
    ("UG-3", "UnderGraduate 3rd year"), 
    ("UG-4", "UnderGraduate 4th year"), 
    ("MS", "MS"),
    ("Ph.D", "Ph.D")
)


def custom_validate_email(value):
        if "@gmail.com" in value: 
            return value
        elif "@yahoo.com" in value:
            return value
        else:
            raise ValidationError("This field accepts mail ids of google and yahoo only") 


class Profile(models.Model):
    user = models.OneToOneField(
        CustomUser, on_delete=models.CASCADE, related_name='profile', null=True, blank=True, default=None)
    phone_number = models.CharField(null=True, max_length=11, default=None)
    bio = models.TextField(null=True, max_length=500, default=None)
    profile_picture = models.ImageField(upload_to='profiles/', null=True, blank=True, default='1.jpg')
    batchYear = models.CharField(max_length=4, choices=CHOICES, default='None',null=True)
    gender = models.CharField(max_length=10, choices=(
        ("Male", "Male"), ("Female", "Female")), default="Male", blank=False, null=True)
    slug = AutoSlugField(populate_from='user', unique=True)



    def get_absolute_url(self):
           return reverse('portal:my-profile', args=[str(self.id)])

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

    def __str__(self):
        return self.user.username


class UsersSkill(models.Model):
    skill_name = models.CharField(max_length=200, blank=False, unique=False,default=None)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True, blank=True, default=None)
    level_of_proficiency = models.IntegerField(default=1)

    def __str__(self):
        return str(self.skill_name) + "/" + str(self.level_of_proficiency)

    def get_absolute_url(self):
        return reverse('portal:my-profile', args=[str(self.id)])


   

class UsersCommunicationLanguage(models.Model):
    language_name = models.CharField(max_length=100, blank=False, default='English')
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True, blank=True, default=None)
    level_of_fluency = models.IntegerField(default=1)

    def __str__(self):
        return str(self.language_name) + "/" + str(self.level_of_fluency)

    def get_absolute_url(self):
           return reverse('portal:my-profile', args=[str(self.id)])

class Category(models.Model):
    name = models.CharField(max_length=200, db_index=True)
    description = models.TextField(max_length=200)
    slug = models.SlugField(max_length=200,unique=True)

    class Meta:
        verbose_name = 'category'
        verbose_name_plural = 'categories'

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('portal:project_list_by_category', args=[self.slug])


class Project(models.Model):
    project_name = models.CharField(max_length=100, blank=False)
    company = models.CharField(max_length=200, blank=True)
    location = models.CharField(max_length=255, blank=True)
    category = models.ForeignKey(Category, related_name='projects', on_delete=models.CASCADE)
    description = models.TextField(max_length=500)
    available = models.BooleanField(default=True)
    postedOn = models.DateTimeField(auto_now_add=True, blank=True)
    leader = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    isCompleted = models.BooleanField(default=False)
    slug = AutoSlugField(populate_from='project_name', unique=True, null=True)
    is_approved = models.BooleanField(default=False)
    deadline = models.DateField(blank=False, default=None)
    task_count = models.IntegerField(default=0)

    def __str__(self):
        return self.project_name


    def get_absolute_url(self):
           return reverse('portal:project_description', args=[str(self.id)])


class Task(models.Model):
    task_name = models.CharField(max_length=50, blank=False)
    addedOn = models.DateTimeField(auto_now_add=True, blank=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    credits = models.CharField(max_length=20, choices=(("Paid", "Paid"), ("Other", "Other")), blank=False,
                               default="Paid")
    rating = models.DecimalField(default=0, max_digits=2, decimal_places=1)
    mention = models.CharField(max_length=200, blank=True, null=True)
    amount = models.IntegerField(default=0)
    task_description = models.TextField(max_length=200, default=None)
    task_link = models.URLField(blank=True, null=True)
    latest_submission_time = models.DateTimeField(blank=True, null=True)
    isCompleted = models.BooleanField(default=False)
    deadline = models.DateField(blank=False, default=None)
    slug = AutoSlugField(populate_from='task_name', unique=True, null=True)

    def __str__(self):
        return self.task_name

    def get_absolute_url(self):
        return reverse('portal:task_description', args=[str(self.id)])




class TaskSkillsRequired(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    skill_name = models.ForeignKey(UsersSkill, on_delete=models.CASCADE)
    proficiency_level_required = models.IntegerField(1)

    def __str__(self):
        return str(self.skill_name)

    def get_absolute_url(self):
        return reverse('portal:myprojects', args=[str(self.id)])


class TaskLanguagesRequired(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    language_name = models.ForeignKey(UsersCommunicationLanguage, on_delete=models.CASCADE)
    fluency_level_required = models.IntegerField(1)

    def __str__(self):
        return str(self.language_name)

    def get_absolute_url(self):
        return reverse('portal:task_description', args=[str(self.id)])



class Applicant(models.Model):
    applicant = models.OneToOneField(CustomUser, related_name='applicants',on_delete=models.CASCADE,primary_key=True)
    task = models.ForeignKey(Task, related_name='applied', on_delete=models.CASCADE)
    time_of_application = models.DateTimeField(auto_now_add=True, blank=True)

    def __str__(self):
        return self.task.task_name

    def get_absolute_url(self):
        return "/applicant/{}".format(self.id)


class Selected(models.Model):
    task = models.ForeignKey(Task, related_name='select_task',default=None, on_delete=models.CASCADE)
    applicant = models.ForeignKey(CustomUser, related_name='select_applicant', on_delete=models.CASCADE)
    date_posted = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.task.task_name

    def get_absolute_url(self):
        return "/select_applicant/{}".format(self.slug)

class SavedTask(models.Model):
    task = models.ForeignKey(
        Task, related_name='saved_task', on_delete=models.CASCADE)
    user = models.ForeignKey(
        CustomUser, related_name='saved', on_delete=models.CASCADE)
    date_posted = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.task.task_name

    def get_absolute_url(self):
        return reverse('portal:task', args=[str(self.id)])

class AppliedTask(models.Model):
    task = models.ForeignKey(Task, related_name='applied_task', on_delete=models.CASCADE)
    user = models.ForeignKey( CustomUser, related_name='applied_user', on_delete=models.CASCADE)
    date_posted = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.task.task_name
        
    def get_absolute_url(self):
        return reverse('portal:applied-tasks', args=[str(self.id)])
    


class Contributor(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    isCreditVerified = models.BooleanField(default=False)
    time_of_selection = models.DateTimeField(auto_now_add=True, blank=True)

    def __str__(self):
        return str(self.user)

    def get_absolute_url(self):
        return reverse('portal:task_description', args=[str(self.id)])


class UserRating(models.Model):
    task = models.OneToOneField(Task, on_delete=models.CASCADE)
    emp = models.ForeignKey(
        CustomUser, related_name='rating_by', on_delete=models.CASCADE)
    fre = models.ForeignKey( CustomUser, related_name='rating_to', on_delete=models.CASCADE)
    f_rating = models.DecimalField(default=0, max_digits=2, decimal_places=1)
    e_rating = models.DecimalField(default=0, max_digits=2, decimal_places=1)

    def __str__(self):
        return str(self.task.id)+"--"+str(self.fre)+"--"+str(self.emp)

class Notification(models.Model):
    _from = models.ForeignKey(
        CustomUser, related_name="msgfrom", on_delete=models.CASCADE)
    _to = models.ForeignKey(
        CustomUser, related_name='msgto', on_delete=models.CASCADE)
    message = models.CharField(default=None, max_length=300)
    has_read = models.BooleanField(default=False)
    sending_time = models.DateTimeField(auto_now_add=True, blank=True)
    recieving_time = models.DateTimeField(default=None, blank=True, null=True)

class Contact(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(max_length=100, validators=[validate_email, custom_validate_email])
    message = models.TextField(max_length=400)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"