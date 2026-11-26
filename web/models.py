from django.db import models
from django.contrib.auth.models import User

class Partner(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name="Пользователь")
    phone = models.CharField(max_length=20, verbose_name="Телефон")
    is_active = models.BooleanField(default=True, verbose_name="Активен")
    offer_accepted_at = models.DateTimeField(null=True, blank=True, verbose_name="Оферта принята")

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} ({self.phone})"

    class Meta:
        verbose_name = "Партнёр"
        verbose_name_plural = "Партнёры"


class Post(models.Model):
    title = models.CharField(max_length=200, verbose_name="Заголовок")
    text = models.TextField(verbose_name="Текст статьи (используйте ## для заголовков H2 и ### для H3)")
    meta_description = models.CharField(max_length=255, blank=True, verbose_name="SEO описание (Description)", help_text="Если оставить пустым, заполнится автоматически из начала статьи")
    keywords = models.CharField(max_length=255, blank=True, verbose_name="SEO-теги (через запятую)", help_text="Например: АУСН, 1С:Фреш, бухгалтерия ИП")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата публикации")
    is_published = models.BooleanField(default=False, verbose_name="Опубликовано")

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Статья"
        verbose_name_plural = "Статьи"


class Review(models.Model):
    name = models.CharField(max_length=100, verbose_name="Имя")
    text = models.TextField(verbose_name="Текст отзыва")
    rating = models.IntegerField(default=5, verbose_name="Оценка (1-5)")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата")
    is_published = models.BooleanField(default=False, verbose_name="Опубликовано")

    def __str__(self):
        return f"{self.name} ({self.rating}★)"

    class Meta:
        verbose_name = "Отзыв"
        verbose_name_plural = "Отзывы"


class Ticket(models.Model):
    STATUS_CHOICES = [
        ('new', 'Новая'),
        ('in_progress', 'В работе'),
        ('on_review', 'На проверке'),
        ('closed', 'Закрыта'),
    ]

    client_name = models.CharField(max_length=100, verbose_name="Имя клиента")
    phone = models.CharField(max_length=20, verbose_name="Телефон")
    subject = models.CharField(max_length=200, verbose_name="Тема")
    description = models.TextField(verbose_name="Описание")
    priority = models.CharField(max_length=10, choices=[('normal', 'Обычно'), ('urgent', 'Срочно')], default='normal', verbose_name="Приоритет")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new', verbose_name="Статус")

    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, verbose_name="Пользователь")
    partner = models.ForeignKey(Partner, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Партнёр")
    result = models.TextField(blank=True, null=True, verbose_name="Результат обработки")
    time_limit = models.IntegerField(default=600, verbose_name="Лимит времени (мин)")
    time_spent = models.IntegerField(default=0, verbose_name="Затрачено времени (мин)")
    revision_comment = models.TextField(blank=True, null=True, verbose_name="Комментарий на доработку")

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

    @property
    def remaining_time(self):
        return self.time_limit - self.time_spent

    def __str__(self):
        return f"{self.subject} - {self.client_name}"

    class Meta:
        verbose_name = "Заявка"
        verbose_name_plural = "Заявки"


class Joke(models.Model):
    name = models.CharField(max_length=100, verbose_name="Имя автора")
    text = models.TextField(verbose_name="Текст шутки")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата")
    is_published = models.BooleanField(default=False, verbose_name="Опубликована")

    def __str__(self):
        return f"{self.name}: {self.text[:30]}..."

    class Meta:
        verbose_name = "Шутка"
        verbose_name_plural = "Шутки"


class Lead(models.Model):
    name = models.CharField(max_length=100, verbose_name="Имя")
    phone = models.CharField(max_length=20, verbose_name="Телефон")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    is_processed = models.BooleanField(default=False, verbose_name="Обработано")

    def __str__(self):
        return f"{self.name} ({self.phone})"

    class Meta:
        verbose_name = "Заявка (с сайта)"
        verbose_name_plural = "Заявки (с сайта)"



class HexJoke(Joke):
    class Meta:
        proxy = True
        verbose_name = "Анекдот (HEX)"
        verbose_name_plural = "Анекдоты (HEX)"
