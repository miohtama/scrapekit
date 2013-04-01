"""

    Scrape modelmayhem.com for Facebook fan pages and email addresses


"""

__author__ = "Mikko Ohtamaa"
__license__ = "BSD"

import os

import gspread
from selenium import webdriver


def get_gspread():
    """
    """
    gc = gspread.login(os.environ["GOOGLE_EMAIL"], os.environ["GOOGLE_PASSWORD"])

    key = os.environ.get("GOOGLE_SPREADSHEET")
    if not key:
        raise RuntimeError("Give target GOOGLE_SPREADHEET")

    try:
        wks = gc.open_by_key(os.environ["GOOGLE_SPREADSHEET"]).sheet1
    except gspread.exceptions.SpreadsheetNotFound:
        raise RuntimeError("No spreadsheet %s" % key)

    return wks


def get_browser():
    """ Create Selenium driver driving the scraper.

    """
    browser = webdriver.Firefox()  # Get local session of firefox
    return browser


def scrape_model_mayhem(browser, worksheet):
    """ Scrape model mayhem database for emails and Facebook addresses.

    We pass the CAPTCHA by using actual human input
    to do the initial search pass.
    """

    browser.get("http://www.modelmayhem.com/browse")

    passed_captcha = False

    while not passed_captcha:
        raw_input("Please fill in the CAPTCHA on the page and choose search parameters and press enter here. Do *not* hit submit\n?")
        browser.find_element_by_id("input[name='submit']").click()



def store_entry(worksheet, entry):
    """ Push scraped entry up to the Google spreadsheet.

    Use link as the source key.
    """
    cell = worksheet.find("Dough")


def main():
    """
    """
    browser = get_browser()
    worksheet = get_gspread()

    scrape_model_mayhem(browser, worksheet)

    browser.close()


if __name__ == "__main__":
    main()
