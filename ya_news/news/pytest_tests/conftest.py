import pytest
from django.urls import reverse
from django.test.client import Client

from news.models import News, Comment


@pytest.fixture
def author(django_user_model):
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def user_client(author):
    client = Client()
    client.force_login(author)
    return client


@pytest.fixture
def news(author):
    return News.objects.create(
        title='Заголовок',
        text='Текст публикации'
    )


@pytest.fixture
def comment(author, news):
    return Comment.objects.create(
        news=news,
        author=author,
        text='Текст комментария'
    )


@pytest.fixture
def form_data(author, news):
    return {
        'news': news,
        'author': author,
        'text': 'Текст комментария'
    }


@pytest.fixture
def comment_id(comment):
    return (comment.id,)


@pytest.fixture
def home_url():
    return reverse('news:home')


@pytest.fixture
def detail_url(news):
    return reverse('news:detail', args=(news.id,))


@pytest.fixture
def edit_url(comment):
    return reverse('news:edit', args=(comment.id,))


@pytest.fixture
def delete_url(comment):
    return reverse('news:delete', args=(comment.id,))


@pytest.fixture
def login_url():
    return reverse('users:login')


@pytest.fixture
def logout_url():
    return reverse('users:logout')


@pytest.fixture
def signup_url():
    return reverse('users:signup')