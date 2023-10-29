from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class TestList(TestCase):
    LIST_URL = reverse('notes:list')

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор Саша')
        cls.author2 = User.objects.create(username='Автор Петя')
        cls.note = Note.objects.create(
            title='Заголовок',
            text='Просто текст',
            author=cls.author,
            slug='any_slug'
        )

    def test_authorized_author_form(self):
        """Тестирование передачи формы на страницу
        создания заметок и редактирования.
        """
        urls = (
            ('notes:add', None),
            ('notes:edit', (self.note.slug,)),
        )
        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                self.client.force_login(self.author)
                response = self.client.get(url)
                self.assertIn('form', response.context)

    def test_note_in_list_for_author(self):
        """Тестирование отображения записи в листе автора."""
        self.client.force_login(self.author)
        response = self.client.get(self.LIST_URL)
        object_list = response.context['object_list']
        self.assertIn(self.note, object_list)

    def test_note_not_in_list_for_another_author(self):
        """Тестирование недоступности чужих заметок
        у других авторов.
        """
        self.client.force_login(self.author2)
        response = self.client.get(self.LIST_URL)
        object_list = response.context['object_list']
        self.assertNotIn(self.note, object_list)
