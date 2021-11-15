import jsonlines
from werkzeug.utils import secure_filename


class ItemsFile():
    def __init__(self, output_directory, object_name):
        self.output_directory = output_directory
        self.object_name = object_name
        self.items = []

    def _export_filename(self):
        return secure_filename(f'{self.object_name}_items.jsonl')

    def add_item(self, name, href):
        item = {
            'name': name,
            'href': href,
        }

        if item not in self.items:
            self.items.append(item)

    def save(self):
        with jsonlines.open(self.output_directory / self._export_filename(), mode='w') as writer:
            for i in sorted(self.items, key=lambda i: i['name']):
                writer.write(i)
