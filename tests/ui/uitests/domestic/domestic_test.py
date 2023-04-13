from pages.domestic.home_page import HomePage


def test_home_h1_text(driver):
    home_page = HomePage(driver)
    home_page.navigate_to_home()
    home_page.click_accept_cookies()
    assert 'MADE in the UK\nSOLD \nto\n the\n world' in home_page.get_h1_text()
