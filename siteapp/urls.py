from django.urls import path
from . import views
app_name = 'siteapp'
urlpatterns = [
    path('',views.index, name='index'),
    path('register/',views.register,name='register'),
    path('login/',views.login_,name='login'),
    path('logout/',views.logout_,name='logout'),
    path('activate/<uidb64>/<token>/',
        views.activate, name='activate'),
]
