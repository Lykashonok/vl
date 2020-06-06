from django.test import RequestFactory, Client
from django.urls import reverse
from django.contrib.auth.models import User, AnonymousUser
from mixer.backend.django import mixer
from lab_queue.views import detail
from django.test import TestCase
import pytest

@pytest.fixture(scope='module')
def factory():
    return RequestFactory()

@pytest.fixture
def new_queue(db):
    mixer.blend('lab_queue.Queue', queue_title = 'testqueue', queue_id = 1)

@pytest.fixture
def path_detail(db):
    return reverse('lab_queue:detail', kwargs={'queue_id': 1})

def test_queue_detail_authenticated(factory, new_queue, path_detail, db):
    request = factory.get(path_detail)
    request.user = mixer.blend(User)

    response = detail(request, queue_id = 1)
    assert response.status_code == 200

def test_queue_detail_non_authenticated(factory, new_queue, path_detail, db):
    request = factory.get(path_detail)
    request.user = AnonymousUser()

    response = detail(request, queue_id = 1)
    assert response.status_code == 302

def test_register(factory, new_queue, db):
    path = reverse('lab_queue:register')
    request = factory.get(path)
    request.user = AnonymousUser()
    response = detail(request)
    assert response.status_code == 302