from django.test import RequestFactory, Client
from django.urls import reverse
from django.contrib.auth.models import User, AnonymousUser
from mixer.backend.django import mixer
from lab_queue.views import detail
from django.test import TestCase
import pytest


@pytest.fixture
def setUp():
    mixer.blend('lab_queue.Queue', queue_title = 'testqueue', queue_id = 1)

@pytest.mark.django_db
class TestViews(TestCase):

    @classmethod 
    def setUpClass(cls):
        super(TestViews, cls).setUpClass()
        cls.factory = RequestFactory()

    def test_queue_detail_authenticated(self):
        path = reverse('lab_queue:detail', kwargs={'queue_id': 1})
        request = self.factory.get(path)
        request.user = mixer.blend(User)

        response = detail(request, queue_id = 1)
        assert response.status_code == 200
    
    def test_queue_detail_non_authenticated(self):
        path = reverse('lab_queue:detail', kwargs={'queue_id': 1})
        request = self.factory.get(path)
        request.user = AnonymousUser()

        response = detail(request, queue_id = 1)
        assert response.status_code == 302

    def test_register(self):
        path = reverse('lab_queue:register')
        request = self.factory.get(path)
        request.user = AnonymousUser()
        # c = Client()
        # c.post('lab_queue:register/', {''})
        response = detail(request)
        assert response.status_code == 302