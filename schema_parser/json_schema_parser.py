import json
import chardet


def get_table_schema_from_json(file_storage):
    data = json.load(file_storage)
    table_name = data['name']
    column_data = data['columns']

    column_names = []
    column_types = []

    for column_dict in column_data:
        column_names.append(column_dict['name'])
        column_types.append(column_dict['type'])

    return {'table_name': table_name, 'column_names': column_names, 'column_types': column_types}
