import logging
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


class ItemsFile():
    def __init__(self, output_directory, object_name):
        self.output_directory = output_directory
        self.object_name = object_name
        self.items = []

    def _export_filename(self):
        return secure_filename(f'{self.object_name}_items.jsonl')

    def add_item(self, item):
        if item not in self.items:
            self.items.append(item)

    def save(self):
        with jsonlines.open(self.output_directory / self._export_filename(), mode='w') as writer:
            for i in sorted(self.items, key=lambda i: list(i.values())):
                writer.write(i)

    def get_items(self):
        with jsonlines.open(self.output_directory / self._export_filename()) as reader:
            for i in reader:
                yield i

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
