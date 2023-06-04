import json
import chardet


def parse_json_schema(file_storage):
    data = json.load(file_storage)
    column_data = data['columns']

    column_names = []
    column_types = []

    for column_dict in column_data:
        column_names.append(column_dict['name'])
        column_types.append(column_dict['type'])

    return {'column_names': column_names, 'column_types': column_types}
