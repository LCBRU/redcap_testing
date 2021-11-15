import logging
from time import sleep
from selenium_helper import get_selenium
from non_destructive_tests.project_tester import get_project_tester
from dotenv import load_dotenv
from datetime import datetime


load_dotenv()

def login(helper):
    pass

logging.basicConfig(level=logging.INFO)
logging.basicConfig(filename='errors.log', level=logging.ERROR)

started = datetime.now()

h = get_selenium()

testers = [
    get_project_tester(h),
]

login(h)

for t in testers:
    t.run()
    sleep(1)

h.close()

print(datetime.now() - started)