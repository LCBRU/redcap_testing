import logging
from helper.selenium import CssSelector
from helper import ItemsFile
from urllib.parse import urlparse
from urllib.parse import parse_qs
from time import sleep
from itertools import islice


URL_VIEW_ALL_PROJECTS = 'ControlCenter/view_projects.php?view_all=1'
URL_REPORT_PROJECT_RECORDS = 'DataExport/index.php?pid={}&report_id=ALL'

def get_project_tester(helper):
    return ProjectTester(helper)


class ProjectTester():
    def __init__(self, helper):
        self.helper = helper

    def run(self):
        project_file = ItemsFile(self.helper.output_directory, 'projects')
        record_file = ItemsFile(self.helper.output_directory, 'records')

        steps = [
            ProjectExporter(helper=self.helper, project_file=project_file),
            ProjectRecordExtractor(helper=self.helper, project_file=project_file, record_file=record_file)
        ]

        for s in steps:
            s.run()


class ProjectExporter():
    def __init__(self, helper, project_file):
        self.helper = helper
        self.project_file = project_file

    def export_items(self):
        logging.info('Extracting projects')

        self.helper.get(URL_VIEW_ALL_PROJECTS)

        sleep(2)

        output_file = self.project_file

        for tr in self.helper.get_elements(CssSelector('tr.myprojstripe')):
            a = self.helper.get_element(CssSelector('div.projtitle > a'), element=tr)
            records = self.helper.get_text(
                self.helper.get_element(CssSelector("span[class^='pid-cntr-']"), element=tr)
            )

            href = self.helper.get_href(a)
            name=self.helper.get_text(a).split(' PID ')[0]

            logging.info(f'Saving project {name}')

            output_file.add_item(dict(
                pid=parse_qs(urlparse(href).query).get('pid', [None])[0],
                name=name,
                href=href,
                records=records,
            ))

        output_file.save()

    def visit_items(self):
        for i in self.project_file().get_items():
            self.helper.get(i['href'])

    def run(self):
        self.export_items()


class ProjectRecordExtractor():
    def __init__(self, helper, project_file, record_file):
        self.helper = helper
        self.project_file = project_file
        self.record_file = record_file

    def visit_items(self):
        for i in self.project_file.get_items():
            if int(i['records']) > 0:
                logging.info(f'Extracting records from project {i["name"]}')
                self.helper.get(URL_REPORT_PROJECT_RECORDS.format(i['pid']))

                table = self.helper.wait_to_appear(CssSelector('table#report_table'), seconds_to_wait=500)

                for a in self.helper.get_elements(CssSelector('a.rl'), element=table):
                    record = self.helper.get_text(a)

                    logging.info(f'Saving record {record} for project {i["name"]}')

                    self.record_file.add_item(dict(
                        pid=i['pid'],
                        href=self.helper.get_href(a),
                        record=record,
                    ))
        
        self.record_file.save()

    def run(self):
        self.visit_items()
