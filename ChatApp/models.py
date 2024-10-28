from django.db import models
from django.contrib.auth.models import User

class Chat(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Link chat to a user
    message = models.TextField()  # User's message
    response = models.TextField()  # AI's response
    created_at = models.DateTimeField(auto_now_add=True)  # Automatically set the field to now when created

    def __str__(self):
        return f"Chat(id={self.id}, user={self.user.username}, message={self.message[:20]}, response={self.response[:20]})"
