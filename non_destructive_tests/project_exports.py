import logging
from helper import ItemFileGroup
from helper.selenium import CssSelector
from non_destructive_tests import ProjectFileGroup


def get_project_report_export_tester(helper):
    return ProjectReportExportTester(helper)


class ReportsFileGroup(ItemFileGroup):
    def __init__(self, helper):
        super().__init__(helper, helper.output_directory / 'reports', 'reports_{pid}_{project_name}')


class ProjectReportExportTester():
    def __init__(self, helper):
        self.helper = helper

    def run(self):
        steps = [
            ProjectAllDataReport(self.helper),
        ]

        for s in steps:
            s.run()


class ProjectAllDataReport():
    URL_LIST_REPORTS = 'DataExport/index.php?pid={}'
    
    def __init__(self, helper):
        self.helper = helper
        self.report_file_group = ReportsFileGroup(self.helper)

    def export_project_reports(self, project):
        report_file =  self.report_file_group.get_file({
            'pid': project['pid'],
            'project_name': project['name'],
        })

        logging.info(f'Extracting records from project {project["name"]}')
        self.helper.get(self.URL_LIST_REPORTS.format(project['pid']))

        for r in self.helper.get_elements(CssSelector('table#table-report_list tbody tr td:nth-of-type(3)')):
            report_title = self.helper.get_text(r)
            logging.info(f'Found report {report_title} for project {project["name"]}')

            report_file.add_item(dict(
                pid=project['pid'],
                report_title=report_title,
            ))
    
        report_file.save()

    def run(self):
        p = ProjectFileGroup(self.helper)
        project_file =  p.get_file()

        self.report_file_group.clean()

        for project in project_file.get_items():
            self.export_project_reports(project)
