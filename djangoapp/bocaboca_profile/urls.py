from django.urls import path
from . import views
from django.contrib.auth.views import LogoutView

app_name = "bocaboca_profile"

urlpatterns = [
    path("send_activation_link/", views.send_activation_link, name="send_activation_link"),
    path("activate/<str:activation_key>/", views.complete_registration, name="activate_account"),
    #path('new_user/edit/<str:username>/', views.edit_new_user, name='edit_new_user'),
    #path('new_client/edit/<str:username>/', views.edit_new_client, name='edit_new_client'),
    #path('activation_success/', views.activation_success, name='activation_success'),
    #path('activation_client_success/', views.activation_client_success, name='activation_client_success'),
    #path('handle_profile_submission/', views.handle_profile_submission, name='handle_profile_submission'),
    path('logout/', LogoutView.as_view(), name='logout'),
    #path('dashboard/', views, name='dashboard'),
    path('role-selection/', views.role_selection, name='role_selection'),
    

]