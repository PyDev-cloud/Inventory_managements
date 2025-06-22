from django.shortcuts import redirect,render

class LogoutMixins(object):
    def dispatch(self,request,*args, **kwargs):
        if self.request.user.is_authenticated:
            return redirect('home')
        return super(LogoutMixins,self).dispatch(request,*args, **kwargs)