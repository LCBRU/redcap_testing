import logging
from lbrc_selenium import ItemFileGroup
from lbrc_selenium.selenium import CssSelector
from non_destructive_tests import ProjectFileGroup


def get_project_data_comparison_tester(helper):
    return ProjectDataComparisonTester(helper)


class ComparisonFileGroup(ItemFileGroup):
    def __init__(self, helper):
        super().__init__(helper, helper.output_directory / 'data_comparison', 'data_comparison_{pid}_{project_name}')


class ProjectDataComparisonTester():
    def __init__(self, helper):
        self.helper = helper

    def run(self):
        steps = [
            ProjectDataComparison(self.helper),
        ]

        for s in steps:
            s.run()


class ProjectDataComparison():
    URL_COMPARISON_TOOL = 'index.php?pid={}&route=DataComparisonController:index'
    
    def __init__(self, helper):
        self.helper = helper
        self.data_comparison_file_group = ComparisonFileGroup(self.helper)

    def export_sample_data_comparison(self, project, comparison_file):
        logging.info(f'Comparing data for project {project["name"]}')
        self.helper.get(self.URL_COMPARISON_TOOL.format(project['pid']))

        record1 = self.helper.click_element(CssSelector('select#record1'))
        self.helper.click_element(CssSelector('option:nth-of-type(2)'), element=record1)

        record2 = self.helper.click_element(CssSelector('select#record2'))
        self.helper.click_element(CssSelector('option:nth-of-type(3)'), element=record2)

        self.helper.click_element(CssSelector('input[type="submit"]'))

        table = self.helper.wait_to_appear(CssSelector('form[name="create_new"] table.form_border'))

        for i, r in enumerate(self.helper.get_elements(CssSelector('tbody tr'), element=table)):
            if i < 3:
                continue

            cells = self.helper.get_elements(CssSelector('td'), element=r)

            comparison_file.add_item(dict(
                label=self.helper.get_text(cells[0]),
                form=self.helper.get_text(cells[1]),
                record_1=self.helper.get_text(cells[2]),
                record_2=self.helper.get_text(cells[3]),
            ))

    def run(self):
        p = ProjectFileGroup(self.helper)
        project_file = p.get_file()

        for project in project_file.get_items(filter=lambda i: int(i['records']) > 1):
            comparison_file =  self.data_comparison_file_group.get_file({
                'pid': project['pid'],
                'project_name': project['name'],
            })

            if not comparison_file.exists():
                self.export_sample_data_comparison(project, comparison_file)
        
                comparison_file.save()
