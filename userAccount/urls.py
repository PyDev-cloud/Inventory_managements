from django.urls import path
from .views import(
     home,
     Login,
     Logout,
     Registration,
     ChangePassword,
)
urlpatterns = [
    path('',home.as_view(),name="home"),
    path('login/',Login.as_view(),name="login"),
    path('logout/',Logout.as_view(),name='logout'),
    path('registration/',Registration.as_view(),name="register"),
    path('changePassword/',ChangePassword.as_view(),name="changepassword")

]