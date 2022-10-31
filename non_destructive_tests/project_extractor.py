import logging
from helper.selenium import CssSelector, XpathSelector
from urllib.parse import urlparse
from urllib.parse import parse_qs
from non_destructive_tests import ProjectFileGroup


def get_project_extractor(helper):
    return ProjectExporter(helper)


class ProjectExporter():
    URL_VIEW_ALL_PROJECTS = 'ControlCenter/view_projects.php?view_all=1&show_archived'

    def __init__(self, helper):
        self.helper = helper

    def export_projects(self, project_file):
        logging.info('Extracting projects')

        self.helper.get(self.URL_VIEW_ALL_PROJECTS)

        self.helper.wait_to_disappear(XpathSelector('//span[text()="Loading..."]'))

        for tr in self.helper.get_elements(CssSelector('tr.myprojstripe')):
            a = self.helper.get_element(CssSelector('div.projtitle > a'), element=tr)
            records = self.helper.get_text(
                self.helper.get_element(CssSelector("span[class^='pid-cntr-']"), element=tr)
            ).replace('.', '').replace(',', '').strip()

            href = self.helper.get_href(a)
            name = self.helper.get_text(a).split(' PID ')[0].split(' OFFLINE')[0]

            logging.info(f'Saving project {name}')

            project_file.add_item(dict(
                pid=parse_qs(urlparse(href).query).get('pid', [None])[0],
                name=name,
                href=self.helper.convert_to_relative_url(href),
                records=records,
            ))

        project_file.save()

    def run(self):
        pfg = ProjectFileGroup(self.helper)
        project_file = pfg.get_file()

        if not project_file.exists():
            self.export_projects(project_file)
