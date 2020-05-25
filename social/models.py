from django.contrib.auth.models import User
from django.contrib.humanize.templatetags.humanize import naturaltime
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.urls import reverse
from django.utils import timezone
from datetime import datetime
from django.utils.translation import gettext_lazy as _

GENDER_CHOICES = [
    ['male', u"Мужской"],
    ['female', u"Женский"],
]

REL_CHOICES = [
    ['none', u"Не определенно"],
    ['single', u"Холост"],
    ['in_a_rel', u"В отношениях"],
    ['engaged', u"Помолвлен(а)"],
    ['married', u"Женат/Замужем"],
    ['in_love', u"Влюблен(а)"],
    ['complicated', u"Все сложно"],
]


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name=u"Пользователь")
    avatar = models.FileField(verbose_name=u"Аватар", null=True, blank=True)
    bio = models.TextField(max_length=500, blank=True, null=True, verbose_name=u"О себе")
    city = models.CharField(max_length=30, blank=True, null=True, verbose_name=u"Город")
    birth_date = models.DateField(null=True, blank=True, verbose_name=u"Дата рождения")
    gender = models.CharField(max_length=10, verbose_name=u"Пол", choices=GENDER_CHOICES, default="male")
    relationship = models.CharField(max_length=20, verbose_name=u"Статус отношений",
                                    choices=REL_CHOICES, default="none")
    likes = models.ManyToManyField(User, related_name='likes', blank=True)
    last_online = models.DateTimeField(blank=True, null=True)
    USERNAME_FIELD = 'username'

    class Meta:
        verbose_name = 'User'

    @receiver(post_save, sender=User)
    def create_user_profile(sender, instance, created, **kwargs):
        if created:
            Profile.objects.create(user=instance)

    def __str__(self):
        return str(self.user) if self.user else ''

    def get_absolute_url(self):
        return reverse('user_detail', args=[self.pk])

    def total_likes(self):
        return self.likes.count()

    def age(self):
        return int((datetime.now().date() - self.birth_date).days / 365.25)

    def is_online(self):
        if self.last_online:
            return (
                timezone.now() - self.last_online) < timezone.timedelta(
                minutes=15)
        return False

    def get_online_info(self):
        if self.is_online():
            return 'Online'
        if self.last_online:
            return 'Last visit {}'.format(naturaltime(self.last_online))
        return 'Unknown'


class Chat(models.Model):
    DIALOG = 'D'
    CHAT = 'C'
    CHAT_TYPE_CHOICES = [
        (DIALOG, _('Dialog')),
        (CHAT, _('Chat'))
    ]

    type = models.CharField(
        max_length=1,
        choices=CHAT_TYPE_CHOICES,
        default=DIALOG)
    members = models.ManyToManyField(Profile, verbose_name=_("Участник"))

    def get_absolute_url(self):
        return 'meeting:messages', (), {'chat_id': self.pk}


class Message(models.Model):
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE)
    author = models.ForeignKey(Profile, on_delete=models.CASCADE)
    message = models.TextField()
    pub_date = models.DateTimeField(default=timezone.now)
    is_readed = models.BooleanField(default=False)

    class Meta:
        ordering = ['pub_date']

    def __str__(self):
        return self.message
