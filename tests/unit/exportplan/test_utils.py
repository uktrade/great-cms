from unittest.mock import Mock, patch

from exportplan import utils


def test_format_two_dp():
    assert utils.format_two_dp(22.23) == '22.23'
    assert utils.format_two_dp(22.234) == '22.23'
    assert utils.format_two_dp(22) == '22.00'
    assert utils.format_two_dp(22.95688) == '22.96'


def test_render_to_pdf_error(user, get_request):
    pdf_context = {'export_plan': get_request.user.export_plan.data, 'user': get_request.user}

    with patch('exportplan.utils.pisa.pisaDocument') as pisadocument:
        pisadocument.return_value = Mock(status_code=500, **{'json.return_value': {}})
        pdf = utils.render_to_pdf('exportplan/pdf_download.html', pdf_context)
        assert pdf is None
