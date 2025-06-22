from django.forms.forms import BaseForm
from django.shortcuts import render,redirect
from django.contrib import messages
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import authenticate,login,logout
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.urls import reverse_lazy



from .mixins import(
     LogoutMixins,
)
from .forms import (
    LoginForm,
    UserRegistrationForm,
    ChengePassowdForm,
)

# Create your views here.

@method_decorator(never_cache,name="dispatch")
class home(LoginRequiredMixin,generic.TemplateView):
    login_url='login'
    template_name = "home.html"

    

@method_decorator(never_cache,name="dispatch")
class Login(LogoutMixins,generic.View):
    def get(self,*args, **kwargs):
        form=LoginForm()
        context={
            'form':form
        }
        return render(self.request,'account/login.html',context)
    
    def post(self,*args, **kwargs):
        form=LoginForm(self.request.POST)

        if form.is_valid():
            user=authenticate(
                self.request,
                username=form.cleaned_data.get('username'),
                password=form.cleaned_data.get('password')
            )
            if user:
                login(self.request,user)
                return redirect('home')
            else:
                messages.warning(self.request,"Email and Password not match")
                return redirect('login')
        else:
            messages.warning(self.request,'User not validated')
            return render(self.request,'account/login.html',{'form':form})
        

class Logout(generic.View):
    def get(self,*args, **kwargs):
        logout(self.request)
        return redirect('login')
    

class Registration(LogoutMixins, generic.CreateView):
    template_name = 'Account/register.html'
    form_class = UserRegistrationForm
    success_url = reverse_lazy('login')

    def form_valid(self, form):
        messages.success(self.request, "Registration Successfull !")
        return super().form_valid(form)
    
    

    

class ChangePassword(LoginRequiredMixin,generic.FormView):
    template_name="Account/chenge_password.html"
    form_class=ChengePassowdForm
    success_url=reverse_lazy('login')


    def get_form_kwargs(self) :
        context= super().get_form_kwargs()
        context['user']=self.request.user
        return context

    def form_valid(self, form):
        user = self.request.user
        user.set_password(form.cleaned_data.get('new_password'))
        user.save()
        messages.success(self.request, "Password changed Successfully !")
        return super().form_valid(form)
    