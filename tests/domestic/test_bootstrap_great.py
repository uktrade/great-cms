import pytest
from django.contrib.auth import get_user_model
from django.core.management import call_command
from wagtail.core.models import Site, Page
from wagtail_factories import PageFactory, SiteFactory

from domestic.models import DomesticHomePage

User = get_user_model()


@pytest.mark.django_db
def test_bootstrap_great(root_page):
    # re-create the same pages and site structure wagtail does
    welcome_page = PageFactory(parent=root_page)
    SiteFactory(root_page=welcome_page, id=1)

    call_command('bootstrap_great')
    assert DomesticHomePage.objects.filter(slug='homepage').exists()
    assert not Page.objects.filter(pk=2).exists()
    homepage = DomesticHomePage.objects.get(slug='homepage')
    site = Site.objects.get(pk=1)
    assert site.root_page_id == homepage.pk
    # check user has been created
    assert User.objects.filter(username='test').exists()
    user = User.objects.get(username='test')
    assert user.is_active
    assert user.is_staff
    assert user.is_superuser
    assert user.check_password('password')
