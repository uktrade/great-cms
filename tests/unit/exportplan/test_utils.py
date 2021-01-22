from exportplan import utils


def test_format_two_dp():
    assert utils.format_two_dp(22.23) == '22.23'
    assert utils.format_two_dp(22.234) == '22.23'
    assert utils.format_two_dp(22) == '22.00'
    assert utils.format_two_dp(22.95688) == '22.96'
