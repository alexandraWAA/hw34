import logging
from datetime import timedelta
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from celery import shared_task
from celery.utils.log import get_task_logger

# Импорты моделей
from users.models import User  # <-- ДОБАВЬТЕ ЭТУ СТРОКУ
from lms.models import Course, Subscription

logger = get_task_logger(__name__)


def _send_email(subject, message, recipient_list):
    try:
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, recipient_list, fail_silently=False)
        return True
    except Exception as e:
        logger.error('Ошибка отправки письма: %s', e)
        return False


@shared_task
def send_course_update_notification(course_id, updated_fields):
    try:
        course = Course.objects.get(pk=course_id)
    except Course.DoesNotExist:
        logger.error('Курс %d не найден', course_id)
        return

    subscribers = Subscription.objects.filter(course=course, user__email__isnull=False).select_related('user')
    if not subscribers.exists():
        return

    subject = f'Обновление курса: {course.name}'
    message = f'Курс "{course.name}" был обновлен. Обновленные поля: {", ".join(updated_fields)}'

    for subscription in subscribers:
        _send_email(subject, message, [subscription.user.email])


@shared_task
def deactivate_inactive_users():
    """Деактивация пользователей, не заходивших более 30 дней"""
    thirty_days_ago = timezone.now() - timedelta(days=30)
    updated_count = User.objects.filter(
        last_login__lt=thirty_days_ago,
        is_active=True,
        is_superuser=False
    ).update(is_active=False)

    if updated_count > 0:
        logger.info('Деактивировано %d неактивных пользователей', updated_count)
    return {'deactivated': updated_count}