import os
import jsonlines
import csv
from time import sleep
from selenium_test_helper import SeleniumTestHelper
from selenium.webdriver.common.by import By
from werkzeug.utils import secure_filename


def get_redcap_helper():
    return RedcapSeleniumTestHelper(
    download_directory=os.environ["DOWNLOAD_DIRECTORY"],
    output_directory=os.environ["OUTPUT_DIRECTORY"],
    base_url=os.environ["BASE_URL"],
    headless=False,
    implicit_wait_time=float(os.environ["IMPLICIT_WAIT_TIME"]),
    click_wait_time=float(os.environ["CLICK_WAIT_TIME"]),
    download_wait_time=float(os.environ["DOWNLOAD_WAIT_TIME"]),
    page_wait_time=float(os.environ["PAGE_WAIT_TIME"]),
    username=os.environ["USERNAME"],
    password=os.environ["PASSWORD"],
    version=os.environ["VERSION"],
    sampling_type=os.environ["SAMPLING_TYPE"],
    compare_version=os.environ["COMPARE_VERSION"],
)


class RedcapSeleniumTestHelper(SeleniumTestHelper):
    def login(self):
        self.get('')
        self.type_in_textbox('//input[@ng-model="loginData.loginName"]', By.XPATH, self._username)
        self.type_in_textbox('//input[@ng-model="loginData.password"]', By.XPATH, self._password)
        self.click_element('span[translate="user.sign_in"]', By.CSS_SELECTOR)


class ItemsFile():
    def __init__(self, output_directory, object_name):
        self.output_directory = output_directory
        self.object_name = object_name
        self.items = []

    def _export_filename(self):
        return secure_filename(f'{self.object_name}_items.jsonl')

    def add_item(self, name, href):
        item = {
            'name': name,
            'href': href,
        }

        if item not in self.items:
            self.items.append(item)

    def save(self):
        with jsonlines.open(self.output_directory / self._export_filename(), mode='w') as writer:
            for i in sorted(self.items, key=lambda i: i['name']):
                writer.write(i)
