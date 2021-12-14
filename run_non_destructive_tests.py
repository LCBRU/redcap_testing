import os
import logging
from time import sleep
from helper.selenium import CssSelector, get_selenium
from non_destructive_tests.project_extractor import get_project_extractor
from non_destructive_tests.project_record_extractor import get_project_record_extractor
from non_destructive_tests.project_record_instrument_extractor import get_project_record_instrument_extractor
from non_destructive_tests.project_record_instrument_details_extractor import get_project_record_instrument_details_extractor
from non_destructive_tests.project_dags import get_project_dags_tester
from non_destructive_tests.project_data_comparison import get_project_data_comparison_tester
from non_destructive_tests.project_exports import get_project_report_export_tester
from non_destructive_tests.project_field_comments import get_project_field_comments_tester
from non_destructive_tests.project_logging import get_project_logging_tester
from non_destructive_tests.project_users import get_project_user_tester
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
    get_project_extractor(h),
    get_project_record_extractor(h),
    get_project_record_instrument_extractor(h),
    get_project_record_instrument_details_extractor(h),
    get_project_dags_tester(h),
    get_project_data_comparison_tester(h),
    get_project_report_export_tester(h),
    get_project_field_comments_tester(h),
    get_project_logging_tester(h),
    get_project_user_tester(h),
]

try:
    login(h)

    for t in testers:
        t.run()
        sleep(1)
finally:
    h.close()

print(datetime.now() - started)