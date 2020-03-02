from django.db import models

from positions import PositionField


class Topic(models.Model):

    description = models.TextField()
    update_date = models.DateTimeField(auto_now=True)
    create_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-id']


class Lesson(models.Model):

    description = models.TextField()
    topic = models.ForeignKey(
        Topic,
        models.SET_NULL,
        blank=True,
        null=True,)
    position = PositionField(collection='topic')
    update_date = models.DateTimeField(auto_now=True)
    create_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-id']
