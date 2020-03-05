from io import BytesIO

import allure
from PIL import Image
from selenium.common.exceptions import NoSuchElementException


def convert_png_to_jpg(screenshot_png):
    raw_image = Image.open(BytesIO(screenshot_png))
    image = raw_image.convert('RGB')
    with BytesIO() as f:
        image.save(f, format='JPEG', quality=90)
        return f.getvalue()


def attach_jpg_screenshot(browser, page_name):
    screenshot_png = browser.get_screenshot_as_png()
    screenshot_jpg = convert_png_to_jpg(screenshot_png)
    allure.attach(
        screenshot_jpg,
        name=page_name,
        attachment_type=allure.attachment_type.JPG
    )


def is_element_present(browser, selector):
    """Check if sought element is present"""
    try:
        elements = browser.find_elements(by=selector.by, value=selector.selector)
        if elements:
            found = True
        else:
            found = False
    except NoSuchElementException:
        found = False
    return found
