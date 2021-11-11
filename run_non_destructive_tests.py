import logging
from time import sleep
from redcap_tester import get_redcap_helper
from non_destructive_tests.project_tester import get_project_tester
from dotenv import load_dotenv
from datetime import datetime


load_dotenv()

logging.basicConfig(level=logging.INFO)
logging.basicConfig(filename='errors.log', level=logging.ERROR)


started = datetime.now()

h = get_redcap_helper()

h.login()

testers = [
    get_project_tester(h),
]

for t in testers:
    t.run()
    sleep(1)

h.close()

print(datetime.now() - started)