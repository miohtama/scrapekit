"""

    Scrape modelmayhem.com for Facebook fan pages and email addresses


"""

__author__ = "Mikko Ohtamaa"
__license__ = "BSD"

import os
import sys
import datetime
from urllib2 import HTTPError

import gspread
from selenium import webdriver
from selenium.webdriver.common.by import By

from seleniumhelper import wait_and_find


#: Arbirary hard limit how much data we want to store in spreadsheer ourselves
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

    This is the place where magic happens.
    We read the data off the page based on HTML layout / CSS
    classes the elements have.

    :return: Dictionary of scraped data
    """

    data = dict()

    data["url"] = url
    data["updated"] = datetime.datetime.now()

    print "Scraping result page: %s" % url
    browser.get(url)

    data["name"] = browser.find_element_by_css_selector("table.maintable table h1").text
    data["homepage"] = browser.find_element_by_css_selector("table.maintable table a").get_attribute("href")

    browser.back()

    return data


def scrape_model_mayhem(browser, worksheet, number_of_pages=5):
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
        submit_success_indicator = wait_and_find(browser, By.PARTIAL_LINK_TEXT, "Refine Search", allow_timeout=True, timeout=3.0)
        if submit_success_indicator:
            passed_captcha = True

    page = 0
    links = []

    # First we scrape search results, all pages of them,
    # for links to individual data pages
    while page < number_of_pages:

        print "Scraping results page %d" % page

        records = browser.find_elements_by_css_selector(".bMemberData")

        # We scrape all links to array first,
        # because visiting subpages in scrape_sub_page() break our WebDriver
        # cached DOM tree and we cannot iterate it directly
        links = []
        for rec in records:
            link = rec.find_element_by_css_selector("a.bold")
            href = link.get_attribute("href")
            links.append(href)

        page += 1
        browser.find_element_by_partial_link_text("Next").click()

    for href in links:
        yield scrape_sub_page(browser, worksheet, href)


def find_append_row(worksheet):
    """ Find the first row in the worksheet which is empty.
    """
    for row_index in xrange(1, MAX_ENTRIES):
        values = worksheet.row_values(row_index)
        if values == []:
            return row_index

    return -1


def get_column_labels(worksheet):
    """ Get label -> column id mappings.

    This way we know in which columns to store entry data even
    if the user is to shuffle the columns.

    Assume labels are on the first row. Also make
    sure all labels are lowercase in internal use.

    :return: label name -> column index dict
    """

    columns = {}

    labels = worksheet.row_values(1)
    for i in range(len(labels)):
        label = labels[i].lower()
        columns[label] = i

    return columns


def store_entry(worksheet, columns, entry, append_row):
    """ Push scraped entry up to the Google spreadsheet.

    Use the orignal page link as the primary key, so
    we can update old entries without readding them.
    """

    # Unique id used to recog. already stored entries
    entry_id = entry["url"]

    try:
        cell = worksheet.find(entry_id)
    except gspread.exceptions.CellNotFound:
        cell = None

    if cell:
        # Update existing row
        row = cell.row
    else:
        # Fill in first empty row
        row = append_row

    # T is the last column in default empty spreadsheet
    cell_range = 'A%d:T%d' % (row, row)

    try:
        cell_list = worksheet.range(cell_range)
    except HTTPError as e:
        # Otherwise the actual exception message is never shown
        raise RuntimeError("Exception from Spreadsheet API: %s" % e.read())

    for key, value in entry.items():
        try:
            index = columns[key]
        except KeyError:
            raise RuntimeError("Did not find column to store %s. Has columns: %s" % (key, columns))

        # Update values in the cell range
        if value is not None:
            cell_list[index].value = value

    worksheet.update_cells(cell_list)

    return row


def main():
    """ ModelMayhem.com scraper entry point
    """
    worksheet = get_gspread()

    # Find first empty row where we can insert data
    append_row = find_append_row(worksheet)
    if append_row < 0:
        sys.exit("The spreadsheet is full / no empty rows available")

    columns = get_column_labels(worksheet)
    if not columns:
        sys.exit("Could not read column labels on the spreadsheet: %s" % os.environ["GOOGLE_SPREADSHEET"])

    # Open a WebDriven browser instance for scraping
    browser = get_browser()

    for entry in scrape_model_mayhem(browser, worksheet):
        stored_row = store_entry(worksheet, columns, entry, append_row)

        # We just filled the last row?
        if stored_row == append_row:
            append_row += 1

    browser.close()


if __name__ == "__main__":
    main()
