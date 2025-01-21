# forms.py
from django import forms
from django.contrib.auth.models import User
from .models import GymMember, Plan, Trainer
from django.core.exceptions import ValidationError

class FitnessPlanForm(forms.Form):
    first_name = forms.CharField(max_length=100, label="Имя", widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(max_length=100, label="Фамилия", widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(label="Email", widget=forms.EmailInput(attrs={'class': 'form-control'}))
    plan = forms.ModelChoiceField(queryset=Plan.objects.all(), label="Выберите план", widget=forms.Select(attrs={'class': 'form-control'}))
    trainer = forms.ModelChoiceField(queryset=Trainer.objects.all(), label="Выберите тренера", widget=forms.Select(attrs={'class': 'form-control'}))
    additional_info = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 4}), label="Дополнительные пожелания", required=False)

class GymMemberForm(forms.ModelForm):
    class Meta:
        model = GymMember
        fields = ['first_name', 'last_name', 'email', 'profile_image', 'plan', 'trainer', 'additional_info']
        labels = {
            'first_name': 'Имя',
            'last_name': 'Фамилия',
            'email': 'Email',
            'profile_image': 'Изображение профиля',
            'plan': 'Выберите план',
            'trainer': 'Выберите тренера',
            'additional_info': 'Дополнительные пожелания',
        }

    def __init__(self, *args, **kwargs):
        super(GymMemberForm, self).__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if GymMember.objects.exclude(pk=self.instance.pk).filter(email=email).exists():
            raise ValidationError("Этот email уже занят другим пользователем.")
        return email

class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    first_name = forms.CharField(max_length=100, label="Имя", widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(max_length=100, label="Фамилия", widget=forms.TextInput(attrs={'class': 'form-control'}))

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'first_name', 'last_name']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError("Этот email уже занят.")
        return email

class UserLoginForm(forms.Form):
    username = forms.CharField(label="Имя пользователя", widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}), label="Пароль")

# forms.py
from django import forms

# forms.py
from django import forms
from .models import ChatMessage

from django.core.exceptions import ValidationError

class ChatMessageForm(forms.ModelForm):
    class Meta:
        model = ChatMessage
        fields = ['content', 'image']
        widgets = {
            'content': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Напишите сообщение...',
                'style': 'border-radius: 25px;'
            }),
            'image': forms.ClearableFileInput(attrs={
                'class': 'form-control-file',
                'style': 'margin-top: 10px;'
            }),
        }

    def clean_image(self):
        image = self.cleaned_data.get('image')
        if image:
            # Поддерживаем .jpg, .jpeg, .png, .gif и .webp
            if not image.name.endswith(('jpg', 'jpeg', 'png', 'gif', 'webp')):
                raise ValidationError('Поддерживаются только изображения форматов .jpg, .jpeg, .png, .gif, .webp')
        return image


# appFT/forms.py
from django import forms
from .models import TrainingSession

from django import forms
from .models import TrainingSession, Trainer

class TrainingSessionForm(forms.ModelForm):
    class Meta:
        model = TrainingSession
        fields = ['trainer', 'date']

    trainer = forms.ModelChoiceField(queryset=Trainer.objects.all(), empty_label="Выберите тренера")
    date = forms.DateTimeField(input_formats=['%Y-%m-%d %H:%M'], widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}))

