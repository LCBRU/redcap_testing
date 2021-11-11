from time import sleep
from selenium_test_helper import CssSelector, XpathSelector


def get_project_tester(helper):
    return ProjectTester_v7_2_2(helper)


class ProjectTester_v7_2_2():
    def __init__(self, helper):
        self.helper = helper

    def export_items(self):
        pass

    def run(self):
        self.export_items()
