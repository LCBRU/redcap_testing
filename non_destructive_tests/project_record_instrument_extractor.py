import logging
from helper.selenium import CssSelector
from non_destructive_tests import ProjectFileGroup, RecordFileGroup, InstrumentFileGroup
from urllib.parse import urlparse


def valid_url(url):
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except:
        return False


def get_project_record_instrument_extractor(helper):
    return ProjectRecordInstrumentExtractor(helper)


class ProjectRecordInstrumentExtractor():
    URL_RECORD_HOME = 'DataEntry/record_home.php?pid={pid}&id={record}'

    def __init__(self, helper):
        self.helper = helper

    def export_record_instruments(self, record, instrument_file):
        logging.info(f'Extracting instruments for record {record["record"]} from project {record["pid"]}')
        self.helper.get(self.URL_RECORD_HOME.format(pid=record['pid'], record=record['record']))

        visits = [self.helper.get_text(h) for h in self.helper.get_elements(CssSelector('table#event_grid_table thead th'))]

        for row in self.helper.get_elements(CssSelector('table#event_grid_table tbody tr')):
            tds  = self.helper.get_elements(CssSelector('td'), element=row)

            instrument_name = self.helper.get_text(tds[0])

            if instrument_name == 'Delete all data on event:':
                continue

            for i, td in enumerate(tds[1:], start=1):
                links = self.helper.get_elements(CssSelector('a'), element=td)

                if len(links) > 0:

                    href = self.helper.get_href(links[0])

                    if valid_url(href):
                        logging.info(f'Saving instrument {instrument_name} for project {record["pid"]} and record {record["record"]}')

                        instrument_file.add_item(dict(
                            pid=record["pid"],
                            record=record['record'],
                            instrument_name=instrument_name,
                            visit_name=visits[i],
                            href=self.helper.convert_to_relative_url(href),
                        ))

    def run(self):
        project_file = ProjectFileGroup(self.helper).get_file()
        rfg = RecordFileGroup(self.helper)
        ifg = InstrumentFileGroup(self.helper)

        for project in project_file.get_sample_items(filter=lambda i: int(i['records']) > 0):
            record_file =  rfg.get_file({
                'pid': project['pid'],
                'project_name': project['name'],
            })

            for record in record_file.get_sample_items():
                instrument_file =  ifg.get_file({
                    'pid': record['pid'],
                    'record': record['record'],
                })

                if not instrument_file.exists():
                    self.export_record_instruments(record, instrument_file)

                    instrument_file.save()
