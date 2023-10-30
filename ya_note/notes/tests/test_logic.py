from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from pytils.translit import slugify

from notes.forms import WARNING
from notes.models import Note

User = get_user_model()


class TestNoteCreate(TestCase):
    ADD_PAGE_URL = reverse('notes:add')

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create(username='Logged user')
        cls.user2 = User.objects.create(username='Logged user2')
        cls.note = Note.objects.create(
            title='Заголовок заметки',
            text='Тект заметки',
            author=cls.user,
            slug='slug',
        )
        cls.form_data = {
            'title': 'Какой-то заголовок',
            'text': 'Какой-то текст',
            'slug': 'slug'
        }
        cls.auth_client = Client()
        cls.auth_client.force_login(cls.user)
        cls.auth_client2 = Client()
        cls.auth_client2.force_login(cls.user2)

    def test_anonymous_user_cant_create_note(self):
        """Тестирование аноним не может создать заметку."""
        Note.objects.all().delete()
        response = self.client.post(self.ADD_PAGE_URL, data=self.form_data)
        login_url = reverse('users:login')
        expected_url = f'{login_url}?next={self.ADD_PAGE_URL}'
        self.assertRedirects(response, expected_url)
        self.assertEqual(Note.objects.count(), 0)

    def test_logged_user_can_create_note(self):
        """Тестирование залогиненного пользователя
        создавать заметки.
        """
        Note.objects.all().delete()
        response = self.auth_client.post(
            self.ADD_PAGE_URL,
            data=self.form_data)
        self.assertRedirects(response, reverse('notes:success'))
        self.assertEqual(Note.objects.count(), 1)
        new_note = Note.objects.get()
        self.assertEqual(new_note.title, self.form_data['title'])
        self.assertEqual(new_note.text, self.form_data['text'])
        self.assertEqual(new_note.slug, self.form_data['slug'])
        self.assertEqual(new_note.author, self.user)

    def test_not_unique_slug(self):
        """Тестирование логики slug"""
        self.form_data['slug'] = self.note.slug
        response = self.auth_client.post(
            self.ADD_PAGE_URL,
            data=self.form_data
        )
        self.assertFormError(
            response,
            'form',
            'slug',
            errors=(self.note.slug + WARNING)
        )
        note_count = Note.objects.count()
        self.assertEqual(note_count, 1)

    def test_empty_slug(self):
        """Тестирование пустого поля slug"""
        Note.objects.all().delete()
        self.form_data.pop('slug')
        response = self.auth_client.post(
            self.ADD_PAGE_URL,
            data=self.form_data
        )
        self.assertRedirects(response, reverse('notes:success'))
        self.assertEqual(Note.objects.count(), 1)
        new_note = Note.objects.get()
        expected_slug = slugify(self.form_data['title'])
        self.assertEqual(new_note.slug, expected_slug)

    def test_other_user_cant_edit_note(self):
        """Тестирование возможности редактирования заметки
        другим залогиненным пользователем.
        """
        edit_url = reverse('notes:edit', args=(self.note.slug,))
        response = self.auth_client2.post(edit_url, self.form_data)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        note_from_db = Note.objects.get(id=self.note.id)
        self.assertEqual(self.note.title, note_from_db.title)
        self.assertEqual(self.note.text, note_from_db.text)
        self.assertEqual(self.note.slug, note_from_db.slug)

    def test_author_can_edit_note(self):
        """Тестирование редактирования заметки залогиненным
        пользователем.
        """
        edit_url = reverse('notes:edit', args=(self.note.slug,))
        response = self.auth_client.post(edit_url, self.form_data)
        self.assertRedirects(response, reverse('notes:success'))
        self.note.refresh_from_db()
        self.assertEqual(self.note.title, self.form_data['title'])
        self.assertEqual(self.note.text, self.form_data['text'])
        self.assertEqual(self.note.slug, self.form_data['slug'])

    def test_other_author_cant_delete_note(self):
        """Тестирование возможности удаления заметки
        другим залогиненным пользователем (не автор).
        """
        note_count = Note.objects.count()
        delete_url = reverse('notes:delete', args=(self.note.slug,))
        response = self.auth_client2.post(delete_url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertEqual(note_count, 1)

    def test_logged_user_can_delete_note(self):
        """Тестирование возможности удаления заметки
        залогиненным пользователем (автором).
        """
        delete_url = reverse('notes:delete', args=(self.note.slug,))
        response = self.auth_client.post(delete_url)
        self.assertRedirects(response, reverse('notes:success'))
        note_count = Note.objects.count()
        self.assertEqual(note_count, 0)
