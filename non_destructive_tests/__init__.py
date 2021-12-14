
from helper import ItemFileGroup


class ProjectFileGroup(ItemFileGroup):
    def __init__(self, helper):
        super().__init__(helper, helper.output_directory / 'projects', 'projects')


class RecordFileGroup(ItemFileGroup):
    def __init__(self, helper):
        super().__init__(helper, helper.output_directory / 'projects' / 'records', 'records_{pid}_{project_name}')


class InstrumentFileGroup(ItemFileGroup):
    def __init__(self, helper):
        super().__init__(helper, helper.output_directory / 'projects' / 'instruments', 'instruments_{pid}_{record}')


class InstrumentDetailsFileGroup(ItemFileGroup):
    def __init__(self, helper):
        super().__init__(helper, helper.output_directory / 'projects' / 'instrument_details', 'instrument_details_{pid}_{record}', sorted=False)
