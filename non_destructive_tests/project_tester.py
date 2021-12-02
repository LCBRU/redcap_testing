import logging
from helper.selenium import CssSelector, XpathSelector
from helper import ItemFileGroup
from urllib.parse import urlparse
from urllib.parse import parse_qs
from non_destructive_tests import ProjectFileGroup


def get_project_tester(helper):
    return ProjectTester(helper)


class RecordFileGroup(ItemFileGroup):
    def __init__(self, helper):
        super().__init__(helper, helper.output_directory / 'projects' / 'records', 'records_{pid}_{project_name}')


class InstrumentFileGroup(ItemFileGroup):
    def __init__(self, helper):
        super().__init__(helper, helper.output_directory / 'projects' / 'instruments', 'instruments_{pid}_{record}')


class InstrumentDetailsFileGroup(ItemFileGroup):
    def __init__(self, helper):
        super().__init__(helper, helper.output_directory / 'projects' / 'instrument_details', 'instrument_details_{pid}_{record}', sorted=False)


class ProjectTester():
    def __init__(self, helper):
        self.helper = helper

    def run(self):
        steps = [
            # ProjectExporter(self.helper),
            # ProjectRecordExtractor(self.helper),
            # ProjectRecordInstrumentExtractor(self.helper),
            ProjectRecordInstrumentDetails(self.helper),
        ]

        for s in steps:
            s.run()


class ProjectExporter():
    URL_VIEW_ALL_PROJECTS = 'ControlCenter/view_projects.php?view_all=1'

    def __init__(self, helper):
        self.helper = helper

    def export_projects(self):
        logging.info('Extracting projects')

        pfg = ProjectFileGroup(self.helper)
        pfg.clean()
        self.project_file =  pfg.get_file()

        self.helper.get(self.URL_VIEW_ALL_PROJECTS)

        self.helper.wait_to_disappear(XpathSelector('//span[text()="Loading..."]'))

        output_file = self.project_file

        for tr in self.helper.get_elements(CssSelector('tr.myprojstripe')):
            a = self.helper.get_element(CssSelector('div.projtitle > a'), element=tr)
            records = self.helper.get_text(
                self.helper.get_element(CssSelector("span[class^='pid-cntr-']"), element=tr)
            )

            href = self.helper.get_href(a)
            name=self.helper.get_text(a).split(' PID ')[0]

            logging.info(f'Saving project {name}')

            output_file.add_item(dict(
                pid=parse_qs(urlparse(href).query).get('pid', [None])[0],
                name=name,
                href=href,
                records=records,
            ))

        output_file.save()

    def run(self):
        self.export_projects()


class ProjectRecordExtractor():
    URL_ADD_EDIT_RECORDS = 'DataEntry/record_home.php?pid={}'
    
    def __init__(self, helper):
        self.helper = helper
        self.record_file_group = RecordFileGroup(self.helper)

    def export_project_records(self, project):
        record_file =  self.record_file_group.get_file({
            'pid': project['pid'],
            'project_name': project['name'],
        })

        logging.info(f'Extracting records from project {project["name"]}')
        self.helper.get(self.URL_ADD_EDIT_RECORDS.format(project['pid']))

        select = self.helper.wait_to_appear(CssSelector('select#record'))

        for o in self.helper.get_elements(CssSelector('option'), element=select):
            record = o.get_attribute("value")

            if record:
                logging.info(f'Saving record {record} for project {project["name"]}')

                record_file.add_item(dict(
                    pid=project['pid'],
                    record=record,
                ))
    
        record_file.save()

    def run(self):
        p = ProjectFileGroup(self.helper)
        project_file =  p.get_file()

        self.record_file_group.clean()

        for project in project_file.get_sample_items(filter=lambda i: int(i['records']) > 0):
            self.export_project_records(project)


