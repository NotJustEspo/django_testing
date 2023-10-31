from http import HTTPStatus

import pytest
from pytest_django.asserts import assertRedirects

pytestmark = pytest.mark.django_db

HOME_URL = pytest.lazy_fixture('home_url')
DETAIL_URL = pytest.lazy_fixture('detail_url')
EDIT_URL = pytest.lazy_fixture('edit_url')
DELETE_URL = pytest.lazy_fixture('delete_url')
LOGIN_URL = pytest.lazy_fixture('login_url')
LOGOUT_URL = pytest.lazy_fixture('logout_url')
SIGNUP_URL = pytest.lazy_fixture('signup_url')


@pytest.mark.parametrize(
    'url',
    (HOME_URL, LOGIN_URL, LOGOUT_URL, SIGNUP_URL, DETAIL_URL)
)
def test_pages_availability_for_anonymous_user(client, url):
    """
    Тестирование доступности главной страницы
    анонимному пользователю.
    """
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    'parametrize_client, expected_status',
    (
        (pytest.lazy_fixture('admin_client'), HTTPStatus.NOT_FOUND),
        (pytest.lazy_fixture('user_client'), HTTPStatus.OK),
    )
)
@pytest.mark.parametrize(
    'url',
    (EDIT_URL, DELETE_URL),
)
def test_availability_for_comment_edit_and_delete(
        parametrize_client,
        url,
        expected_status
):
    """
    Тестирование удаления и редактирования комментария
    автору комментария.
    """
    response = parametrize_client.get(url)
    assert response.status_code == expected_status


@pytest.mark.parametrize(
    'name',
    (EDIT_URL, DELETE_URL),
)
def test_redirect_for_anonymous_client(client, name, login_url):
    """
    Тестирование редиректа анонимного пользователя
    при попытке удаления или редактирования комментария.
    """
    expected_url = f'{login_url}?next={name}'
    response = client.get(name)
    assertRedirects(response, expected_url)
