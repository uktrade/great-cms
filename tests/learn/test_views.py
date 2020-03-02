from django.test import TestCase
from django.urls import reverse

from learn.models import Lesson


class LessonTest(TestCase):

    def test_lesson_list(self):
        response = self.client.get(reverse('core:lesson_list'))
        self.failUnlessEqual(response.status_code, 200)

    def test_lesson_crud(self):
        # Create new instance
        response = self.client.post(reverse('core:lesson_list'), {'description': 'Test', 'position': '1'})
        self.assertContains(response, '"success": "true"')

        # Read instance
        items = Lesson.objects.all()
        self.failUnlessEqual(items.count(), 1)
        item = items[0]
        response = self.client.get(reverse('core:lesson_details', kwargs={'id': item.id}))

        self.failUnlessEqual(response.status_code, 200)

        # Update instance
        response = self.client.post(
            reverse('core:lesson_details', kwargs={'id': item.id}),
            {'description': 'Test 2', 'position': '2'}
        )
        self.assertContains(response, '"success": "true"')

        # Delete instance
        response = self.client.post(reverse('core:lesson_delete', kwargs={'id': item.id}), {})
        self.assertContains(response, '"success": "true"')
        items = Lesson.objects.all()
        self.failUnlessEqual(items.count(), 0)
