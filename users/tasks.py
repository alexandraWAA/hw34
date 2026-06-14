import logging
from datetime import timedelta
from django.utils import timezone
from celery import shared_task
from celery.utils.log import get_task_logger
from users.models import User

logger = get_task_logger(__name__)


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