class ProjectRecordInstrumentExtractor():
    URL_RECORD_HOME = 'DataEntry/record_home.php?pid={pid}&id={record}'

    def __init__(self, helper):
        self.helper = helper

    def export_record_instruments(self, record, instrument_file):
        logging.info(f'Extracting instruments for record {record["record"]} from project {record["pid"]}')
        self.helper.get(self.URL_RECORD_HOME.format(pid=record['pid'], record=record['record']))

        visits = [self.helper.get_text(h) for h in self.helper.get_elements(CssSelector('table#event_grid_table thead th'))]

        for row in self.helper.get_elements(CssSelector('table#event_grid_table tbody tr')):
            tds  = self.helper.get_elements(CssSelector('td'), element=row)

            instrument_name = self.helper.get_text(tds[0])

            if instrument_name == 'Delete all data on event:':
                continue

            for i, td in enumerate(tds[1:], start=1):
                links = self.helper.get_elements(CssSelector('a'), element=td)

                if len(links) > 0:

                    href = self.helper.get_href(links[0])

                    logging.info(f'Saving instrument {instrument_name} for project {record["pid"]} and record {record["record"]}')

                    instrument_file.add_item(dict(
                        pid=record["pid"],
                        record=record['record'],
                        instrument_name=instrument_name,
                        visit_name=visits[i],
                        href=href,
                    ))

    def run(self):
        pfg = ProjectFileGroup(self.helper)
        project_file =  pfg.get_file()
        rfg = RecordFileGroup(self.helper)
        ifg = InstrumentFileGroup(self.helper)

        for project in project_file.get_sample_items(filter=lambda i: int(i['records']) > 0):
            record_file =  rfg.get_file({
                'pid': project['pid'],
                'project_name': project['name'],
            })
            for record in record_file.get_sample_items():
                instrument_file =  ifg.get_file({
                    'pid': record['pid'],
                    'record': record['record'],
                })

                if not instrument_file.exists():
                    self.export_record_instruments(record, instrument_file)

                    instrument_file.save()


class ProjectRecordInstrumentDetails():
    def __init__(self, helper):
        self.helper = helper

    def export_instrument_details(self, instrument, instrument_details_file):
        logging.info(f'Extracting details for instrument {instrument["instrument_name"]} for visit {instrument["visit_name"]} from project {instrument["pid"]} for participant {instrument["record"]}')
        self.helper.get(instrument['href'])
        fs = FieldSelector(self.helper)


        for i, row in enumerate(self.helper.get_elements(CssSelector('table#questiontable tbody tr[id]'))):
            if row.is_displayed():
                f = fs.get_field(row, i)

                if f:
                    f.save_to_items_file(instrument_details_file, instrument)

    def run(self):
        pfg = ProjectFileGroup(self.helper)
        project_file =  pfg.get_file()
        rfg = RecordFileGroup(self.helper)
        ifg = InstrumentFileGroup(self.helper)
        idfg = InstrumentDetailsFileGroup(self.helper)

        for project in project_file.get_sample_items(filter=lambda i: int(i['records']) > 0):
            record_file =  rfg.get_file({
                'pid': project['pid'],
                'project_name': project['name'],
            })
            for record in record_file.get_sample_items():

                instrument_file =  ifg.get_file({
                    'pid': record['pid'],
                    'record': record['record'],
                })

                instrument_details_file =  idfg.get_file({
                    'pid': project['pid'],
                    'record': record['record'],
                })

                if not instrument_details_file.exists():
                    for instrument in instrument_file.get_items():
                        self.export_instrument_details(instrument, instrument_details_file)

                    instrument_details_file.save()


class FieldSelector:
    def __init__(self, helper):
        self.helper = helper

        self.field_types = [
            MatrixHeader,
            MatrixCheckboxRow,
            MatrixRadioRow,
            HorizontalRadiosField,
            HorizontalCheckboxField,
            VericalRadiosField,
            VericalCheckboxField,
            ReadOnlyTextInputField,
            TextInputField,
            SelectInputField,
            HeaderField,
            DescriptiveField,
            ReadOnlyField,
            UnknownField,
        ]

    def get_field(self, row, row_number):
        if row.get_attribute("id") in [
            '__LOCKRECORD__-tr',
            '__SUBMITBUTTONS__-tr',
            '__DELETEBUTTONS__-tr',
        ]:
            return None

        cells = self.helper.get_elements(XpathSelector('./td'), element=row)

        for ft in self.field_types:
            f = ft(row, row_number, self.helper, cells)

            if f.is_of_type():
                return f


