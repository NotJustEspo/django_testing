from http import HTTPStatus

from django.urls import reverse
from django.contrib.auth import get_user_model
from django.test import TestCase

from notes.models import Note

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
        cls.home_url = reverse('notes:home', None)
        cls.login_url = reverse('users:login', None)
        cls.logout_url = reverse('users:logout', None)
        cls.signup_url = reverse('users:signup', None)
        cls.add_url = reverse('notes:add', None)
        cls.list_url = reverse('notes:list', None)
        cls.success_url = reverse('notes:success', None)
        cls.edit_url = reverse('notes:edit', args=(cls.note.slug,))
        cls.detail_url = reverse('notes:detail', args=(cls.note.slug,))
        cls.delete_url = reverse('notes:delete', args=(cls.note.slug,))

    def test_pages_availability(self):
        """Тест отображения страниц для анонимного пользователя"""
        urls = (
            self.home_url,
            self.login_url,
            self.logout_url,
            self.signup_url,
        )
        for elem in urls:
            with self.subTest(elem=elem):
                response = self.client.get(elem)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_availability_for_author(self):
        """Тестирование доступности страниц для авторизованного пользователя"""
        urls = (
            self.edit_url,
            self.detail_url,
            self.delete_url,
            self.add_url,
            self.list_url,
            self.success_url,
        )
        for elem in urls:
            user = self.author
            self.client.force_login(user)
            with self.subTest(user=user, elem=elem):
                response = self.client.get(elem)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_redirect_for_author(self):
        """Тестирование страницы редиректа для неавторизованного автора"""
        login_url = reverse('users:login')
        urls = (
            self.add_url,
            self.list_url,
            self.success_url,
            self.detail_url,
            self.edit_url,
            self.delete_url,
        )
        for elem in urls:
            redirect_url = f'{login_url}?next={elem}'
            response = self.client.get(elem)
            self.assertRedirects(response, redirect_url)
