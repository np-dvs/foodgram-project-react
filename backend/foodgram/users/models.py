from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    email = models.EmailField(max_length=200,
                              verbose_name='Почта',
                              unique=True)
    first_name = models.CharField(max_length=50,
                                  verbose_name='Имя')
    second_name = models.CharField(max_length=50,
                                   verbose_name='Фамилия')

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ['id']

        def __str__(self) -> str:
            return self.email
