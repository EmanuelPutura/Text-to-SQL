import json
import jwt


from datetime import datetime, timedelta
from flask import Flask, request, make_response, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash


from loader.pretrained_loader import get_all_pretrained_models_metadata, translate_to_sql
from schema_parser.json_schema_parser import get_table_schema_from_json


app = Flask(__name__)
cors = CORS(app)

# TODO: don't hardcode the configuration, store it in a .env file instead
app.config['SECRET_KEY'] = 'test_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///TextToSQLDb.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

db = SQLAlchemy(app)
# app.app_context().push()


# Database ORMs
class User(db.Model):
    username = db.Column(db.String(50), primary_key=True)
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    password = db.Column(db.String(80))


class UserTableSchema(db.Model):
    table_name = db.Column(db.String(50), primary_key=True)
    username = db.Column(db.String(50))
    column_names = db.Column(db.String(100))
    column_types = db.Column(db.String(100))


@app.route('/pretrained_models_metadata')
def get_pretrained_models_metadata():
    return get_all_pretrained_models_metadata()


@app.route('/user_table_schemas/<username>')
def get_user_table_schemas(username):
    tables = UserTableSchema.query.filter_by(username=username).all()
    table_schemas = list(map(lambda table: table.table_name, tables))
    return table_schemas


@app.route('/submit/guest_query', methods=['POST'])
def submit_guest_query():
    if 'file' not in request.files or 'natural_language_query' not in request.form or 'pretrained_model' not in request.form:
        return 'Invalid request: file, query, or pretrained model was not correctly specified.', 400

    file_storage = request.files.get('file')
    natural_language_query = request.form.get('natural_language_query')
    pretrained_model_dir = request.form.get('pretrained_model')

    table_data_dict = get_table_schema_from_json(file_storage)
    query = translate_to_sql(natural_language_query, pretrained_model_dir, table_data_dict)

    json_response = jsonify({
        'query': query,
    })
    return make_response(json_response, 200)


@app.route('/submit/home_query', methods=['POST'])
def submit_home_query():
    if 'natural_language_query' not in request.form or 'pretrained_model' not in request.form or 'table_schema_name' not in request.form:
        return 'Invalid request: file, query, or pretrained model was not correctly specified.', 400

    natural_language_query = request.form.get('natural_language_query')
    pretrained_model_dir = request.form.get('pretrained_model')
    table_schema_name = request.form.get('table_schema_name')

    table = UserTableSchema.query.filter_by(table_name=table_schema_name).first()
    table_data_dict = {'table_name': table.table_name, 'column_names': table.column_names.split(','), 'column_types': table.column_types.split(',')}
    query = translate_to_sql(natural_language_query, pretrained_model_dir, table_data_dict)

    json_response = jsonify({
        'query': query,
    })
    return make_response(json_response, 200)


@app.route('/submit/schema', methods=['POST'])
def submit_schema():
    if 'file' not in request.files or 'username' not in request.form:
        return 'Invalid request: file, or username was not correctly specified.', 400

    file_storage = request.files.get('file')
    username = request.form.get('username')
    table_data_dict = get_table_schema_from_json(file_storage)
    table_name = table_data_dict['table_name']

    table = UserTableSchema.query.filter_by(table_name=table_name).first()
    if not table:
        table = UserTableSchema(
            table_name=table_name,
            username=username,
            column_names=','.join(table_data_dict['column_names']),
            column_types=','.join(table_data_dict['column_types'])
        )

        db.session.add(table)
        db.session.commit()

        json_response = jsonify({
            'status': 'table_schema_successfully_added',
            'message': 'The table schema has been successfully added.',
            'table_name': table_name
        })
        return make_response(json_response, 201)
    else:
        json_response = jsonify({
            'status': 'table_schema_already_added',
            'message': 'The table schema has already been added.'
        })
        return make_response(json_response, 202)


@app.route('/users/register', methods=['POST'])
def register():
    if 'firstName' not in request.json or 'lastName' not in request.json or 'password' not in request.json or 'username' not in request.json:
        return 'Invalid request: first name, last name, password, or username was not correctly specified.', 400

    first_name = request.json.get('firstName')
    last_name = request.json.get('lastName')
    password = request.json.get('password')
    username = request.json.get('username')

    user = User.query.filter_by(username=username).first()
    if not user:
        user = User(
            username=username,
            first_name=first_name,
            last_name=last_name,
            password=generate_password_hash(password)
        )

        db.session.add(user)
        db.session.commit()

        json_response = jsonify({
            'status': 'registered',
            'message': 'Successfully registered user \'{}\'.'.format(username)
        })
        return make_response(json_response, 201)
    else:
        json_response = jsonify({
            'status': 'already_registered',
            'message': 'User \'{}\' already exists, please log in.'.format(username)
        })
        return make_response(json_response, 202)


@app.route('/users/authenticate', methods=['POST'])
def login():
    if 'username' not in request.json or 'password' not in request.json:
        return 'Invalid request: username or password was not correctly specified.', 400

    username = request.json.get('username')
    password = request.json.get('password')

    user = User.query.filter_by(username=username).first()
    if not user:
        json_response = jsonify({
            'status': 'unregistered_user',
            'message': 'User \'{}\' does not exist.'.format(username)
        })
        return make_response(json_response, 401)

    if check_password_hash(user.password, password):
        token = jwt.encode({
            'username': username,
            'exp': datetime.utcnow() + timedelta(minutes=30)
        }, app.config['SECRET_KEY'])

        json_response = jsonify({
            'username': username,
            'password': password,
            'firstName': user.first_name,
            'lastName': user.last_name,
            'token': token
        })
        return make_response(json_response, 201)

    json_response = jsonify({
        'status': 'invalid_password',
        'message': 'Invalid password.'
    })
    return make_response(json_response, 403)


if __name__ == '__main__':
    app.run()
