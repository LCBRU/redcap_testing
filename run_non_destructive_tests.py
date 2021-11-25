import os
import logging
from time import sleep
from helper.selenium import CssSelector, get_selenium
from non_destructive_tests.project_tester import get_project_tester
from dotenv import load_dotenv
from datetime import datetime


load_dotenv()

def login(helper):
    helper.get('')
    helper.type_in_textbox(CssSelector('input#username'), os.environ["USERNAME"])
    helper.type_in_textbox(CssSelector('input#password'), os.environ["PASSWORD"])
    helper.click_element(CssSelector('button#login_btn'))
    sleep(2)

LOGGING_FORMAT = '%(asctime)s %(levelname)s %(message)s'
logging.basicConfig(level=logging.INFO, format=LOGGING_FORMAT)
logging.basicConfig(filename='errors.log', level=logging.ERROR, format=LOGGING_FORMAT)

started = datetime.now()

h = get_selenium()

testers = [
    get_project_tester(h),
]

try:
    login(h)

    for t in testers:
        t.run()
        sleep(1)
finally:
    h.close()

print(datetime.now() - started)