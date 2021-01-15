from unittest import mock

from django.test import override_settings

from domestic.wagtail_hooks import editor_css, global_admin_css


def _fake_static(value):
    return '/path/to/static/' + value


@mock.patch('domestic.wagtail_hooks.static')
def test_editor_css(mock_static):
    mock_static.side_effect = _fake_static
    assert editor_css() == '<link rel="stylesheet" href="/path/to/static/cms-admin/css/domestic-editor.css">'


@override_settings(ENVIRONMENT_CSS_THEME_FILE='')  # '' is the default
@mock.patch('domestic.wagtail_hooks.static')
def test_global_admin_css__no_customisation(mock_static):
    mock_static.side_effect = _fake_static
    assert global_admin_css() == '<link rel="stylesheet" href="/path/to/static/cms-admin/css/domestic.css">'


@override_settings(ENVIRONMENT_CSS_THEME_FILE='path/to/custom/file.css')
@mock.patch('domestic.wagtail_hooks.static')
def test_global_admin_css__with_customisation(mock_static):
    mock_static.side_effect = _fake_static

    assert global_admin_css() == (
        '<link rel="stylesheet" href="/path/to/static/cms-admin/css/domestic.css">'
        '<link rel="stylesheet" href="/path/to/static/path/to/custom/file.css">'
    )
