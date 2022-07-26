import json
from django.contrib.auth import login, authenticate, logout
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render, reverse, redirect, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from .models import *
from django.contrib.auth.models import User
from datetime import datetime

from django.db import connection

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from django.views.generic import TemplateView, CreateView
from .forms import ( ProjectForm,TaskForm,UsersSkillForm, 
    UsersCommunicationLanguageForm,
    TaskSkillsRequiredForm,
    TaskLanguagesRequiredForm, ApplicantForm, ContributorForm, 
    UserRatingForm, NotificationForm, ProfileUpdateForm, ContactForm)
from .models import *
from django.core.paginator import Paginator

#url =  'http://10.0.80.133:3000/oauth/getDetails'
#url = 'https://serene-wildwood-35121.herokuapp.com/oauth/changeUr/'
#clientSecret = "445b354949599afbcc454441543297a9a827b477dd3eb78d1cdd478f1482b5da08f9b6c3496e650783927e03b20e716483d5b9085143467804a5c6d40933282f"

class HomeView(TemplateView):
    template_name = "portal/home.html"
    
def home(request):
    categories = Category.objects.all()    #retrive all categories
    context = {'categories': categories}
    return render(request, 'portal/home.html', context)

def privacy(request):
    return render(request, 'portal/privacy.html')


def terms(request):
    return render(request, 'portal/terms.html')


def pricing(request):
    context = {
        'rec_navbar': 1,
    }
    return render(request, 'portal/pricing.html', context)



            
def check_username(request):
    data = json.loads(request.body.decode('utf-8'))
    username = data['username']
    try:
        user = User.objects.get(username=username)
        if user:
            return HttpResponse('<b>Username must be unique.</b>')
    except User.DoesNotExist:
        return HttpResponse('')


@csrf_exempt
def check_email(request):
    data = json.loads(request.body.decode('utf-8'))
    email = data['email']
    try:
        if User.objects.get(email=email):
            return HttpResponse('<b>Email must be unique.</b>')
    except User.DoesNotExist:
        return HttpResponse('')

@login_required
@csrf_exempt
def open_close_project(request):
    data = json.loads(request.body.decode('utf-8'))
    tid = data["task_id"]
    current_state = data["current"]
    task = Task.objects.get(id=tid)
    task.isCompleted = not task.isCompleted
    task.save()
    return HttpResponse(str(task.isCompleted))

def send_simple_message(reciever,subject,text):
    print(">>",reciever)
    print(">>",subject)
    print(">>",text)
    fromaddr = "freelancingportaliiits@gmail.com"
    toaddr = reciever
    msg = MIMEMultipart()

    msg['From'] = fromaddr
    msg['To'] = toaddr
    msg['Subject'] = subject
    body = text
    msg.attach(MIMEText(body, 'plain'))
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(fromaddr, "freelancingportal")
    text = msg.as_string()
    x=server.sendmail(fromaddr, toaddr, text)
    print(x,"sent mail")
    server.quit()


def recommended_jobs(cuser):
    jobs_recommended = list()
    cuser = CustomUser.objects.get(pk=request.user.pk)
    users_skill_obj_list = UsersSkill.objects.filter(user=cuser)
    skills_list = set([obj.skill for obj in users_skill_obj_list])
    users_languages_obj_list = UsersCommunicationLanguage.objects.filter(
        user=cuser)
    languages_list = set([obj.language for obj in users_languages_obj_list])
    jobs = applicable_jobs(cuser)
    if jobs:
        for job in jobs:
            taskskreq_obj_list = TaskSkillsRequired.objects.filter(task=job)
            job_req_skills = set([obj.skill for obj in taskskreq_obj_list])
            tasklgreq_obj_list = TaskLanguagesRequired.objects.filter(task=job)
            job_req_languages = set(
                [obj.language for obj in tasklgreq_obj_list])
            common_job_skill = skills_list.intersection(job_req_skills)
            common_job_language = languages_list.intersection(
                job_req_languages)
            if len(common_job_skill) > 0 and len(common_job_language) > 0:
                jobs_recommended.append(job)
    return jobs_recommended





