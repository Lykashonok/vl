from django.urls import path

from . import views as lab_queue_views
from django.contrib.auth import views as auth_views

app_name = 'lab_queue'
urlpatterns = [
    path('', lab_queue_views.index, name = 'index'),
    path('<int:queue_id>/', lab_queue_views.detail, name = 'detail'),
    path('register/', lab_queue_views.register, name = 'register'),
    # path('editqueue/', lab_queue_views.editqueue, name = 'editqueue'),
    path('account/', lab_queue_views.account, name = 'account'),
    path('newqueue/', lab_queue_views.newqueue, name = 'newqueue'),
    path('login/', auth_views.LoginView.as_view(template_name='lab_queue/login.html'), name = 'login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='lab_queue/logout.html'), name = 'logout'),
]