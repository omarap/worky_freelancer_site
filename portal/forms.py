from django.forms import ModelForm
from django.forms import Textarea
from .models import (Profile,Project, Task,
                     UsersSkill,
                     UsersCommunicationLanguage,
                     TaskSkillsRequired,
                     TaskLanguagesRequired,
                     Applicant,
                     Contributor,
                     UserRating,
                     Notification, Contact) 



class ProfileUpdateForm(ModelForm):
    class Meta:
        model = Profile
        fields = fields = ['phone_number','bio', 'profile_picture', 'batchYear', 'gender']



class ProjectForm(ModelForm):
    class Meta:
        model = Project
        fields = ['project_name', 'description','category','leader', 'isCompleted', 'deadline', 'task_count']


class TaskForm(ModelForm):
    class Meta:
        model = Task
        fields = '__all__'

class UsersSkillForm(ModelForm):
    class Meta:
        model = UsersSkill
        fields = ['skill_name', 'level_of_proficiency']


class UsersCommunicationLanguageForm(ModelForm):
    class Meta:
        model = UsersCommunicationLanguage
        fields = ['language_name', 'level_of_fluency']



class TaskSkillsRequiredForm(ModelForm):
    class Meta:
        model = TaskSkillsRequired
        fields = '__all__'

class TaskLanguagesRequiredForm(ModelForm):
    class Meta:
        model = TaskLanguagesRequired
        fields = '__all__'

class ApplicantForm(ModelForm):
    class Meta:
        model = Applicant
        fields =  ['applicant', 'task']

class ContributorForm(ModelForm):
    class Meta:
        model = Contributor
        fields = '__all__'


class UserRatingForm(ModelForm):
    class Meta:
        model = UserRating
        fields = '__all__'


class NotificationForm(ModelForm):
    class Meta:
        model = Notification
        fields = '__all__'


class ContactForm(ModelForm):
    class Meta:
        model = Contact
        fields = ["first_name", "last_name","email", "message"]
        widgets = {
            "message": Textarea(
                attrs={
                    "placeholder": "Talk to us here"
                }
            )
        }
