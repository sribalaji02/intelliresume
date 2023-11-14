from django.urls import path
from . import views

urlpatterns = [
    path('signup/', views.signup, name="signup"),
    path('login/', views.login, name = "login"),
    path('validate/', views.validate, name = "validate"),
    path('home/<uname>', views.home, name = "home"),
    path('res/<uname>', views.res, name = "res"),
    path('resgen/<uname>', views.resgen, name = "resgen"),
    path('chat/<uname>', views.chat, name = "chat"),
]