class Field:
    def __init__(self, row, row_number, helper, cells):
        self.row = row
        self.row_number = row_number
        self.helper = helper
        self.cells = cells

    def is_of_type(self):
        return False

    def _get_horizontal_name(self):
        label = self.helper.get_element(CssSelector('td table td'), element=self.row)
        return '#{} {}'.format(self.row_number, self.helper.get_text(label))

    def _get_vertical_name(self):
        return '#{} {}'.format(self.row_number, self.helper.get_text(self.cells[0]))

    @property
    def field_name(self):
        return self._get_vertical_name()

    @property
    def value(self):
        return ''

    @property
    def field_type(self):
        return type(self).__name__

    def save_to_items_file(self, items_file, instrument):
        logging.info(f'Saving {self.field_type}: {self.field_name} = {self.value}')
        items_file.add_item(dict(
            instrument_name=instrument['instrument_name'],
            visit_name=instrument['visit_name'],
            field_type=self.field_type,
            field_name=self.field_name,
            value=self.value or '',
        ))

class HeaderField(Field):
    def is_of_type(self):
        return (
            len(self.cells) == 1 and
            self.cells[0].get_attribute("class") == 'header'
        )


class DescriptiveField(Field):
    def is_of_type(self):
        return (
            len(self.cells) == 1 and
            'labelrc' in self.cells[0].get_attribute("class")
        )


class ReadOnlyField(Field):
    def is_of_type(self):
        return (
            len(self.cells) == 2 and
            'labelrc' in self.cells[0].get_attribute("class")
        )

    @property
    def value(self):
        return self.helper.get_text(self.cells[1])


class ReadOnlyTextInputField(Field):
    def __init__(self, row, row_number, helper, cells):
        super().__init__(row, row_number, helper, cells)

        self.readonly_inputs = self.helper.get_elements(CssSelector('input[type="text"][readonly]'), element=self.row)

    def is_of_type(self):
        return (
            len(self.cells) == 2 and
            len(self.readonly_inputs) > 0
        )

    @property
    def value(self):
        return self.readonly_inputs[0].get_attribute('value')


class TextInputField(Field):
    def __init__(self, row, row_number, helper, cells):
        super().__init__(row, row_number, helper, cells)

        self.text_inputs = self.helper.get_elements(CssSelector('input[type="text"]'), element=self.row)

    def is_of_type(self):
        return (
            len(self.cells) == 2 and
            len(self.text_inputs) > 0
        )

    @property
    def value(self):
        return self.text_inputs[0].get_attribute('value')


class SelectInputField(Field):
    def __init__(self, row, row_number, helper, cells):
        super().__init__(row, row_number, helper, cells)

        self.select_inputs = self.helper.get_elements(CssSelector('select'), element=self.row)

    def is_of_type(self):
        return (
            len(self.cells) == 2 and
            len(self.select_inputs) > 0
        )

    @property
    def value(self):
        selected_options = self.helper.get_elements(CssSelector('option[selected]'), element=self.select_inputs[0])

        if len(selected_options) > 0:
            return self.helper.get_text(selected_options[0])


class MatrixHeader(Field):
    def __init__(self, row, row_number, helper, cells):
        super().__init__(row, row_number, helper, cells)

        self.inputs = self.helper.get_elements(CssSelector('input'), element=self.row)

    def is_of_type(self):
        return self.row.get_attribute('mtxgrp') and len(self.inputs) == 0

    def save_to_items_file(self, items_file, instrument):
        logging.info(f'Saving {self.field_type}: Skipping')


class MatrixCheckboxRow(Field):
    def __init__(self, row, row_number, helper, cells):
        super().__init__(row, row_number, helper, cells)

        self.checkboxes = self.helper.get_elements(CssSelector('input[type="checkbox"]'), element=self.row)

    def is_of_type(self):
        return self.row.get_attribute('mtxgrp') and len(self.checkboxes) > 0

    @property
    def value(self):
        row_parent = self.helper.get_parent(self.row)
        header_row = self.helper.get_element(CssSelector('tr[id$="-mtxhdr-tr"][mtxgrp="{}"]'.format(self.row.get_attribute("mtxgrp"))), element=row_parent)
        headers = [self.helper.get_text(h) for h in self.helper.get_elements(CssSelector('td table td:not(:first-of-type)'), element=header_row)]

        hidden_fields = self.helper.get_elements(CssSelector('input[type="hidden"]'), element=self.row)

        values = []

        for f, h in zip(hidden_fields, headers):
            if len(f.get_attribute('value')) > 0:
                values.append(h)

        return '; '.join(values)


