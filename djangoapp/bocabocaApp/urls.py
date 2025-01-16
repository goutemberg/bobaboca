

from django.urls import path
from bocaboca_profile import views as profile_views
from bocabocaApp import views as app_views


app_name = "bocaboca"

urlpatterns = [
    path('', app_views.index, name='index'),  # Rota para o index
    path('profissional/<str:categoria>/', app_views.profissional_view, name='profissional'),  
    path('profissional/', app_views.profissional_sem_categoria, name='profissional_sem_categoria'),  
    path('register/', app_views.register_view, name='register'),
    path('login/', app_views.login, name='login'),
    #path('profile/edit/<str:username>/', profile_views.edit_profile, name='edit_profile'), 
    path('submit_profile/', app_views.submit_profile, name='submit_profile'),
    path('new_user/edit/<str:username>/', profile_views.edit_new_user, name='edit_new_user'),
    path('activation_success/<str:email>/', profile_views.activation_success, name='activation_success'),

]

