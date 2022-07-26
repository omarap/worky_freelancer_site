from django.contrib import admin

# Register your models here.
from .models import *

admin.site.register([
                     Profile,
                     UsersSkill,
                     UsersCommunicationLanguage,
                     Project,
                     Task,
                     TaskSkillsRequired,
                     TaskLanguagesRequired,
                     Applicant,
                     Selected,
                     Contributor,
                     UserRating,
                     Notification,
                     SavedTask,
                     AppliedTask,
                     Contact,
                     Category
                     ])

class CategoryAdmin(admin.ModelAdmin):
 list_display = ['name', 'slug']
 prepopulated_fields = {'slug': ('name',)}