def auth_callback_token(request, token):
    payload = {
        'token': token,
        'secret': clientSecret
    }
    response = requests.post(url, payload)
    content = json.loads(response.content.decode('utf-8'))
    student = content['student'][0]
    email = student['Student_Email']
    try:
        user = User.objects.get(email=email)
        login(request, user)
        if request.COOKIES.get('post_project'):
            print(request.COOKIES.get('post_project'))
            return form_state(request, 2)
        return redirect('Portal:home')
    except User.DoesNotExist:
        context = dict()
        context['student'] = student
        skill_list = Skill.objects.all()
        language_list = CommunicationLanguage.objects.all()
        context['skill_list'] = skill_list
        context['language_list'] = language_list
    return render(request, 'signup.html', context)
    

def applicable_jobs(request):
    cuser=None
    projects = Project.objects.filter(is_approved=True)
    '''
    Use this function when using sqlclient database
    '''
    if not cuser:
        projects = Project.objects.filter(is_approved=True)
    else:
        projects = Project.objects.exclude(leader=cuser)

    jobs = set()
    if projects:
        for project in projects:
            if not project.isCompleted:
                tasks = Task.objects.filter(
                        project=project, isCompleted=False)
                for task in tasks:
                    if task.contributor_set.count() == 0:
                        jobs.add(task)
    if jobs:
        print(jobs)
        sorted(jobs, key=lambda x: x.addedOn, reverse=True)
    return jobs


# def applicable_jobs(cuser):
#     '''
#     Use this function when using MySQL as a database
#     '''
#     cur = connection.cursor()
#     if not cuser:
#         id=0
#     else:
#         id=cuser.id
#     cur.callproc('applicable_jobs', [id])
#     results = cur.fetchall()
#     cur.close()
#     jobs = [Task(*row) for row in results]
#     if jobs:
#         jobs = [Task.objects.get(id=job.id) for job in jobs]
#         sorted(jobs, key=lambda x: x.addedOn, reverse=True)
#     return jobs

@login_required
@csrf_exempt
def jobs_update(request):
    data = json.loads(request.body.decode('utf-8'))
    skills = data['skills']
    languages = data['languages']
    credits = data['credits']
    context = dict()
    cuser = None
    if request.user.is_authenticated:
        cuser = CustomUser.objects.get(pk=request.user.pk)
    jobs = applicable_jobs(cuser)
    # else:
    #     jobs = Task.objects.filter(isCompleted=False).order_by('-addedOn')
    filtered_tasks = set()
    filtered_tasks_skills = set()
    filtered_tasks_languages = set()
    filtered_tasks_credits = set()
    skills_len = len(skills)
    languages_len = len(languages)
    if len(skills) == 0 and len(languages) == 0:
        if not credits == "Both":
            filtered_tasks = [job for job in jobs if job.credits == credits]
            jobs = filtered_tasks
    else:
        for task in jobs:
            if skills_len > 0:
                taskskreq = TaskSkillsRequired.objects.filter(task=task)
                skill_list = [Skill.objects.get(
                    id=obj.skill.id) for obj in taskskreq]
                skill_list = [obj.skill_name for obj in skill_list]
                flag_skills = sum([skill in skills for skill in skill_list])
                if flag_skills > 0:
                    filtered_tasks_skills.add(task)
            if languages_len > 0:
                tasklgreq = TaskLanguagesRequired.objects.filter(task=task)
                language_list = [UsersCommunicationLanguage.objects.get(
                    id=obj.language.id) for obj in tasklgreq]
                language_list = [obj.language_name for obj in language_list]
                flag_languages = sum(
                    [language in languages for language in language_list])
                if flag_languages > 0:
                    filtered_tasks_languages.add(task)
            if task.credits == credits:
                filtered_tasks_credits.add(task)

        if credits == "Both":
            if skills_len > 0 and languages_len > 0:
                filtered_tasks = filtered_tasks_skills.intersection(
                    filtered_tasks_languages)
            elif skills_len > 0:
                filtered_tasks = filtered_tasks_skills
            else:
                filtered_tasks = filtered_tasks_languages
        else:
            if skills_len > 0 and languages_len > 0:
                filtered_tasks = filtered_tasks_skills.intersection(
                    filtered_tasks_languages, filtered_tasks_credits)
            elif skills_len > 0:
                filtered_tasks = filtered_tasks_skills.intersection(filtered_tasks_credits)
            else:
                filtered_tasks = filtered_tasks_languages.intersection(filtered_tasks_credits)
        jobs = filtered_tasks
    print(filtered_tasks_skills, filtered_tasks_languages, filtered_tasks_credits)
    context['jobs'] = jobs
    print(jobs)
    return render(request, 'portal/jobs.html', context)


