from helper.selenium import CssSelector
from helper import ItemsFile
from urllib.parse import urlparse
from urllib.parse import parse_qs


def get_project_tester(helper):
    return ProjectTester_v7_2_2(helper)


URL_VIEW_ALL_PROJECTS = 'ControlCenter/view_projects.php?view_all=1'


class ProjectTester_v7_2_2():
    def __init__(self, helper):
        self.helper = helper

    def export_file(self):
        return ItemsFile(self.helper.output_directory, 'projects')

    def export_items(self):
        self.helper.get(URL_VIEW_ALL_PROJECTS)

        output_file = self.export_file()

        for a in self.helper.get_elements(CssSelector('div.projtitle > a')):
            href = self.helper.get_href(a)

            output_file.add_item(dict(
                pid=parse_qs(urlparse(href).query).get('pid', [None])[0],
                name=self.helper.get_text(a).split(' PID ')[0],
                href=href,
            ))

        output_file.save()

    def visit_items(self):
        for i in self.export_file().get_items():
            self.helper.get(i['href'])

    def run(self):
        self.export_items()
        self.visit_items()
