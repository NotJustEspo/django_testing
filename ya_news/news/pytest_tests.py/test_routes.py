import pytest

from http import HTTPStatus
from pytest_django.asserts import assertRedirects

from django.urls import reverse

pytestmark = pytest.mark.django_db


@pytest.mark.parametrize(
        'name, expected_status',
        (
            ('news:home', HTTPStatus.OK),
            ('users:login', HTTPStatus.OK),
            ('users:logout', HTTPStatus.OK),
            ('users:signup', HTTPStatus.OK),
        ),
)
def test_home_availability_for_anonymous_user(client, name, expected_status):
    """Тестирование доступности главной страницы
    анонимному пользователю"""
    url = reverse(name)
    response = client.get(url)
    assert response.status_code == expected_status


def test_detail_page_availability_for_anonymous_user(client, news):
    """Тестирование доступности страницы отдельной
    новости анонимному пользователю"""
    url = reverse('news:detail', args=(news.id,))
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
        'parametrize_client, expected_status',
        (
            (pytest.lazy_fixture('admin_client'), HTTPStatus.NOT_FOUND),
            (pytest.lazy_fixture('author_client'), HTTPStatus.OK)
        )
)
@pytest.mark.parametrize(
    'name',
    ('news:edit', 'news:delete'),
)
def test_availability_for_comment_edit_and_delete(
    parametrize_client,
    name,
    comment,
    expected_status
):
    """Тестирование удаление и реадктирования комментария
    автору комментария."""
    url = reverse(name, args=(comment.id,))
    response = parametrize_client.get(url)
    assert response.status_code == expected_status


@pytest.mark.parametrize(
    'name, args',
    (
        ('news:edit', pytest.lazy_fixture('comment_id')),
        ('news:delete', pytest.lazy_fixture('comment_id')),
    )
)
def test_redirect_for_anonymous_client(client, name, args):
    """Тестирование редиректа анонимного пользователя
    при попытке удаления или редактирования комментария."""
    login_url = reverse('users:login')
    url = reverse(name, args=args)
    expected_url = f'{login_url}?next={url}'
    response = client.get(url)
    assertRedirects(response, expected_url)
