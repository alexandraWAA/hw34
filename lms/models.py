from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator
from lms.validators import validate_youtube_url


class Course(models.Model):
    name = models.CharField(max_length=200, verbose_name='Название')
    preview = models.ImageField(upload_to='course_previews/', blank=True, null=True, verbose_name='Превью')
    description = models.TextField(blank=True, null=True, verbose_name='Описание')
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='courses', verbose_name='Владелец', null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0, validators=[MinValueValidator(0)], verbose_name='Цена')
    stripe_product_id = models.CharField(max_length=255, blank=True, null=True, verbose_name='ID продукта в Stripe')
    stripe_price_id = models.CharField(max_length=255, blank=True, null=True, verbose_name='ID цены в Stripe')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Курс'
        verbose_name_plural = 'Курсы'

    def __str__(self):
        return self.name


class Lesson(models.Model):
    name = models.CharField(max_length=200, verbose_name='Название')
    description = models.TextField(blank=True, null=True, verbose_name='Описание')
    preview = models.ImageField(upload_to='lesson_previews/', blank=True, null=True, verbose_name='Превью')
    video_url = models.URLField(blank=True, null=True, validators=[validate_youtube_url], verbose_name='Ссылка на видео')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='lessons', verbose_name='Курс')
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='lessons', verbose_name='Владелец', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Урок'
        verbose_name_plural = 'Уроки'

    def __str__(self):
        return f"{self.name} ({self.course.name})"


class Subscription(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='subscriptions', verbose_name='Пользователь')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='subscriptions', verbose_name='Курс')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'course']
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'


class Payment(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='payments', verbose_name='Пользователь')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='payments', verbose_name='Курс')
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Сумма')
    stripe_session_id = models.CharField(max_length=255, blank=True, null=True)
    stripe_payment_intent_id = models.CharField(max_length=255, blank=True, null=True)
    payment_url = models.URLField(max_length=500, blank=True, null=True)
    status = models.CharField(max_length=50, default='pending', choices=[('pending', 'Ожидает'), ('paid', 'Оплачен'), ('failed', 'Ошибка')])
    created_at = models.DateTimeField(auto_now_add=True)
    paid_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        verbose_name = 'Платеж'
        verbose_name_plural = 'Платежи'