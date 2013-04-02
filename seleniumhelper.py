from selenium.webdriver.support.wait import WebDriverWait


def wait_and_find(browser, by, target, message=None, timeout=10, poll=0.5, allow_timeout=False):
    """
    Wait until some element is visible on the page (assume DOM is ready by then).

    Wraps selenium.webdriver.support.wait() API.

    http://selenium.googlecode.com/svn/trunk/docs/api/py/webdriver_support/selenium.webdriver.support.wait.html#module-selenium.webdriver.support.wait

    :param by: WebDriver By.XXX target

    :param target: CSS selector or such

    :param message: Error message to show if the element is not found

    :param allow_timeout: Let timeout exceptions through, otherwise invoke ipdb in SELENIUM_DEBUG_MODE
                          if element is not found
    """

    if not message:
        message = "Waiting for element: %s" % target

    waitress = WebDriverWait(browser, timeout, poll)
    matcher = lambda driver: driver.find_element(by, target)

    if allow_timeout:
        # Waitress throws an exception if element is not found within the timeout
        try:
            waitress.until(matcher, message)
        except Exception:
            return None
    else:
        waitress.until(matcher, message)

    elem = browser.find_element(by, target)
    return elem
