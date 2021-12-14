import logging
from helper import ItemFileGroup
from helper.selenium import CssSelector
from non_destructive_tests import ProjectFileGroup


def get_project_dags_tester(helper):
    return ProjectDagTester(helper)


class DagFileGroup(ItemFileGroup):
    def __init__(self, helper):
        super().__init__(helper, helper.output_directory / 'dags', 'dags_{pid}_{project_name}')


class ProjectDagTester():
    def __init__(self, helper):
        self.helper = helper

    def run(self):
        steps = [
            ProjectDags(self.helper),
        ]

        for s in steps:
            s.run()


class ProjectDags():
    URL_PROJECT_DAGS = 'DataAccessGroups/index.php?pid=14'
    
    def __init__(self, helper):
        self.helper = helper
        self.dag_file_group = DagFileGroup(self.helper)

    def export_dags(self, project, dag_file):
        logging.info(f'Export dags for project {project["name"]}')
        self.helper.get(self.URL_PROJECT_DAGS.format(project['pid']))

        for r in self.helper.get_elements(CssSelector('table#table-dags_table tbody tr')):
            cells = self.helper.get_elements(CssSelector('td'), element=r)

            for u in self.helper.get_elements(CssSelector('div.wrap div'), element=cells[1]):

                dag_file.add_item(dict(
                    dag=self.helper.get_text(cells[0]),
                    username=self.helper.get_text(u),
                ))

    def run(self):
        p = ProjectFileGroup(self.helper)
        project_file =  p.get_file()

        for project in project_file.get_items():
            dag_file =  self.dag_file_group.get_file({
                'pid': project['pid'],
                'project_name': project['name'],
            })

            if not dag_file.exists():
                self.export_dags(project, dag_file)

                dag_file.save()
