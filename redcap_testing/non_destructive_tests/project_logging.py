import logging
from lbrc_selenium import ItemFileGroup
from lbrc_selenium.selenium import CssSelector
from non_destructive_tests import ProjectFileGroup



CV_ACTION_TRANSLATION = {
    '0.0.0': {},
    '7.2.2': {
        'Updated Record': 'Update record',
    },
}

def get_project_logging_tester(helper):
    return ProjectLoggingTester(helper)


class LoggingFileGroup(ItemFileGroup):
    def __init__(self, helper):
        super().__init__(helper, helper.output_directory / 'logging', 'logging_{pid}_{project_name}')


class ProjectLoggingTester():
    def __init__(self, helper):
        self.helper = helper

    def run(self):
        steps = [
            ProjectLogging(self.helper),
        ]

        for s in steps:
            s.run()


class ProjectLogging():
    URL_LOGGING = 'Logging/index.php?pid={}&beginTime=&endTime='

    def __init__(self, helper):
        self.helper = helper
        self.logging_file_group = LoggingFileGroup(self.helper)

    def export_logging(self, project, logging_file):
        logging.info(f'Export logging for project {project["name"]}')
        self.helper.get(self.URL_LOGGING.format(project['pid']))

        action_translations = self.helper.get_compare_version_item(CV_ACTION_TRANSLATION)

        for r in self.helper.get_elements(CssSelector('table.form_border tbody tr:nth-of-type(2) ~ tr')):
            cells = self.helper.get_elements(CssSelector('td'), element=r)

            a = self.helper.get_text(cells[2])

            for ts, td in action_translations.items():
                a = a.replace(ts, td)

            logging_file.add_item(dict(
                time=self.helper.get_text(cells[0]),
                username=self.helper.get_text(cells[1]),
                action=a,
                changes=self.helper.get_text(cells[3]),
            ))

    def run(self):
        p = ProjectFileGroup(self.helper)
        project_file =  p.get_file()

        for project in project_file.get_items():
            logging_file =  self.logging_file_group.get_file({
                'pid': project['pid'],
                'project_name': project['name'],
            })

            if not logging_file.exists():
                self.export_logging(project, logging_file)
        
                logging_file.save()
