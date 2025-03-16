import pytest
from bs4 import BeautifulSoup

from gds_tooling import forms
from sso_profile.enrolment import widgets

pytestmark = pytest.mark.django_db


def assert_html_equal(expected_html, actual_html):
    actual = BeautifulSoup(actual_html, 'html.parser')
    expected = BeautifulSoup(expected_html, 'html.parser')

    assert list(actual.stripped_strings) == list(expected.stripped_strings)


def test_choice_field_help_text_widget():
    class Form(forms.Form):
        a = forms.ChoiceField(
            label='',
            widget=widgets.RadioSelect(help_text={'foo': 'Helptext for foo', 'bar': 'Helptext for bar'}),
            choices=(('foo', 'foo label'), ('bar', 'bar label'), ('baz', 'baz label')),
        )

    span_class = 'border-light-grey padding-left-30 padding-top-15 padding-bottom-15'
    expected = """
    <p class=" form-group">
        <div class="form-group">
            <ul id="id_a">
                <li class="multiple-choice">
                    <input type="radio" name="a" value="foo" id="id_a_0" />
                    <label id="id_a_0-label" for="id_a_0" class="form-label">
                        foo label
                    </label>
                    <span class="radio-button-helptext {span_class}">
                        Helptext for foo
                    </span>
                </li>
                <li class="multiple-choice">
                    <input type="radio" name="a" value="bar" id="id_a_1" />
                    <label id="id_a_1-label" for="id_a_1" class="form-label">
                        bar label
                    </label>
                    <span class="radio-button-helptext {span_class}">
                        Helptext for bar
                    </span>
                </li>
                <li class="multiple-choice">
                    <input type="radio" name="a" value="baz" id="id_a_2" />
                    <label id="id_a_2-label" for="id_a_2" class="form-label">
                        baz label
                    </label>
                </li>
            </ul>
        </div>
    </p>
    """.format(
        span_class=span_class
    )

    assert_html_equal(expected_html=expected, actual_html=Form().as_p())
