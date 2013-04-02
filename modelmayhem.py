"""

    Scrape modelmayhem.com for Facebook fan pages and email addresses


"""

__author__ = "Mikko Ohtamaa"
__license__ = "BSD"

import os
import sys

import gspread
from selenium import webdriver
from selenium.webdriver.common.by import By

from seleniumhelper import wait_and_find


MAX_ENTRIES = 1000


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


def scrape_sub_page(browser, worksheet, url):
    """ Enter into a data page and grab relevant information.

    :yield: Dictionary of scraped data
    """

    data = dict(url=url)

    print "Scraping result page: %s" % url
    browser.get(url)
    browser.back()

    return data


def scrape_model_mayhem(browser, worksheet, number_of_pages=10):
    """ Scrape model mayhem database for emails and Facebook addresses.

    We pass the CAPTCHA by using actual human input
    to do the initial search pass.

    :param number_of_pages: How many search result subpages we dive into
    """

    browser.get("http://www.modelmayhem.com/browse")

    passed_captcha = False

    while not passed_captcha:
        raw_input("Please fill in the CAPTCHA on the page and choose search parameters and press enter here. Do *not* hit submit\n?")
        browser.find_element_by_css_selector("input[name='submit']").click()

        # Wait to see if we get a page which looks like search results
        submit_success_indicator = wait_and_find(browser, By.PARTIAL_LINK_TEXT, "Refine Search", allow_timeout=True)
        if submit_success_indicator:
            passed_captcha = True

    page = 1
    # Scrape each seacrh result page individually
    while page < number_of_pages:

        print "Scraping results page %d" % page

        records = browser.find_elements_by_css_selector(".bMemberData")

        # Click each search result individually
        for rec in records:
            link = rec.find_element_by_css_selector("a.bold")
            href = link.get_attribute("href")
            yield scrape_sub_page(browser, worksheet, href)

        page += 1


def find_append_row(worksheet):
    """ Find the first row in the worksheet which is empty.
    """
    for row_index in xrange(1, MAX_ENTRIES):
        values = worksheet.row_values(row_index)
        if values == []:
            return row_index

    return -1


def store_entry(worksheet, entry, append_row):
    """ Push scraped entry up to the Google spreadsheet.

    Use link as the source key.
    """

    # Unique id used to recog. already stored entries
    entry_id = entry["url"]
    cell = worksheet.find(entry_id)

    if cell:
        row = cell.row
    else:
        # Find first empty row
        row = append_row

    return row


def main():
    """ ModelMayhem.com scraper entry point
    """
    worksheet = get_gspread()

    # Find first empty row where we can insert data
    append_row = find_append_row(worksheet)
    if append_row < 0:
        sys.exit("The spreadsheet is full / no empty rows available")

    # Open a WebDriven browser instance for scraping
    browser = get_browser()

    for entry in scrape_model_mayhem(browser, worksheet):
        stored_row = store_entry(worksheet, entry, append_row)

        # We just filled the last row?
        if stored_row == append_row:
            append_row += 1

    browser.close()


if __name__ == "__main__":
    main()
