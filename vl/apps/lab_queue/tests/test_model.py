from mixer.backend.django import mixer
import pytest

@pytest.mark.django_db
class TestModels:

    def test_queue_sort_false(self):
        queue = mixer.blend('lab_queue.Queue', queue_title = 'testqueue')
        assert queue.queue_sort_by_enter_time == False
    
    def test_queue_sort_true(self):
        queue = mixer.blend('lab_queue.Queue', queue_title = 'testqueue', queue_sort_by_enter_time = True)
        assert queue.queue_sort_by_enter_time == True