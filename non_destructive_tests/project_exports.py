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

    def export_project_reports(self, project, report_file):
        logging.info(f'Extracting records from project {project["name"]}')
        self.helper.get(self.URL_LIST_REPORTS.format(project['pid']))

        for row in self.helper.get_elements(CssSelector('table#table-report_list tbody tr')):
            tds  = self.helper.get_elements(CssSelector('td'), element=row)

            report_code = self.helper.get_text(tds[1])

            if not report_code.isnumeric():
                continue

            report_title = self.helper.get_text(tds[2])
            logging.debug(f'Found report {report_title} for project {project["name"]}')

            report_file.add_item(dict(
                pid=project['pid'],
                report_code=report_code,
                report_title=report_title,
            ))
    

    def run(self):
        p = ProjectFileGroup(self.helper)
        project_file =  p.get_file()

        for project in project_file.get_items():
            report_file =  self.report_file_group.get_file({
                'pid': project['pid'],
                'project_name': project['name'],
            })

            if not report_file.exists():
                self.export_project_reports(project, report_file)
        
                report_file.save()
