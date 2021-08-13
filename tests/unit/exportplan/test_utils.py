from unittest import mock
from unittest.mock import Mock, patch

from django.core.files.base import ContentFile
from django.http import HttpResponse

from exportplan import utils
from exportplan.core.parsers import ExportPlanParser


def test_format_two_dp():
    assert utils.format_two_dp(22.23) == '22.23'
    assert utils.format_two_dp(22.234) == '22.23'
    assert utils.format_two_dp(22) == '22.00'
    assert utils.format_two_dp(22.95688) == '22.96'


def test_render_to_pdf_error(user, get_request, export_plan_data):
    pdf_context = {
        'export_plan': ExportPlanParser(export_plan_data),
        'user': get_request.user,
    }

    with patch('exportplan.utils.pisa.pisaDocument') as pisadocument:
        pisadocument.return_value = Mock(status_code=500, **{'json.return_value': {}})
        pdf, pdf_file = utils.render_to_pdf('exportplan/pdf_download.html', pdf_context)
        assert pdf is None


@mock.patch.object(utils.pisa, 'pisaDocument')
def test_render_to_pdf(mock_pisa, user, get_request, export_plan_data):
    pdf_context = {
        'export_plan': ExportPlanParser(export_plan_data),
        'user': get_request.user,
    }

    # Must be a better way of mocking a return object
    class Errordoc:
        err = False

    mock_pisa.return_value = Errordoc()
    pdf, pdf_file = utils.render_to_pdf('exportplan/pdf_download.html', pdf_context)
    assert isinstance(pdf, HttpResponse)
    assert isinstance(pdf_file, ContentFile)
