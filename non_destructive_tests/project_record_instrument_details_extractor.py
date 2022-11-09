import logging
from helper.selenium import CssSelector, XpathSelector
from non_destructive_tests import ProjectFileGroup, RecordFileGroup, InstrumentFileGroup, InstrumentDetailsFileGroup


def get_project_record_instrument_details_extractor(helper):
    return ProjectRecordInstrumentDetailsExtractor(helper)


class ProjectRecordInstrumentDetailsExtractor():
    def __init__(self, helper):
        self.helper = helper

    def export_instrument_details(self, instrument, instrument_details_file):
        logging.info(f'Extracting details for instrument: \'{instrument["instrument_name"]}\' for visit: \'{instrument["visit_name"]}\'')
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

        for project in project_file.get_items():
            logging.info(f'Extracting instrument details for project {project["name"]}')
            record_file =  rfg.get_file({
                'pid': project['pid'],
                'project_name': project['name'],
            })
            for record in record_file.get_sample_items():
                logging.info(f'Extracting instrument details for record {record["record"]}')

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
        logging.debug(f'Saving {self.field_type}: {self.field_name} = {self.value}')
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
        logging.debug(f'Saving {self.field_type}: Skipping')


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