def browse_jobs(request):
    context = dict()
    user = None
    cuser = None
    if request.user.is_authenticated:
        cuser = CustomUser.objects.get(pk = request.user.pk)
    context['jobs'] = applicable_jobs(cuser)
    skill_list = UsersSkill.objects.filter(pk = request.user.pk)
    language_list = UsersCommunicationLanguage.objects.filter(pk = request.user.pk)
    context['skill_list'] = skill_list
    context['language_list'] = language_list
    if(request.method=='GET'):
        context['skill_check']=request.GET.get('skill',None)
        context['language_check']=request.GET.get('language',None)
    return render(request, 'portal/browsejobs.html', context)


def form_state(request, id=1):
    context = dict()
    projects=Project.objects.filter(pk=request.user.pk)
    if projects  == 1:
        project_name = request.POST['project_name']
        description = request.POST['description']
        deadline = request.POST['deadline']
        context['post_project'] = 'post_project'
        response = render(request, 'portal/login.html', context)
        response.set_cookie('post_project', 'post_project')
        response.set_cookie('project_name', str(project_name))
        response.set_cookie('description', str(description))
        response.set_cookie('deadline', str(deadline))
        return response
    else:
        context['project_name'] = request.COOKIES.get('project_name')
        context['description'] = request.COOKIES.get('description')
        context['deadline'] = request.COOKIES.get('deadline')
        context['post_project'] = 'post_project'
        response = render(request, 'portal/postproject.html', context)
        response.delete_cookie('post_project')
        response.delete_cookie('project_name')
        response.delete_cookie('description')
        response.delete_cookie('deadline')
        return response

class ProjectView(LoginRequiredMixin, CreateView):
    form_class = ProjectForm
    template_name = 'portal/postproject.html'
    success_url = reverse_lazy('portal:myprojects')

    def post_project(request):
        if request.method == 'POST':
            project_name = request.POST['name']
            description = request.POST['desc']
            deadline = request.POST['deadline']
            if request.user.is_authenticated:
                project = Project()
                project.project_name = project_name
                project.description = description
                project.leader = CustomUser.objects.get(pk=request.user.pk)
                project.deadline = deadline
                project.postedOn=datetime.now()
                project.save()
                return redirect('portal:project_description',project.id)
        else:
            return form_state(request)
        return render(request, "portal/postproject.html")


class UsersSkillView(LoginRequiredMixin, CreateView):
    form_class = UsersSkillForm
    template_name = 'portal/userskill.html'
    success_url = reverse_lazy('portal:my-profile')

@login_required
def edit_userskills(request):
    user = request.user
    skill = UsersSkill.objects.get(pk=request.user.pk)
    if request.method == "POST":
        form = UsersSkillForm(request.POST, request.FILES, instance=skill)
        if form.is_valid():
            data = form.save(commit=False)
            data.save()
            return redirect('portal:my-profile')
    else:
        form = UsersSkillForm(instance=skill)
    context = {
        'form': form,
        'project': skill
    }
    return render(request, 'portal/edit_skill.html', context)