class MatrixRadioRow(Field):
    def __init__(self, row, row_number, helper, cells):
        super().__init__(row, row_number, helper, cells)

        self.radios = self.helper.get_elements(CssSelector('input[type="radio"]'), element=self.row)

    def is_of_type(self):
        return self.row.get_attribute('mtxgrp') and len(self.radios) > 0

    @property
    def value(self):
        row_parent = self.helper.get_parent(self.row)
        header_row = self.helper.get_element(CssSelector('tr[id$="-mtxhdr-tr"][mtxgrp="{}"]'.format(self.row.get_attribute("mtxgrp"))), element=row_parent)
        headers = [self.helper.get_text(h) for h in self.helper.get_elements(CssSelector('td table td:not(:first-of-type)'), element=header_row)]

        values = []

        for f, h in zip(self.radios, headers):
            if f.get_attribute('checked'):
                values.append(h)

        return '; '.join(values)


class HorizontalRadiosField(Field):
    def __init__(self, row, row_number, helper, cells):
        super().__init__(row, row_number, helper, cells)

        self.radios = self.helper.get_elements(CssSelector('input[type="radio"]'), element=self.row)

    def is_of_type(self):
        return (
            len(self.cells) == 1 and
            len(self.radios) > 0
        )

    @property
    def field_name(self):
        return self._get_horizontal_name()

    @property
    def value(self):
        for r in self.radios:
            if r.get_attribute("checked"):
                parent = self.helper.get_element(XpathSelector("./.."), element=r)
                return self.helper.get_text(parent)

        return ''


class HorizontalCheckboxField(Field):
    def __init__(self, row, row_number, helper, cells):
        super().__init__(row, row_number, helper, cells)

        self.checkboxes = self.helper.get_elements(CssSelector('input[type="checkbox"]'), element=self.row)

    def is_of_type(self):
        return (
            len(self.cells) == 1 and
            len(self.checkboxes) > 0
        )

    @property
    def field_name(self):
        return self._get_horizontal_name()

    @property
    def value(self):
        checked = []
        for c in self.helper.get_elements(CssSelector('input[type="hidden"][value]'), element=self.row):
            if c.get_attribute('value'):
                parent = self.helper.get_element(XpathSelector("./.."), element=c)
                checked.append(self.helper.get_text(parent))
        
        return '; '.join(checked)


class VericalRadiosField(Field):
    def __init__(self, row, row_number, helper, cells):
        super().__init__(row, row_number, helper, cells)

        self.radios = self.helper.get_elements(CssSelector('input[type="radio"]'), element=self.row)

    def is_of_type(self):
        return (
            len(self.cells) == 2 and
            len(self.radios) > 0
        )

    @property
    def field_name(self):
        return self._get_horizontal_name()

    @property
    def value(self):
        for r in self.radios:
            if r.get_attribute("checked"):
                parent = self.helper.get_element(XpathSelector("./.."), element=r)
                return self.helper.get_text(parent)
        
        return ''


class VericalCheckboxField(Field):
    def __init__(self, row, row_number, helper, cells):
        super().__init__(row, row_number, helper, cells)

        self.checkboxes = self.helper.get_elements(CssSelector('input[type="checkbox"]'), element=self.row)

    def is_of_type(self):
        return (
            len(self.cells) == 2 and
            len(self.checkboxes) > 0
        )

    @property
    def field_name(self):
        return self._get_horizontal_name()

    @property
    def value(self):
        checked = []
        for c in self.helper.get_elements(CssSelector('input[type="hidden"][value]'), element=self.row):
            if c.get_attribute('value'):
                parent = self.helper.get_element(XpathSelector("./.."), element=c)
                checked.append(self.helper.get_text(parent))
        
        return '; '.join(checked)


class UnknownField(Field):
    def is_of_type(self):
        return True

    @property
    def field_type(self):
        return '--------------------- Unknown ----------------------------'
