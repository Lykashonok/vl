from mixer.backend.django import mixer
import pytest

@pytest.fixture(scope='module')
def queue_sorted(request, db):
    return mixer.blend('lab_queue.Queue', queue_title = 'testqueue', queue_sort_by_enter_time = request.param)

@pytest.mark.parametrize('queue_sorted', [False], indirect=True)
def test_queue_sort_false(queue_sorted):
    assert queue_sorted.queue_sort_by_enter_time == False

@pytest.mark.parametrize('queue_sorted', [True], indirect=True)
def test_queue_sort_true(queue_sorted):
    assert queue_sorted.queue_sort_by_enter_time == True