class UsersCommunicationLanguageView(LoginRequiredMixin, CreateView):
    form_class = UsersCommunicationLanguageForm
    template_name = 'portal/usercommunicationlanguage.html'
    success_url = reverse_lazy('portal:my-profile')



@login_required
def edit_userlanguage(request):
    user = request.user
    language = UsersCommunicationLanguage.objects.get(pk=request.user.pk)
    if request.method == "POST":
        form = UsersCommunicationLanguageForm(request.POST, request.FILES, instance=language)
        if form.is_valid():
            data = form.save(commit=False)
            data.save()
            return redirect('portal:my-profile')
    else:
        form = UsersCommunicationLanguageForm(instance=language)
    context = {
        'form': form,
        'project': language
    }
    return render(request, 'portal/edit_language.html', context)


class ContributorView(LoginRequiredMixin, CreateView):
    form_class = ContributorForm
    template_name = 'portal/contributor.html'
    success_url = reverse_lazy('portal:task_description')
    
    

def myprojects(request):
    if request.user.is_authenticated:
        context={}
        cuser=CustomUser.objects.get(pk = request.user.pk)
        posted_tasks = [j for i in cuser.project_set.all() for j in i.task_set.all()]
        contributor_tasks=[i.task for i in cuser.contributor_set.all()]
        context['current_projects']=[i for i in cuser.project_set.all() if i.task_set.count()==0]
        context['completed']=[i for i in posted_tasks if i.isCompleted==True]+[i for i in contributor_tasks if i.isCompleted==True]
        context['active']=[i for i in posted_tasks if i.isCompleted==False]+[i for i in contributor_tasks if i.isCompleted==False]
        return render(request, 'portal/myprojects.html',context)
    return render(request, 'login.html')

def project_list(request, category_slug=None):
     category = None
     categories = Category.objects.all()
     projects = Project.objects.all()
     if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        projects = projects.filter(category=category)
     return render(request,'portal/list.html',
     {'category': category,
     'categories': categories,
     'projects': projects})

def projects(request):
    projects = Project.objects.all().order_by('postedOn')
    return render(request,'portal/projects.html', {'projects': projects})


 
def project_description(request, project_id):
    project = Project.objects.get(id=project_id)
    if not project.isCompleted:
        if project.deadline < datetime.now().date():
            project.isCompleted = True
            project.save()
    added_tasks = Task.objects.filter(project=project.id)
    context = dict()
    context['project'] = project
    context['added_tasks'] = added_tasks
    year = project.deadline.strftime("%Y")
    month = project.deadline.strftime("%m")
    date = project.deadline.strftime("%d")
    context['year'] = year
    context['month'] = month
    context['date'] = date
    if request.user.is_authenticated:
        context['is_leader'] = (project.leader.pk == request.user.pk)
    return render(request, 'portal/projectdescription.html', context)

@login_required
def edit_project(request, project_id):
    user = request.user
    project = Project.objects.get(pk=request.user.pk)
    if request.method == "POST":
        form = ProjectForm(request.POST, request.FILES, instance=project)
        if form.is_valid():
            data = form.save(commit=False)
            data.save()
            return redirect('portal:myprojects')
    else:
        form = ProjectForm(instance=project)
    context = {
        'form': form,
        'project': project
    }
    return render(request, 'portal/edit_project.html', context)

