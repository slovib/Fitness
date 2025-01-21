from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.utils import timezone
from datetime import datetime, timedelta
from django.http import JsonResponse
from django.views import View
from collections import defaultdict
from django.contrib.auth.decorators import login_required
from .models import GymMember, TrainingSession, Plan, Trainer, UserRole
from .forms import GymMemberForm, UserRegistrationForm, UserLoginForm, ChatMessageForm
from .forms import ChatMessage
import logging

logger = logging.getLogger(__name__)
def index2(request):
    return render(request, "index2.html")
# Главная страница
def index(request):
    return render(request, "index.html")

# Страница выбора плана
def choose_plan(request):
    if request.method == 'POST':
        gym_member = get_object_or_404(GymMember, user=request.user)
        form = GymMemberForm(request.POST, instance=gym_member)
        if form.is_valid():
            form.save()
            return redirect('confirmation', member_id=gym_member.id)
    else:
        gym_member = get_object_or_404(GymMember, user=request.user)
        form = GymMemberForm(instance=gym_member)
    
    return render(request, 'choose_plan.html', {'form': form})

# Подтверждение выбора плана
class ConfirmationView(View):
    def get(self, request, member_id):
        gym_member = get_object_or_404(GymMember, id=member_id)
        return render(request, 'confirmation.html', {
            'first_name': gym_member.first_name,
            'last_name': gym_member.last_name,
            'email': gym_member.email,
            'plan': gym_member.plan,
            'trainer': gym_member.trainer,
            'additional_info': gym_member.additional_info
        })

# Регистрация пользователя
def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.is_active = True
            user.save()

            GymMember.objects.create(
                user=user,
                first_name=form.cleaned_data['first_name'],
                last_name=form.cleaned_data['last_name'],
                email=form.cleaned_data['email'],
                profile_image='default_avatar.png'
            )

            # Назначаем роль 'user'
            user_role, created = UserRole.objects.get_or_create(user=user)
            if created:
                user_role.role = 'user'
                user_role.save()

            login(request, user)
            return redirect('profile')
    else:
        form = UserRegistrationForm()

    return render(request, 'register.html', {'form': form})

# Вход в систему
def login_view(request):
    if request.method == 'POST':
        form = UserLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('profile')
            else:
                form.add_error(None, 'Неверное имя пользователя или пароль.')
        else:
            messages.error(request, 'Форма имеет ошибки.')
    else:
        form = UserLoginForm()

    return render(request, 'login.html', {'form': form})

# Выход из системы
def logout_view(request):
    logout(request)
    return redirect('index')

# Функция для генерации календаря
def generate_calendar():
    today = timezone.now().date()  # Текущая дата
    start_date = today.replace(day=1)  # Начало текущего месяца

    # Найдем, какой день недели первый день месяца (0 = понедельник)
    first_weekday = start_date.weekday()  # Понедельник = 0, воскресенье = 6
    days_in_month = (start_date.replace(month=start_date.month + 1) - timedelta(days=1)).day  # Количество дней в месяце

    # Генерируем календарь с пустыми днями перед первым числом месяца
    calendar_days = []

    # Добавляем пустые дни перед первым числом месяца
    for _ in range(first_weekday):
        calendar_days.append(None)

    # Добавляем все дни месяца
    for day in range(1, days_in_month + 1):
        calendar_days.append(start_date.replace(day=day))

    return calendar_days

# Получение недель для отображения календаря
def get_weeks(calendar_days):
    weeks = []
    for i in range(0, len(calendar_days), 7):
        weeks.append(calendar_days[i:i+7])
    return weeks

from collections import defaultdict
from django.shortcuts import render, get_object_or_404
from .models import GymMember, TrainingSession, Trainer
from django.utils import timezone

def profile_view(request):
    member = get_object_or_404(GymMember, user=request.user)
    today = timezone.now().date()
    weeks = get_weeks(generate_calendar())  # Генерация календаря
    scheduled_sessions = get_scheduled_sessions(member)  # Получаем запланированные тренировки для пользователя

    context = {
        'member': member,
        'weeks': weeks,
        'today': today,
        'scheduled_sessions': scheduled_sessions,  # передаем расписание тренировок
        'trainers': Trainer.objects.all(),  # Список тренеров для модального окна
    }

    return render(request, 'profile.html', context)


def get_scheduled_sessions(member):
    sessions = TrainingSession.objects.filter(member=member)
    sessions_by_day = defaultdict(list)
    for session in sessions:
        sessions_by_day[session.date.date()].append(session)  # группируем по дате
    return sessions_by_day


from django.utils import timezone
from datetime import datetime

# Функция для создания тренировки
def create_training_session(request):
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        # Получаем данные из запроса
        date_time = request.POST.get('date_time')
        trainer_id = request.POST.get('trainer')
        member = get_object_or_404(GymMember, user=request.user)

        # Преобразуем строку времени в объект datetime
        date_time_obj = datetime.strptime(date_time, '%Y-%m-%dT%H:%M')

        # Преобразуем в объект с учётом часового пояса
        aware_date_time_obj = timezone.make_aware(date_time_obj, timezone.get_current_timezone())

        # Получаем тренера
        trainer = get_object_or_404(Trainer, id=trainer_id)

        # Создаем тренировку с указанием плана пользователя
        TrainingSession.objects.create(
            member=member,
            trainer=trainer,
            date=aware_date_time_obj,
            plan=member.plan  # передаем план, связанный с пользователем
        )

        return JsonResponse({'status': 'success', 'message': 'Тренировка записана успешно!'})

    return JsonResponse({'status': 'error', 'message': 'Что-то пошло не так!'})


# Редактирование профиля
class EditProfileView(View):
    def get(self, request):
        if request.user.is_authenticated:
            member = get_object_or_404(GymMember, email=request.user.email)
            form = GymMemberForm(instance=member)
            return render(request, 'edit_profile.html', {'form': form})
        return redirect('login')

    def post(self, request):
        member = get_object_or_404(GymMember, email=request.user.email)
        form = GymMemberForm(request.POST, request.FILES, instance=member)
        if form.is_valid():
            form.save()
            return redirect('profile')
        return render(request, 'edit_profile.html', {'form': form})

# Чат для пользователей
@login_required
def chat_view(request):
    chat_messages = ChatMessage.objects.all().order_by('-timestamp')
    user_role = UserRole.objects.filter(user=request.user).first()

    if request.method == 'POST':
        form = ChatMessageForm(request.POST, request.FILES)
        if form.is_valid():
            content = form.cleaned_data.get('content', '').strip()
            if content or form.cleaned_data.get('image'):
                ChatMessage.objects.create(
                    user=request.user,
                    content=content,
                    image=form.cleaned_data.get('image')
                )
                return redirect('chat')
            else:
                form.add_error('content', 'Сообщение не может быть пустым!')
        else:
            messages.error(request, 'Ошибка отправки сообщения: ' + str(form.errors))
    else:
        form = ChatMessageForm()

    return render(request, 'chat.html', {
        'chat_messages': chat_messages,
        'form': form,
        'user_role': user_role,
    })

# Удаление сообщения из чата
@login_required
def delete_message(request, message_id):
    message = get_object_or_404(ChatMessage, id=message_id)
    
    # Проверка прав
    user_role = UserRole.objects.filter(user=request.user).first()
    if user_role and (user_role.role in ['admin', 'trainer'] or message.user == request.user):
        message.delete()
        messages.success(request, 'Сообщение успешно удалено!')
    else:
        messages.error(request, 'У вас нет прав для удаления этого сообщения!')

    return redirect('chat')
