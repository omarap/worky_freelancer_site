from django.urls import path
from . import views 
from .views import (ProjectView, TaskView, 
    UsersSkillView, UsersCommunicationLanguageView,
    TaskLanguagesView, ContributorView, ThanksView,
    UseratingView, NotificationView, ContactView, thanks
    )
from django.conf import settings 
from django.conf.urls.static import static

app_name = 'portal'

urlpatterns = [
    path('', views.home, name='home'),
    path('privacy-policy/', views.privacy, name='privacy-policy'),
    path('terms-of-service/', views.terms, name='terms-of-service'),
    path('pricing/', views.pricing, name='pricing'),
    path('check_username/', views.check_username, name='check_username'),
    path('check_email/', views.check_email, name='check_email'),
    path('auth/callback/<token>', views.auth_callback_token, name='login_iiits'),
    path('open_close_project/', views.open_close_project,name="open_close_project"),
    path('browse_jobs/', views.browse_jobs, name='browse_jobs'),
    path('jobs_update/', views.jobs_update, name='jobs_update'),
    path('form_state/', views.form_state, name='form_state'),
    path('post_project/', ProjectView.as_view(), name='post_project'),
    path('myprojects/<int:project_id>/edit_project', views.edit_project, name='edit-project'),
    path('myprojects/', views.myprojects, name="myprojects"),
    path('myprojects/<int:project_id>/', views.project_description, name='project_description'),
    path('<int:project_id>/add_task/', TaskView.as_view(), name='add_task'),
    path('<int:project_id>/task_description/<int:task_id>/', views.task_description, name='task_description'),
    path('task-skills/', views.task_skill, name='task-skills'),
    path('task-languages/', TaskLanguagesView.as_view(),  name='task-languages'),
    path('<int:project_id>/task_description/<int:task_id>/apply/', views.applyTask, name='apply'),
    path('thanks/', ThanksView.as_view(), name='thanks'),
    path('contributor/', ContributorView.as_view(), 
        name='contributor'),
    path('<int:project_id>/task_description/<int:task_id>/user-rating/', UseratingView.as_view(), 
        name='user-rating'),
    path('<int:project_id>/task_edit/<int:task_id>/', views.task_editfunction, name='task_edit'),
    path('profile/notification', NotificationView.as_view(), name='notification'),
    path('profile/', views.user_profile, name="my-profile"),
    path('profile/edit/', views.edit_profile, name='edit-profile'),
    path('profile_view/<int:profile_id>/', views.profile_view, name='profile_description'),
    path('profile/add-skill', UsersSkillView.as_view(), name="add-skill"),
    path('profile/edit-skill', views.edit_userskills, name='edit-skill'),
    path('profile/add-language', UsersCommunicationLanguageView.as_view(), name="add-language"),
    path('profile/edit-language', views.edit_userlanguage, name="edit-language"),
    path('applicants/<int:task_id>/', views.applicants,name="applicants"),
    path('applied_task_list/', views.applied_tasks, name='applied-tasks'),
    path('task/<slug>/save/', views.save_task, name='save-task'),
    path('saved_task_list/', views.saved_tasks, name='saved-tasks'),
    path('task/<int:task_id>', views.saved_task_details, name='saved-tasks_details'),
    path('task/<int:task_id>', views.applied_task_details, name='task_detail'),
    path('task/<slug>/selected', views.selected_list, name='selected-list'),
    path('task/<task_id>/select-applicant/<can_id>/', views.select_applicant, name='select-applicant'),
    path('task/<task_id>/remove_applicant-applicant/<can_id>/', views.remove_applicant, name='remove-applicant'),

    path("contact/", ContactView.as_view(), name="contact"),
    path("contact_thanks/", views.thanks, name="contact_thanks"),

    path('project_list/', views.project_list, name='project_list'),
    path('projects/', views.projects, name='projects'),
    path('<slug:category_slug>/', views.project_list, name='project_list_by_category'),


] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