class TaskView(LoginRequiredMixin, CreateView):
    form_class = TaskForm
    template_name = 'portal/addtask.html'
    success_url = reverse_lazy('portal:myprojects')

    def add_task(request, project_id):
        context = {}
        if request.method == 'POST':
            form.fields['project'].queryset = Task.objects.filter(id=task_id)
            if request.user.is_authenticated:
                task = Task()
                task.task_name = request.POST['name']
                task.task_description = request.POST['desc']
                task.credits = request.POST['credits']
                if(task.credits=="Other"):
                    task.mention = request.POST['mention']
                elif(task.credits=="Paid"):
                    task.amount = int(request.POST['amount'])
                task.deadline = request.POST['deadline']
                skills = request.POST.getlist('skills[]')
                languages = request.POST.getlist('languages[]')
                task.project = Project.objects.get(id=project_id)
                task.save()
                project = Project.objects.get(id=task.project.id)
                project.task_count += 1
                project.save()
                for rskill in skills:
                    skill = UsersSkill.objects.get(skill_name=rskill)
                    task_skill_req = TaskSkillsRequired()
                    task_skill_req.task = task
                    task_skill_req.skill = skill
                    task_skill_req.proficiency_level_required = int(
                        request.POST[skill.skill_name])
                    task_skill_req.save()
                for rlanguage in languages:
                    language = UsersCommunicationLanguage.objects.get(
                        language_name=rlanguage)
                    task_language_req = TaskLanguagesRequired()
                    task_language_req.task = task
                    task_language_req.language = language
                    task_language_req.fluency_level_required = int(
                        request.POST[language.language_name])
                    task_language_req.save()
                return redirect('portal/task_description',project_id ,task.id)
            return render(request, 'login.html')
        project = Project.objects.get(id=project_id)
        year = project.deadline.strftime("%Y")
        month = project.deadline.strftime("%m")
        date = project.deadline.strftime("%d")
        context['year'] = year
        context['month'] = month
        context['date'] = date
        context['project_id'] = project_id
        skill_list = UsersSkill.objects.all()
        language_list = UsersCommunicationLanguage.objects.all()
        context['skill_list'] = skill_list
        context['language_list'] = language_list
        return render(request, "portal/addtask.html", context)


@login_required
def task_skill(request):
    user = request.user
    skill = TaskSkillsRequired.objects.get(pk=request.user.pk)

    if request.method == "POST":
        form = TaskSkillsRequiredForm(request.POST)
        if form.is_valid():
            data = form.save(commit=False)
            data.user = user
            data.save()
            return redirect('portal:myprojects')
    else:
        form = TaskSkillsRequiredForm()
    context = {
        'form': form
    }
    return render(request, 'portal/task_skills.html', context)


class TaskLanguagesView(LoginRequiredMixin, CreateView):
    form_class = TaskLanguagesRequiredForm
    template_name = 'portal/task_languages.html'
    success_url = reverse_lazy('portal:myprojects')



def applicants(request, task_id):
    task = Task.objects.get(id=task_id)
    applicants = Applicant.objects.filter(task=task).order_by('time_of_application')
    profiles = []
    for applicant in applicants:
        profile = Profile.objects.filter(user=applicant.applicant).first()
        profiles.append(profile)
    context = {
        'profiles': profiles,

        'task': task,
    }
    return render(request, "portal/applicants.html", context)
    
def task_description(request, project_id, task_id):
    task = Task.objects.get(id=task_id, project=project_id)
    if not task.isCompleted:
        if task.deadline < datetime.now().date():
            task.isCompleted = True
            task.save()
    context = dict()
    year = task.deadline.strftime("%Y")
    month = task.deadline.strftime("%m")
    date = task.deadline.strftime("%d")
    context['year'] = year
    context['month'] = month
    context['date'] = date
    # if(request.user.is_authenticated):
    #     cuser=CustomUser.objects.get(user=request.user)
    #     if task.isCompleted:
    #         try:
    #             taskuserrating = UserRating.get(task=task)
    #             context["user_rating"]=taskuserrating
    #         except:
    #             taskuserrating = UserRating(task=task, emp=task.project.leader, fre=)
    #             context["user_rating"]= 
    context['task'] = task
    context['is_leader'] = (task.project.leader.pk == request.user.pk)
    context['applicants'] = task.task_name
    context['is_contributor'] = False
    context['submit_link'] = task.task_link
    context['skills_required'] = task.taskskillsrequired_set.all()
    context['languages_required']=task.tasklanguagesrequired_set.all()
    context['task_rating'] = task.rating
    try:
        context['contributor'] = task.contributor_set.get(pk=request.user.pk)
        context['is_contributor'] = (context['contributor'].pk == request.user.pk)
    except Contributor.DoesNotExist:
        context['contributor'] = None
    if request.method == 'POST':
        if request.user.is_authenticated:
            if request.POST["work"] == "status_update":
                status_update(request, task)
            elif request.POST["work"] == "user_task_rating":
                user_task_rating(request, task)
            elif request.POST["work"] == "user_user_rating":
                user_user_rating(request, task, context)
            elif request.POST["work"] == "start_working":
                start_end_working(request, task, )
        return redirect("portal:task_description", project_id, task_id)
    return render(request, 'portal/taskdescription.html', context)
    
