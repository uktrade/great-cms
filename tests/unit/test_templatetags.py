from unittest import mock

from core.templatetags.personalised_blocks import render_video_block
from core.templatetags.video_tags import render_video


def test_render_video_block_tag():
    video_mock = mock.Mock(
        sources=[{'src': '/media/foo.mp4', 'type': 'video/mp4'}]
    )
    block = dict(
        width=20,
        height=20,
        video=video_mock
    )
    html = render_video_block(block)

    assert '<video width="20" height="20" controls>' in html
    assert '<source src="/media/foo.mp4" type="video/mp4">' in html
    assert 'Your browser does not support the video tag.' in html


def test_render_video_tag():
    video_mock = mock.Mock(
        sources=[{'src': '/media/foo.mp4', 'type': 'video/mp4'}]
    )
    block = dict(
        video=video_mock
    )
    html = render_video(block)

    assert '<video controls>' in html
    assert '<source src="/media/foo.mp4" type="video/mp4">' in html
    assert 'Your browser does not support the video tag.' in html


def test_empty_block_render_video_tag():

    block = dict()
    html = render_video(block)
    assert '' in html
