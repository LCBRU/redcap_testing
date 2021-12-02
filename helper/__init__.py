import shutil
import math
import os
import jsonlines
from werkzeug.utils import secure_filename


# Helpers
class Sampler:
    TYPE_ALL = 'all'
    TYPE_FIBONACCI = 'fibonacci'
    TYPE_FIRST = 'first'

    def __init__(self):
        self.sampling_type = os.environ.get("SAMPLING_TYPE", self.TYPE_ALL)

    def is_sampling_pick(self, n):
        is_perfect_square = lambda x: int(math.sqrt(x))**2 == x

        if self.sampling_type.isnumeric():
            if (n % 100) < int(self.sampling_type.isnumeric()):
                return True
            else:
                return False

        if self.sampling_type == Sampler.TYPE_ALL:
            return True
        elif self.sampling_type == Sampler.TYPE_FIRST:
            return n == 0
        else:
            return is_perfect_square(5*n*n + 4) or is_perfect_square(5*n*n - 4)


class ItemFileGroup():
    def __init__(self, helper, output_directory, filename_template, sorted=True):
        self.helper = helper
        self.output_directory = output_directory
        self.filename_template = filename_template
        self.sorted = sorted

    def get_file(self, template_arguments=None):
        self.output_directory.mkdir(parents=True, exist_ok=True)

        if template_arguments:
            filename = self.filename_template.format(**template_arguments)
        else:
            filename = self.filename_template

        return ItemsFile(self.output_directory, filename, sorted=self.sorted)

    def clean(self):
        if os.path.exists(self.output_directory):
            shutil.rmtree(self.output_directory)


class ItemsFile():
    def __init__(self, output_directory, filename, sorted=True):
        self.output_directory = output_directory
        self.filename = filename
        self.items = []
        self.sorted = sorted

    def _export_filename(self):
        return secure_filename(f'{self.filename}.jsonl')

    def add_item(self, item):
        if item not in self.items:
            self.items.append(item)

    def exists(self):
        return (self.output_directory / self._export_filename()).exists()

    def save(self):
        with jsonlines.open(self.output_directory / self._export_filename(), mode='w') as writer:
            if self.sorted:
                for i in sorted(self.items, key=lambda i: list(i.values())):
                    writer.write(i)
            else:
                for i in self.items:
                    writer.write(i)

    def get_items(self, filter=None):
        with jsonlines.open(self.output_directory / self._export_filename()) as reader:
            for item in reader:
                if filter and not filter(item):
                    continue

                yield item


    def get_sample_items(self, filter=None):
        sampler = Sampler()

        with jsonlines.open(self.output_directory / self._export_filename()) as reader:
            n = 0

            for item in reader:
                if filter and not filter(item):
                    continue

                if sampler.is_sampling_pick(n):
                    yield item
                    
                n += 1
