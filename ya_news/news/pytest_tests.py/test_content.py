import pytest

from datetime import timedelta
from django.conf import settings
from django.utils import timezone
from django.urls import reverse
from news.models import Comment

pytestmark = pytest.mark.django_db


def test_news_count(client):
    """Тестирование количества новостей на"""
    """главной странице."""
    home_url = reverse('news:home')
    response = client.get(home_url)
    object_list = response.context['object_list']
    news_count = len(object_list)
    assert news_count <= settings.NEWS_COUNT_ON_HOME_PAGE


def test_order_news(client):
    """Тестирование сортировки отображения новостей"""
    home_url = reverse('news:home')
    response = client.get(home_url)
    object_list = response.context['object_list']
    all_dates = [news.date for news in object_list]
    sorted_dates = sorted(all_dates, reverse=True)
    assert all_dates == sorted_dates


def test_comment_order(client, news, author):
    """Тестирование сортировки комментариев."""
    now = timezone.now()
    for index in range(2):
        comment = Comment.objects.create(
            news=news,
            author=author,
            text=f'Текст {index}',
        )
        comment.created = now + timedelta(days=index)
        comment.save()
    detail_url = reverse('news:detail', args=(news.id,))
    response = client.get(detail_url)
    assert 'news' in response.context
    news = response.context['news']
    all_comments = news.comment_set.all()
    assert all_comments[0].created < all_comments[1].created


def test_pages_contains_form_for_authorize_user(author_client, news):
    """Тестирование доступности формы комментария авторизованному пользователю"""
    url = reverse('news:detail', args=(news.id,))
    response = author_client.get(url)
    assert 'form' in response.context


def test_pages_contains_form_for_non_authorize_user(client, news):
    """Тестирование не доступности формы комментария анонимному пользователю"""
    url = reverse('news:detail', args=(news.id,))
    response = client.get(url)
    assert 'form' not in response.context
