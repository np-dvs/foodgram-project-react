from django.contrib.auth.models import AbstractUser
from django.db import models

from foodgram.constants import MAIL_LENGTH, NAME_LENGTH


class User(AbstractUser):
    email = models.EmailField(max_length=MAIL_LENGTH,
                              verbose_name='Почта',
                              unique=True)
    username = models.CharField(max_length=NAME_LENGTH,
                                unique=True,
                                verbose_name='Логин')
    first_name = models.CharField(max_length=NAME_LENGTH,
                                  verbose_name='Имя')
    second_name = models.CharField(max_length=NAME_LENGTH,
                                   verbose_name='Фамилия')

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ['username']

        def __str__(self) -> str:
            return self.email