def task_editfunction(request, project_id, task_id):
    if request.user.is_authenticated:
        task = Task.objects.get(id=task_id, project=project_id)
        project = Project.objects.get(id=project_id)
        context = {}
        context['task'] = task
        context['project'] = project
        if request.method == 'POST':
            task.task_name = request.POST['name']
            task.task_description = request.POST['description']
            task.credits = request.POST['credits']
            if task.credits == 'Paid':
                task.amount = int(request.POST['amount'])
            else:    
                task.mention = request.POST['mention']
            task.deadline = request.POST['deadline']
            task.save()
            return redirect("portal:task_description", project_id, task_id)
        project = Project.objects.get(id=project_id)
        year = project.deadline.strftime("%Y")
        month = project.deadline.strftime("%m")
        date = project.deadline.strftime("%d")
        context['year'] = year
        context['month'] = month
        context['date'] = date
        return render(request,'portal/edittask.html',context)
    return redirect("portal:task_description", project_id, task_id)



@login_required
def submit_task(request, task):
    submit_url = request.POST.get("work_link",None)
    if(submit_url!=None):
        if (not task.isCompleted):
            task.task_link = submit_url
            task.save()

def status_update(request, task):
    if request.POST["status_update"] == "open":
        task.isCompleted = False
    elif request.POST["status_update"] == "close":
        task.isCompleted = True
    else:
        print("some error in task_description")
    task.save()


def applyTask(request, project_id, task_id):
    user = request.user
    task = Task.objects.get(id=task_id, project=project_id)
    project = Project.objects.get(id=project_id)
    
    form=ApplicantForm()
    form.fields['applicant'].queryset = CustomUser.objects.filter(pk=request.user.pk)
    form.fields['task'].queryset = Task.objects.filter(id=task_id)
    if request.method=='POST':
        form=ApplicantForm(request.POST,request.FILES)
        if form.is_valid():
            form.save()
        applied, created = AppliedTask.objects.get_or_create(task=task, user=user)
        applicant, creation = Applicant.objects.get_or_create(task=task, applicant=user)
        return redirect('portal:thanks')
    context={'form':form}
    return render(request,'portal/task_applicants.html',context)



class ThanksView(TemplateView):
    template_name = 'portal/thanks.html'
    success_url = reverse_lazy('portal:browse_jobs')

class TaskAppView(TemplateView):
    template_name = 'portal/task_applicants.html'
    success_url = reverse_lazy('portal:browse_jobs')


@login_required
def submit_task_review(request, task):
    print("We will accept/reject the students work here")


def user_task_rating(request,task):
    task.rating=request.POST.get("rating",None)
    task.save()


def user_user_rating(request,task,context):
    try:
        uurating=UserRating.objects.get(task=task)
    except:
        uurating=UserRating()
    uurating.task=task
    uurating.fre=Contributor.objects.get(task=task).user
    uurating.emp=task.project.leader
    if(context["is_contributor"]):
        uurating.e_rating=request.POST.get("rating",None)
    elif(context["is_leader"]):
        uurating.f_rating=request.POST.get("rating",None)
    uurating.save()


