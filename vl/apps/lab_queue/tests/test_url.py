from django.urls import reverse, resolve

class TestUrls:

    def test_detail_url(self):
        path = reverse('lab_queue:detail', kwargs={'queue_id': 1})
        assert resolve(path).view_name == 'lab_queue:detail'