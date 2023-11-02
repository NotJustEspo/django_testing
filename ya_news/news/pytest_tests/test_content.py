import pytest

from news.forms import CommentForm

pytestmark = pytest.mark.django_db


def test_news_count(
        client,
        news_count_fixture,
        home_url
):
    """
    Тестирование количества новостей на
    главной странице.
    """
    response = client.get(home_url)
    object_list = response.context.get('object_list')
    assert object_list is not None
    assert len(object_list) <= news_count_fixture


def test_order_news(client, home_url, news):
    """Тестирование сортировки отображения новостей"""
    response = client.get(home_url)
    object_list = response.context.get('object_list')
    assert object_list is not None
    all_dates = [news.date for news in object_list]
    sorted_dates = sorted(all_dates, reverse=True)
    assert all_dates == sorted_dates


def test_comment_order(
        client,
        detail_url,
        news,
        comment_created
):
    """Тестирование сортировки комментариев."""
    response = client.get(detail_url)
    comments = response.context.get('news')
    assert comments is not None
    comments_set = news.comment_set.all()
    all_comments = [comment.created for comment in comments_set]
    sorted_comments = sorted(all_comments)
    assert all_comments == sorted_comments


def test_pages_contains_form_for_authorize_user(detail_url, user_client):
    """
    Тестирование доступности формы комментария
    авторизованному пользователю.
    """
    response = user_client.get(detail_url)
    assert 'form' in response.context
    assert isinstance(response.context['form'], CommentForm)


def test_pages_contains_form_for_non_authorize_user(client, detail_url):
    """Тестирование не доступности формы комментария анонимному пользователю"""
    response = client.get(detail_url)
    assert 'form' not in response.context
