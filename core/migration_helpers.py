"""This function is core to a data migration that updates the page tree to use
the new TopicPage model.

It takes information from CuratedListPage.topics (a CuratedTopicBlock instance)
and uses that to:

1) For EACH `topic` within the CuratedTopicBlock add one new TopicPage (using the
title of the `topic`) as a child of the CuratedListPage instance

2) For EACH `topic` within the CuratedTopicBlock, for EACH item featured
within it:
   a) if it is a lesson, move that lesson (DetailPage) to be a child of the
   relevant TopicPage,
   B) if it is a placeholder, create a LessonPlaceholderPage, using the title
   from the data, to be a child of the relevant TopicPage,
all the while ensuring the order of the children of the TopicPage is the same as the
order they were in when represented by a CuratedTopicBlock

"""

from django.db import transaction


from core.models import (
    CuratedListPage,
    TopicPage,
    LessonPlaceholderPage,
)


def _reparent_lesson(lesson, new_parent):
    lesson.move(new_parent, pos='last-child', user=None)


def _add_placeholder(placeholder_name, new_parent):
    placeholder_page = LessonPlaceholderPage(title=placeholder_name)  # Unsaved
    new_parent.add_child(instance=placeholder_page)  # ...because saved here
    placeholder_page.refresh_from_db()
    assert placeholder_page.id is not None


@transaction.atomic
def create_topics_and_reparent_lessons():
    curated_list_pages = CuratedListPage.objects.all()
    for clp in curated_list_pages:
        for topic_block in clp.topics:
            # 1. Create TopicPage with existing title
            topic_title = topic_block.value['title']  # meant to fail hard
            topic_page = TopicPage(title=topic_title)  # NB unsaved at the moment
            clp.add_child(instance=topic_page)  # ...because THIS saves and sets the path and depth
            topic_page.refresh_from_db()
            assert topic_page.pk is not None

            # 2. Reparent module's lessons, adding placeholder pages where required
            for item in topic_block.value.get('lessons_and_placeholders', []):
                if item.block_type == 'lesson':
                    _reparent_lesson(
                        lesson=item.value,
                        new_parent=topic_page,
                    )
                elif item.block_type == 'placeholder':
                    _add_placeholder(
                        placeholder_name=item.value['title'],  # again meant to fail hard
                        new_parent=topic_page,
                    )
