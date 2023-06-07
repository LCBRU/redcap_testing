import logging
from lbrc_selenium.selenium import CssSelector
from non_destructive_tests import ProjectFileGroup, RecordFileGroup


def get_project_record_extractor(helper):
    return ProjectRecordExtractor(helper)


class ProjectRecordExtractor():
    URL_ADD_EDIT_RECORDS = 'DataEntry/record_home.php?pid={}'
    
    def __init__(self, helper):
        self.helper = helper

    def export_project_records(self, project, record_file):
        logging.info(f'Extracting records from project {project["name"]}')
        self.helper.get(self.URL_ADD_EDIT_RECORDS.format(project['pid']))

        select = self.helper.wait_to_appear(CssSelector('select#record'))

        for o in self.helper.get_elements(CssSelector('option'), element=select):
            record = o.get_attribute("value")

            if record:
                logging.debug(f'Saving record {record} for project {project["name"]}')

                record_file.add_item(dict(
                    pid=project['pid'],
                    record=record,
                ))

    def run(self):
        p = ProjectFileGroup(self.helper)
        project_file = p.get_file()

        self.record_file_group = RecordFileGroup(self.helper)

        for project in project_file.get_items():
            record_file =  self.record_file_group.get_file({
                'pid': project['pid'],
                'project_name': project['name'],
            })

            if not record_file.exists():
                self.export_project_records(project, record_file)

                record_file.save()
