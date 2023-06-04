import json


from flask import Flask, request
from flask_cors import CORS


from loader.pretrained_loader import get_all_pretrained_models_metadata, translate_to_sql
from schema_parser.json_schema_parser import parse_json_schema


app = Flask(__name__)
cors = CORS(app)


@app.route('/pretrained_models_metadata')
def get_pretrained_models_metadata():
    return get_all_pretrained_models_metadata()


@app.route('/submit', methods=['POST'])
def submit():
    if 'file' not in request.files or 'natural_language_query' not in request.form or 'pretrained_model' not in request.form:
        return 'Invalid request: file, query, or pretrained model was not correctly specified.', 400

    file_storage = request.files.get('file')
    natural_language_query = request.form.get('natural_language_query')
    pretrained_model_dir = request.form.get('pretrained_model')

    column_data_dict = parse_json_schema(file_storage)
    return translate_to_sql(natural_language_query, pretrained_model_dir, column_data_dict)


if __name__ == '__main__':
    app.run()
