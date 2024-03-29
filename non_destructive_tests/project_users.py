import logging
from lbrc_selenium import ItemFileGroup
from lbrc_selenium.selenium import CssSelector
from non_destructive_tests import ProjectFileGroup


def get_project_user_tester(helper):
    return ProjectUserTester(helper)


class UserFileGroup(ItemFileGroup):
    def __init__(self, helper):
        super().__init__(helper, helper.output_directory / 'users', 'users_{pid}_{project_name}')


class ProjectUserTester():
    def __init__(self, helper):
        self.helper = helper

    def run(self):
        steps = [
            ProjectUsers(self.helper),
        ]

        for s in steps:
            s.run()


class ProjectUsers():
    URL_PROJECT_USERS = 'UserRights/index.php?pid={}'
    
    def __init__(self, helper):
        self.helper = helper
        self.users_file_group = UserFileGroup(self.helper)

    def export_users(self, project, users_file):
        logging.info(f'Export users for project {project["name"]}')
        self.helper.get(self.URL_PROJECT_USERS.format(project['pid']))

        for r in self.helper.get_elements(CssSelector('table#table-user_rights_roles_table tbody tr')):
            cells = self.helper.get_elements(CssSelector('td'), element=r)

            for u in self.helper.get_elements(CssSelector('a.userLinkInTable'), element=cells[1]):

                users_file.add_item(dict(
                    role=self.helper.get_text(cells[0]),
                    username=self.helper.get_text(u),
                ))

    def run(self):
        p = ProjectFileGroup(self.helper)
        project_file =  p.get_file()

        for project in project_file.get_items():
            users_file =  self.users_file_group.get_file({
                'pid': project['pid'],
                'project_name': project['name'],
            })

            if not users_file.exists():
                self.export_users(project, users_file)
        
                users_file.save()
