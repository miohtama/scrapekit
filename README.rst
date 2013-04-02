We use `GSpread <https://github.com/burnash/gspread>`_ library to write results
directly to Google Docs spreadsheet in real-time.

Installation
--------------

    curl -L -o virtualenv.py https://raw.github.com/pypa/virtualenv/master/virtualenv.py
    python virtualenv.py venv
    . venv/bin/activate
    pip install selenium gspread ipdb

Running
-----------------

    . venv/bin/activate
    GOOGLE_EMAIL="xxx" GOOGLE_PASSWORD="yyyy" GOOGLE_SPREADSHEET="zzz" python modelmayhem.py


Alternative solutions
------------------------

* http://nrabinowitz.github.com/pjscrape/

* `Selenium WebDriver API <http://code.google.com/p/selenium/source/browse/py/selenium/webdriver/remote/webdriver.py>`_

* `Selenium WebElement API <http://code.google.com/p/selenium/source/browse/py/selenium/webdriver/remote/webelement.py>`_