def select_user(request, task, context):
    user_id = request.POST["user_id"]
    is_applicant = False
    print(user_id)
    for i in context['applicants']:
        if i.user.user.id == int(user_id):
            is_applicant = True
    if is_applicant:
        if task.contributor_set.count() == 0:
            contributor = Contributor()
            contributor.user = CustomUser.objects.get(user=int(user_id))
            contributor.task = Task.objects.get(id=task.id)
            contributor.save()
            send_simple_message(str(contributor.user.user.email),"Selection for the Task"+str(),"You have been selected for the task "+str(contributor.task.task_name)+" of project "+str(contributor.task.project.project_name)+"\n\n -"+str(contributor.task.project.leader.user.username)) 
            for i in context['applicants']:
                if i.user!=contributor.user:
                    send_simple_message(str(i.user.user.email),"Non-Selection for the Task"+str(),"You have not been selected for the task "+str(contributor.task.task_name)+" of project "+str(contributor.task.project.project_name)+"\n\n -"+str(contributor.task.project.leader.user.username))
        else:
            print("we already have a contributor")
    else:
        print("Not an applicant")





@login_required
def selected_list(request, slug):
    task = get_object_or_404(Task, slug=slug)
    selected = Selected.objects.filter(task=task).order_by('date_posted')
    profiles = []
    for applicant in selected:
        profile = Profile.objects.filter(user=applicant.applicant).first()
        profiles.append(profile)
    context = {
        'profiles': profiles,
        'task': task,
    }
    return render(request, 'portal/selected_list.html', context)


@login_required
def select_applicant(request, can_id, task_id):
    task = get_object_or_404(Task, slug=task_id)
    profile = get_object_or_404(Profile, slug=can_id)
    user = profile.user
    selected, created = Selected.objects.get_or_create(task=task, applicant=user)
    applicant = Applicant.objects.filter(task=task, applicant=user).first()
    context = {
        'profile': profile,
        'task': task,
    }
    applicant.delete()
    return HttpResponse("Applicant Selected")

@login_required
def remove_applicant(request, can_id, task_id):
    task = get_object_or_404(Task, slug=task_id)
    profile = get_object_or_404(Profile, slug=can_id)
    user = profile.user
    applicant = Applicant.objects.filter(task=task, applicant=user).first()
    applicant.delete()
    return HttpResponse("Applicant Rejected")


@login_required
def save_task(request, slug):
    user = request.user
    task = get_object_or_404(Task, slug=slug)
    saved, created = SavedTask.objects.get_or_create(task=task, user=user)
    return HttpResponse("Task saved")


@login_required
def saved_tasks(request):
    tasks = SavedTask.objects.filter(
        user=request.user).order_by('-date_posted')
    return render(request, 'portal/saved_tasks.html', {'tasks': tasks})

def saved_task_details(request, task_id):
    task = get_object_or_404(SavedTask, pk=task_id)
    context = {
        'task': task,
    }
    return render(request, 'portal/savedtaskdetails.html', context)

def task(request, project_id, task_id):
    task = get_object_or_404(Task, pk=task_id)
    project = get_object_or_404(Project, pk=project_id)
    context = {
        'task': task,
        'project': project,
    }
    return redirect("portal:task_description", project_id, task_id)
    return render(request, 'portal/taskdescription.html', context)



@login_required
def applied_tasks(request):
    tasks = AppliedTask.objects.filter(
        user=request.user).order_by('-date_posted')
    statuses = []
    for task in tasks:
        if Selected.objects.filter(task=task.task).filter(applicant=request.user).exists():
            statuses.append(0)
        elif Applicant.objects.filter(task=task.task).filter(applicant=request.user).exists():
            statuses.append(1)
        else:
            statuses.append(2)
    zipped = zip(tasks, statuses)
    return render(request, 'portal/applied_task.html', {'zipped': zipped})

def applied_task_details(request, task_id):
    task = get_object_or_404(AppliedTask, pk=task_id)
    context = {
        'task': task,
    }
    return render(request, 'portal/appliedtaskdetails.html', context)
    

