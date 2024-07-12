
from django.db import models
from django.contrib.auth import get_user_model
import uuid

User = get_user_model()

class Automation(models.Model):
    session_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    objective = models.CharField(max_length=255)
    created_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Automation {self.session_id} - {self.objective}"
