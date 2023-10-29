from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase
from notes.models import Note

from django.urls import reverse

User = get_user_model()


class TestRoutes(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='TestAuthor')
        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст',
            author=cls.author,
            slug='slug')

    def test_pages_availability(self):
        """Тест отображения страниц для анонимного пользователя"""

        urls = (
            ('notes:home', None),
            ('users:login', None),
            ('users:logout', None),
            ('users:signup', None),
        )
        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_availability_for_author(self):
        """Тестирование доступности страниц для авторизованного пользователя"""

        urls = (
            ('notes:edit', (self.note.slug,)),
            ('notes:detail', (self.note.slug,)),
            ('notes:delete', (self.note.slug,)),
            ('notes:add', None),
            ('notes:list', None),
            ('notes:success', None),
        )
        for name, args in urls:
            user = self.author
            self.client.force_login(user)
            with self.subTest(user=user, name=name):
                url = reverse(name, args=args)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_redirect_for_author(self):
        """Тестирование страницы редиректа для неавторизованного автора"""

        login_url = reverse('users:login')
        urls = (
            ('notes:add', None),
            ('notes:list', None),
            ('notes:success', None),
            ('notes:detail', (self.note.slug,)),
            ('notes:edit', (self.note.slug,)),
            ('notes:delete', (self.note.slug,)),
        )
        for name, args in urls:
            url = reverse(name, args=args)
            redirect_url = f'{login_url}?next={url}'
            response = self.client.get(url)
            self.assertRedirects(response, redirect_url)