@login_required
def user_profile(request):
    you = request.user
    context = dict()
    cuser = CustomUser.objects.get(pk=request.user.pk)
    profile = Profile.objects.filter(user=you).first()
    context = {
        'u': you,
        'profile': profile,
    }
    context['cuser'] = cuser
    if request.user.is_authenticated:
        if request.method == "POST":
            bio = request.POST['bio']
            cuser.bio = bio
            if request.FILES.get('profile_picture', None) is not None:
                profile_picture = request.FILES['profile_picture']
                cuser.image = profile_picture
            cuser.save()
            skills = request.POST.getlist('skills[]')
            languages = request.POST.getlist('languages[]')
            UsersSkill.objects.filter(pk = request.user.pk).all()
            UsersCommunicationLanguage.objects.filter(
                pk = request.user.pk).all()
            for skill in skills:
                skillreq = UsersSkill.objects.get(skill_name=skill)
                uskill = UsersSkill(skill=skillreq, user=cuser,
                                    level_of_proficiency=int(request.POST[skill]))
                uskill.save()
            for language in languages:
                languagereq = UsersCommunicationLanguage.objects.get(language_name=language)
                ulanguage = UsersCommunicationLanguage(language=languagereq, user=cuser,
                                                       level_of_fluency=int(request.POST[language]))
                ulanguage.save()
            return redirect('portal:my-profile')
    skills = UsersSkill.objects.filter(user=cuser)
    languages = UsersCommunicationLanguage.objects.filter(user=cuser)
    context['uskills'] = [obj.skill_name for obj in skills]
    context['ulanguages'] = [
        obj.language_name for obj in languages]
    skill_list = UsersSkill.objects.filter(pk = request.user.pk)
    context['skill_list'] = skill_list
    language_list = UsersCommunicationLanguage.objects.filter(pk = request.user.pk)
    context['skill_list'] = skill_list
    context['language_list'] = language_list
    context['erating'], context['frating'] = give_rating(cuser)
    return render(request, 'portal/profile.html', context)



@login_required
def edit_profile(request):
    you = request.user
    profile = Profile.objects.filter(user=you).first()
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            data = form.save(commit=False)
            data.user = you
            data.save()
            return redirect('portal:my-profile')
    else:
        form = ProfileUpdateForm(instance=profile)
    context = {
        'form': form,
    }
    return render(request, 'portal/edit_profile.html', context)


@login_required
def profile_view(request, profile_id):
    p= Profile.objects.get(id=profile_id)
    user_skills = UsersSkill.objects.filter(pk=request.user.pk)
    user_languages = UsersCommunicationLanguage.objects.filter(pk=request.user.pk)
    context = {
        'profile': p,
        'skills': user_skills,
        'languages': user_languages,
    }
    return render(request, 'portal/profile-description.html', context)


def give_rating(cuser):
    etasks = cuser.rating_by.all()
    ftasks = cuser.rating_to.all()
    elist = [task.e_rating for task in etasks]
    flist = [task.f_rating for task in ftasks]
    erating = None 
    frating = None
    if len(elist)>0:
        erating = int(round(sum(elist)/len(elist)))
        erating = [[1] * erating, [1] * (5 - erating)]
    if len(flist)>0:
        frating = int(round(sum(flist)/len(flist)))
        frating = [[1] * frating, [1] * (5 - frating)]
    return erating, frating



class UseratingView(LoginRequiredMixin, CreateView):
    form_class = UserRatingForm
    template_name = 'portal/user_rating.html'
    success_url = reverse_lazy('portal:my-profile')

class NotificationView(LoginRequiredMixin, CreateView):
    form_class = NotificationForm
    template_name = 'portal/notification.html'
    success_url = reverse_lazy('portal:my-profile')


class ContactView(CreateView):
    template_name = 'portal/contact_form.html'
    form_class = ContactForm
    success_url = reverse_lazy("portal:contact_thanks")


def thanks(request):
    return HttpResponse("Thank you! Will get in touch soon.")