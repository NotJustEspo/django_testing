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
        response = self.client.post(self.ADD_PAGE_URL, data=self.form_data)
        login_url = reverse('users:login')
        expected_url = f'{login_url}?next={self.ADD_PAGE_URL}'
        self.assertRedirects(response, expected_url)

    def test_logged_user_can_create_note(self):
        """Тестирование залогиненного пользователя
        создавать заметки."""
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
        note = Note.objects.create(
            title='Заголовок заметки',
            text='Тект заметки',
            author=self.user,
            slug='slug',
        )
        self.form_data['slug'] = note.slug
        response = self.auth_client.post(
            self.ADD_PAGE_URL,
            data=self.form_data
        )
        self.assertFormError(
            response,
            'form',
            'slug',
            errors=(note.slug + WARNING)
        )
        self.assertEqual(Note.objects.count(), 1)

    def test_empty_slug(self):
        """Тестирование пустого поля slug"""
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
        другим залогиненным пользователем."""
        note = Note.objects.create(
            title='Заголовок заметки',
            text='Тект заметки',
            author=self.user,
            slug='slug',
        )
        edit_url = reverse('notes:edit', args=(note.slug,))
        response = self.auth_client2.post(edit_url, self.form_data)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        note_from_db = Note.objects.get(id=note.id)
        self.assertEqual(note.title, note_from_db.title)
        self.assertEqual(note.text, note_from_db.text)
        self.assertEqual(note.slug, note_from_db.slug)

    def test_author_can_edit_note(self):
        """Тестирование редактирования заметки залогиненным
        пользователем"""
        note = Note.objects.create(
            title='Заголовок заметки',
            text='Тект заметки',
            author=self.user,
            slug='slug',
        )
        edit_url = reverse('notes:edit', args=(note.slug,))
        response = self.auth_client.post(edit_url, self.form_data)
        self.assertRedirects(response, reverse('notes:success'))
        note.refresh_from_db()
        self.assertEqual(note.title, self.form_data['title'])
        self.assertEqual(note.text, self.form_data['text'])
        self.assertEqual(note.slug, self.form_data['slug'])

    def test_other_author_cant_delete_note(self):
        """Тестирование возможности удаления заметки
        другим залогиненным пользователем (не автор)."""
        note = Note.objects.create(
            title='Заголовок заметки',
            text='Тект заметки',
            author=self.user,
            slug='slug',
        )
        delete_url = reverse('notes:delete', args=(note.slug,))
        response = self.auth_client2.post(delete_url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertEqual(Note.objects.count(), 1)

    def test_logged_user_can_delete_note(self):
        """Тестирование возможности удаления заметки
        залогиненным пользователем (автором)."""
        note = Note.objects.create(
            title='Заголовок заметки',
            text='Тект заметки',
            author=self.user,
            slug='slug',
        )
        delete_url = reverse('notes:delete', args=(note.slug,))
        response = self.auth_client.post(delete_url)
        self.assertRedirects(response, reverse('notes:success'))
        self.assertEqual(Note.objects.count(), 0)
