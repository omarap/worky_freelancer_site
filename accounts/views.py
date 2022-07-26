from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import CreateView
from django.views import generic
from .forms import CustomUserCreationForm
from .models import CustomUser
from django.contrib.auth import authenticate, login
from django.http import Http404

# Create your views here.

class SignUpView(generic.CreateView):
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('login')
    template_name = 'signup.html'

    def signup_user(request):
            context = dict()
            skill_list = Skill.objects.all()
            language_list = CommunicationLanguage.objects.all()
            context['skill_list'] = skill_list
            context['language_list'] = language_list
            if request.method == 'POST':
                username = request.POST['name']
                first_name = request.POST['fname']
                last_name = request.POST['lname']
                email = request.POST['email']
                age = request.POST['age']
                phone_number = request.POST['phno']
                bio = request.POST['bio']
                image = request.FILES['image']
                batchYear = request.POST['batch']
                gender = request.POST['gender']
                skills = request.POST.getlist('skills[]')
                languages = request.POST.getlist('languages[]')
                user = User.objects.create_user(username=username, first_name=first_name, last_name=last_name, email=email,
                                                password=password1)
                cuser = CustomUser(user=user, phone_number=phone_number, image=image, bio=bio, batchYear=batchYear,
                                   gender=gender)
                user.save()
                cuser.save()
                for uskill in skills:
                    skill = Skill.objects.get(skill_name=uskill)
                    cuskill = UsersSkill()
                    cuskill.skill = skill
                    cuskill.user = cuser
                    cuskill.level_of_proficiency = int(request.POST[skill.skill_name])
                    cuskill.save()
                for ulanguage in languages:
                    language = CommunicationLanguage.objects.get(
                        language_name=ulanguage)
                    culanguage = UsersCommunicationLanguage()
                    culanguage.language = language
                    culanguage.user = cuser
                    culanguage.level_of_fluency = int(
                        request.POST[language.language_name])
                    culanguage.save()
                login(request, user)
                return HttpResponseRedirect(reverse("portal:home"))
            return render(request, 'signup.html', context)




def login(request):
    username = request.POST['username']
    password = request.POST['password']
    user = authenticate(request, username=username, password=password)
    if user is not None:
        login(request, user)
        # Redirect to a success page.
        return redirect('home')
    else:
        # Return an 'invalid login' error message.
        raise Http404("please login with valid credentials")