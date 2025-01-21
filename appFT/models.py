from django.db import models
from django.contrib.auth.models import User

class Plan(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    training_days = models.JSONField(default=list)  # Хранение дней, например: [0, 2, 4] для понедельника, среды и пятницы

    def __str__(self):
        return self.name


class Trainer(models.Model):
    name = models.CharField(max_length=100)
    specialization = models.CharField(max_length=100)

    def __str__(self):
        return self.name

from django.db import models
from django.contrib.auth.models import User

from django.db import models
from django.contrib.auth.models import User

class GymMember(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    profile_image = models.ImageField(upload_to='profile_images', default='default_avatar.png')  # Устанавливаем изображение по умолчанию
    plan = models.ForeignKey('Plan', on_delete=models.SET_NULL, null=True)
    trainer = models.ForeignKey('Trainer', on_delete=models.SET_NULL, null=True)
    additional_info = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


from django.db import models
from django.contrib.auth.models import User
from datetime import datetime
from django.utils import timezone

class TrainingSession(models.Model):
    member = models.ForeignKey('GymMember', on_delete=models.CASCADE)
    trainer = models.ForeignKey('Trainer', on_delete=models.CASCADE)
    plan = models.ForeignKey('Plan', on_delete=models.CASCADE)
    date = models.DateTimeField()
    duration = models.PositiveIntegerField(default=60)  # Длительность тренировки по умолчанию 60 минут
    notes = models.TextField(blank=True, null=True)

    class Meta:
        unique_together = ('trainer', 'date')  # Обеспечивает уникальность тренера и времени

    def __str__(self):
        return f"Тренировка с {self.trainer.name} для {self.member.first_name} {self.member.last_name} на {self.date}"




# models.py
from django.db import models
from django.contrib.auth.models import User

class UserRole(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.user.username}: {self.role}"

# models.py
from django.db import models
from django.contrib.auth.models import User

class ChatMessage(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField(blank=True, null=True)  # Содержание может быть пустым, если отправляется только изображение
    image = models.ImageField(upload_to='chat_images', blank=True, null=True)  # Поле для изображения
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message from {self.user.username} at {self.timestamp}"

from django.db import models
from django.contrib.auth.models import User

class UserMessage(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='messages')
    message = models.TextField()
    response = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_resolved = models.BooleanField(default=False)

    def __str__(self):
        return f"Message from {self.user.username}"
