from http import HTTPStatus

import pytest
from pytest_django.asserts import assertRedirects, assertFormError

from news.forms import BAD_WORDS, WARNING
from news.models import Comment


@pytest.mark.django_db
def test_anonymouse_user_cant_create_comment(
        detail_url,
        client,
        form_data,
        login_url
):
    """
    Тестирование анонимный пользователь не может
    создать комментарий
    """
    response = client.post(detail_url, data=form_data)
    expected_url = f'{login_url}?next={detail_url}'
    assertRedirects(response, expected_url)
    assert Comment.objects.count() == 0


def test_autorize_user_can_sent_comment(
        author,
        detail_url,
        form_data,
        news,
        user_client
):
    """
    Тестирование авторизованный пользователь может
    оставить комментарий.
    """
    response = user_client.post(detail_url, data=form_data)
    assertRedirects(response, f'{detail_url}#comments')
    assert Comment.objects.count() == 1
    comment = Comment.objects.get()
    assert comment.text == form_data['text']
    assert comment.news == news
    assert comment.author == author


def test_user_cant_use_bad_words(
        detail_url,
        user_client
):
    """
    Пользователь не может использовать в комментарии
    запрещенный слова.
    """
    bad_words_data = {'text': f'Какой-то текст, {BAD_WORDS[0]}, еще текст'}
    response = user_client.post(detail_url, data=bad_words_data)
    assertFormError(response, 'form', 'text', errors=WARNING)
    assert Comment.objects.count() == 0


def test_author_can_edit_comment(
        detail_url,
        user_client,
        form_data,
        news,
        author,
        comment
):
    """Тестирование редактирования комментария автором"""
    response = user_client.post(detail_url, form_data)
    assertRedirects(response, f'{detail_url}#comments')
    comment.refresh_from_db()
    assert comment.text == form_data['text']
    assert comment.news == news
    assert comment.author == author


def test_other_user_cant_edit_comment(
        admin_client,
        edit_url,
        form_data,
        comment
):
    """Тестирование возможности редактирования коммента другим автором."""
    response = admin_client.post(edit_url, form_data)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment_from_db = Comment.objects.get(id=comment.id)
    assert comment.text == comment_from_db.text
    assert comment.news == comment_from_db.news
    assert comment.author == comment_from_db.author


def test_user_cant_delete_comment_of_another_author(
        admin_client,
        delete_url
):
    """Тестирование невозможности удаления чужого комментария"""
    response = admin_client.post(delete_url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == 1


def test_author_can_delete_comment(
        detail_url,
        delete_url, 
        user_client
):
    """Тестирование возможности удаления своего комментария"""
    response = user_client.post(delete_url)
    assertRedirects(response, detail_url + '#comments')
    assert Comment.objects.count() == 0
