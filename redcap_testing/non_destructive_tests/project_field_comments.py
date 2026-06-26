import logging
from lbrc_selenium import ItemFileGroup
from lbrc_selenium.selenium import CssSelector
from non_destructive_tests import ProjectFileGroup


def get_project_field_comments_tester(helper):
    return ProjectFieldCommentsTester(helper)


class FieldCommentsFileGroup(ItemFileGroup):
    def __init__(self, helper):
        super().__init__(helper, helper.output_directory / 'comments', 'comments_{pid}_{project_name}')


class ProjectFieldCommentsTester():
    def __init__(self, helper):
        self.helper = helper

    def run(self):
        steps = [
            ProjectFieldComments(self.helper),
        ]

        for s in steps:
            s.run()


class ProjectFieldComments():
    URL_FIELD_COMMENTS = 'DataQuality/field_comment_log.php?pid={}'
    
    def __init__(self, helper):
        self.helper = helper
        self.field_comments_file_group = FieldCommentsFileGroup(self.helper)

    def export_field_comments(self, project, field_comments_file):
        logging.info(f'Export field comments for project {project["name"]}')
        self.helper.get(self.URL_FIELD_COMMENTS.format(project['pid']))

        for r in self.helper.get_elements(CssSelector('table#table-dq_field_comment_table tbody tr')):
            cells = self.helper.get_elements(CssSelector('td'), element=r)

            field_comments_file.add_item(dict(
                record=self.helper.get_text(cells[1]),
                field=self.helper.get_text(cells[2]),
                comments=self.helper.get_text(cells[3]),
            ))

    def run(self):
        p = ProjectFileGroup(self.helper)
        project_file =  p.get_file()

        for project in project_file.get_items():
            field_comments_file =  self.field_comments_file_group.get_file({
                'pid': project['pid'],
                'project_name': project['name'],
            })

            if not field_comments_file.exists():
                self.export_field_comments(project, field_comments_file)
    
                field_comments_file.save()
