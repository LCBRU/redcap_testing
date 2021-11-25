import logging
from helper.selenium import CssSelector, XpathSelector
from helper import ItemsFile
from urllib.parse import urlparse
from urllib.parse import parse_qs


def get_project_tester(helper):
    return ProjectTester(helper)


def _get_project_file(helper):
    return ItemsFile(helper.output_directory, 'projects')


def _get_record_file(helper, project):
    return ItemsFile(helper.output_directory, f'records_{project["pid"]}_{project["name"]}')


def _get_instrument_file(helper, project):
    return ItemsFile(helper.output_directory,f'instruments_{project["pid"]}_{project["name"]}')


def _get_instrument_details_file(helper, project):
    return ItemsFile(helper.output_directory,f'instrument_details_{project["pid"]}_{project["name"]}')


class ProjectTester():
    def __init__(self, helper):
        self.helper = helper

    def run(self):
        steps = [
            ProjectExporter(helper=self.helper),
            ProjectRecordExtractor(helper=self.helper),
            ProjectRecordInstrumentExtractor(helper=self.helper),
        ]

        for s in steps:
            s.run()


class ProjectExporter():
    URL_VIEW_ALL_PROJECTS = 'ControlCenter/view_projects.php?view_all=1'

    def __init__(self, helper):
        self.helper = helper
        self.project_file =  _get_project_file(self.helper)

    def export_projects(self):
        logging.info('Extracting projects')

        self.helper.get(self.URL_VIEW_ALL_PROJECTS)

        self.helper.wait_to_disappear(XpathSelector('//span[text()="Loading..."]'))

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

    def run(self):
        self.export_projects()


class ProjectRecordExtractor():
    URL_ADD_EDIT_RECORDS = 'DataEntry/record_home.php?pid={}'
    
    def __init__(self, helper):
        self.helper = helper

    def export_project_records(self, project):
        record_file = _get_record_file(self.helper, project)

        logging.info(f'Extracting records from project {project["name"]}')
        self.helper.get(self.URL_ADD_EDIT_RECORDS.format(project['pid']))

        select = self.helper.wait_to_appear(CssSelector('select#record'))

        for o in self.helper.get_elements(CssSelector('option'), element=select):
            record = o.get_attribute("value")

            if record:
                logging.info(f'Saving record {record} for project {project["name"]}')

                record_file.add_item(dict(
                    pid=project['pid'],
                    record=record,
                ))
    
        record_file.save()

    def run(self):
        project_file =  _get_project_file(self.helper)

        for project in project_file.get_sample_items(filter=lambda i: int(i['records']) > 0):
            self.export_project_records(project)


class ProjectRecordInstrumentExtractor():
    URL_RECORD_HOME = 'DataEntry/record_home.php?pid={pid}&id={record}'

    def __init__(self, helper):
        self.helper = helper

    def export_record_instruments(self, record, instrument_file):
        logging.info(f'Extracting instruments for record {record["record"]} from project {record["pid"]}')
        self.helper.get(self.URL_RECORD_HOME.format(pid=record['pid'], record=record['record']))

        table = self.helper.wait_to_appear(CssSelector('table#event_grid_table'))

        visits = [self.helper.get_text(h) for h in self.helper.get_elements(CssSelector('thead th'), element=table)]

        for row in self.helper.get_elements(CssSelector('tbody tr'), element=table):
            instrument_name = self.helper.get_text(self.helper.get_element(CssSelector('td:first-of-type'), element=row))

            for i, td in enumerate(self.helper.get_elements(CssSelector('td:not(:first-of-type)'), element=row), start=1):
                links = self.helper.get_elements(CssSelector('a'), element=td)

                if len(links) > 0:

                    href = self.helper.get_href(links[0])

                    logging.info(f'Saving instrument {instrument_name} for project {record["pid"]} and record {record["record"]}')

                    instrument_file.add_item(dict(
                        pid=record["pid"],
                        record=record['record'],
                        instrument_name=instrument_name,
                        visit_name=visits[i],
                        href=href,
                    ))

    def run(self):
        project_file =  _get_project_file(self.helper)

        for project in project_file.get_sample_items(filter=lambda i: int(i['records']) > 0):
            record_file = _get_record_file(self.helper, project)
            instrument_file = _get_instrument_file(self.helper, project)

            for record in record_file.get_sample_items():
                self.export_record_instruments(record, instrument_file)

            instrument_file.save()


class ProjectRecordInstrumentDetails():
    def __init__(self, helper):
        self.helper = helper

    def export_instrument_details(self, record, instrument_file):
        logging.info(f'Extracting instruments for record {record["record"]} from project {record["pid"]}')
        self.helper.get(self.URL_RECORD_HOME.format(pid=record['pid'], record=record['record']))

        table = self.helper.wait_to_appear(CssSelector('table#event_grid_table'))

        visits = [self.helper.get_text(h) for h in self.helper.get_elements(CssSelector('thead th'), element=table)]

        for row in self.helper.get_elements(CssSelector('tbody tr'), element=table):
            instrument_name = self.helper.get_text(self.helper.get_element(CssSelector('td:first-of-type'), element=row))

            for i, td in enumerate(self.helper.get_elements(CssSelector('td:not(:first-of-type)'), element=row), start=1):
                links = self.helper.get_elements(CssSelector('a'), element=td)

                if len(links) > 0:

                    href = self.helper.get_href(links[0])

                    logging.info(f'Saving instrument {instrument_name} for project {record["pid"]} and record {record["record"]}')

                    instrument_file.add_item(dict(
                        pid=record["pid"],
                        record=record['record'],
                        instrument_name=instrument_name,
                        visit_name=visits[i],
                        href=href,
                    ))

    def run(self):
        project_file =  _get_project_file(self.helper)

        for project in project_file.get_sample_items(filter=lambda i: int(i['records']) > 0):
            instrument_file = _get_instrument_file(self.helper, project)
            instrument_details_file = _get_instrument_details_file(self.helper, project)

            for instrument in instrument_file.get_sample_items():
                self.export_instrument_details(instrument, instrument_file)

            instrument_file.save()
