from django.urls import path
from appFT import views
from django.conf import settings
from django.conf.urls.static import static
from .views import profile_view, EditProfileView
from .views import chat_view, delete_message
urlpatterns = [
    path("", views.index, name='index'),
    path('choose-plan/', views.choose_plan, name='choose_plan'),
    path('confirmation/<int:member_id>/', views.ConfirmationView.as_view(), name='confirmation'),
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path("profile/", profile_view, name='profile'),  # Путь для просмотра профиля
    path('chat/', chat_view, name='chat'),
    path('delete_message/<int:message_id>/', views.delete_message, name='delete_message'),
    path("edit-profile/", EditProfileView.as_view(), name='edit_profile'),  # Путь для редактирования профиля
    path("home/", views.index2, name='index2'),  # Добавьте этот путь, если нужно
    path('create-training-session/', views.create_training_session, name='create_training_session'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)