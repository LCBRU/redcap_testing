
from helper import ItemFileGroup


class ProjectFileGroup(ItemFileGroup):
    def __init__(self, helper):
        super().__init__(helper, helper.output_directory / 'projects', 'projects')
