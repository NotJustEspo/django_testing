import pytest
from http import HTTPStatus

from pytest_django.asserts import assertRedirects, assertFormError
from django.urls import reverse

from news.models import News, Comment
from news.forms import BAD_WORDS, WARNING


@pytest.mark.django_db
def test_anonymouse_user_cant_create_comment(client, news, form_data):
    """Тестирование анонимный пользователь не может
    создать комментарий"""
    url = reverse('news:detail', args=(news.id,))
    response = client.post(url, data=form_data)
    login_url = reverse('users:login')
    expected_url = f'{login_url}?next={url}'
    assertRedirects(response, expected_url)
    assert Comment.objects.count() == 0


def test_autorize_user_can_sent_comment(
        author_client,
        form_data,
        news,
        author
):
    """Тестирование авторизованный пользователь может
    оставить комментарий."""
    url = reverse('news:detail', args=(news.id,))
    response = author_client.post(url, data=form_data)
    assertRedirects(response, f'{url}#comments')
    assert Comment.objects.count() == 1
    comment = Comment.objects.get()
    assert comment.text == form_data['text']
    assert comment.news == news
    assert comment.author == author


def test_user_cant_use_bad_words(author_client, news, form_data):
    """Пользователь не может использовать в комментарии
    запрещенный слова."""
    url = reverse('news:detail', args=(news.id,))
    bad_words_data = {'text': f'Какой-то текст, {BAD_WORDS[0]}, еще текст'}
    response = author_client.post(url, data=bad_words_data)
    assertFormError(response, 'form', 'text', errors=WARNING)
    assert Comment.objects.count() == 0


def test_author_can_edit_comment(
        author_client,
        form_data,
        news,
        author, 
        comment
):
    """Тестирование редактирования комментария автором"""
    url = reverse('news:detail', args=(news.id,))
    response = author_client.post(url, form_data)
    assertRedirects(response, f'{url}#comments')
    comment.refresh_from_db()
    assert comment.text == form_data['text']
    assert comment.news == news
    assert comment.author == author


def test_other_user_cant_edit_comment(admin_client, form_data, news, comment):
    """Тестирование возможности редактирования коммента другим автором."""
    url = reverse('news:edit', args=(news.id,))
    response = admin_client.post(url, form_data)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment_from_db = Comment.objects.get(id=comment.id)
    assert comment.text == comment_from_db.text
    assert comment.news == comment_from_db.news
    assert comment.author == comment_from_db.author


def test_user_cant_delete_comment_of_another_author(admin_client, comment_id):
    """Тестирование невозможности удаления чужого комментария"""
    url = reverse('news:delete', args=comment_id)
    response = admin_client.post(url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == 1


def test_author_can_delete_comment(author_client, comment_id, news):
    """Тестирование возможности удаления своего комментария"""
    news_url = reverse('news:detail', args=(news.id,))
    url = reverse('news:delete', args=comment_id)
    response = author_client.post(url)
    assertRedirects(response, news_url + '#comments')
    assert Comment.objects.count() == 0
