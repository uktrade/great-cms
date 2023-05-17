from unittest import mock

from directory_forms_api_client import actions

from international_online_offer.core import filter_tags, helpers


def test_find_articles_based_on_tags():
    tag = type(
        'obj',
        (object,),
        {'name': 'tag1'},
    )
    tag2 = type(
        'obj',
        (object,),
        {'name': 'tag2'},
    )

    tag3 = type(
        'obj',
        (object,),
        {'name': filter_tags.SUPPORT_AND_INCENTIVES},
    )

    tag4 = type(
        'obj',
        (object,),
        {'name': filter_tags.OPPORTUNITY},
    )

    specific = type(
        'obj',
        (object,),
        {'tags': [tag, tag2]},
    )

    specific2 = type(
        'obj',
        (object,),
        {'tags': [tag3]},
    )

    specific3 = type(
        'obj',
        (object,),
        {'tags': [tag, tag4]},
    )

    article = type(
        'obj',
        (object,),
        {'specific': specific},
    )

    article2 = type(
        'obj',
        (object,),
        {'specific': specific},
    )

    article3 = type(
        'obj',
        (object,),
        {'specific': specific2},
    )

    article4 = type(
        'obj',
        (object,),
        {'specific': specific3},
    )

    articles = []
    articles.append(article)
    articles.append(article2)
    articles.append(article3)
    articles.append(article4)

    assert len(helpers.find_get_to_know_market_articles(articles, 'tag1', ['tag2'])) == 2
    assert len(helpers.find_get_support_and_incentives_articles(articles)) == 1
    assert len(helpers.find_opportunities_articles(articles, 'tag1')) == 1
    assert helpers.find_get_to_know_market_articles([], '', []) == []
    assert helpers.find_get_support_and_incentives_articles([]) == []
    assert helpers.find_opportunities_articles([], '') == []


def test_concat_filters():
    assert helpers.concat_filters('test', ['test']) == ['test', 'test']


@mock.patch.object(actions, 'GovNotifyEmailAction')
def test_send_eyb_welcome_notification(mock_action_class, settings):
    helpers.send_welcome_notification(email='jim@example.com', form_url='foo')

    assert mock_action_class.call_count == 1
    assert mock_action_class.call_args == mock.call(
        template_id=settings.EYB_ENROLMENT_WELCOME_TEMPLATE_ID,
        email_address='jim@example.com',
        form_url='foo',
    )
    assert mock_action_class().save.call_count == 1
