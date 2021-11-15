from io import BytesIO

import PIL.Image
from django.core.files.images import ImageFile
from django.test import TestCase
from wagtail.core.models import Collection
from wagtail.tests.utils.wagtail_tests import WagtailTestUtils

from core import models
from core.admin import ImageAdmin


def get_test_image_file(filename='test.png', colour='white', size=(640, 480)):
    f = BytesIO()
    image = PIL.Image.new('RGBA', size, colour)
    image.save(f, 'PNG')
    return ImageFile(f, name=filename)


class ImageAdminTests(TestCase, WagtailTestUtils, ImageAdmin):
    def setUp(self):
        self.login()

    def test_size(self):
        evil_plans_collection = Collection.objects.create(name="Evil plans", depth=1)

        image = models.AltTextImage.objects.create(
            title="Test image", file=get_test_image_file(), collection=evil_plans_collection, file_size=512000
        )
        size = self.size(image)
        self.assertEqual(size, "500KB")
