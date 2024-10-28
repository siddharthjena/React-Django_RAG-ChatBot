from django.urls import path
from .views import RegisterView, LoginView, ChatView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('chat/', ChatView.as_view(), name='chat'),
]