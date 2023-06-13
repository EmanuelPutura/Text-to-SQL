import os
import json
import importlib
import inspect


from transformers import AutoTokenizer, T5ForConditionalGeneration


CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PRETRAINED_MODELS_PATH = os.path.join(CURRENT_DIR, '../pretrained/')

METADATA_FILE_NAME = 'metadata.json'
MODEL_INPUTS_MODULE_NAME = 'model_inputs.model_inputs'


pretrained_models_dict = {}


def get_all_pretrained_models_dir_names():
    pretrained_model_names = []
    if os.path.isdir(PRETRAINED_MODELS_PATH):
        pretrained_model_names = [name for name in os.listdir(PRETRAINED_MODELS_PATH) if os.path.isdir(os.path.join(PRETRAINED_MODELS_PATH, name))]
    return pretrained_model_names


def get_pretrained_model_metadata_from_dir(pretrained_model_dir_name):
    model_path = os.path.join(PRETRAINED_MODELS_PATH, pretrained_model_dir_name)
    metadata_path = os.path.join(model_path, METADATA_FILE_NAME)

    with open(metadata_path, 'r') as file:
        json_data = json.load(file)
    return json_data


def get_all_pretrained_models_metadata():
    pretrained_dir_names = get_all_pretrained_models_dir_names()
    json_data_dict = {}

    for dir in pretrained_dir_names:
        json_data_dict[dir] = get_pretrained_model_metadata_from_dir(dir)
    return json_data_dict


def get_pretrained_model_class_from_dir(pretrained_model_dir_name):
    metadata = get_pretrained_model_metadata_from_dir(pretrained_model_dir_name)
    module = importlib.import_module(MODEL_INPUTS_MODULE_NAME)
    class_name = metadata['class_name']

    return getattr(module, class_name)


def get_pretrained_model_path(model_dir):
    return os.path.join(PRETRAINED_MODELS_PATH, model_dir)


def translate_to_sql(query, pretrained_model_dir, column_data_dict):
    path_to_pretrained_model = get_pretrained_model_path(pretrained_model_dir)

    if pretrained_model_dir in pretrained_models_dict:
        tokenizer = pretrained_models_dict[pretrained_model_dir]['tokenizer']
        model = pretrained_models_dict[pretrained_model_dir]['model']
    else:
        tokenizer = AutoTokenizer.from_pretrained(path_to_pretrained_model)
        model = T5ForConditionalGeneration.from_pretrained(path_to_pretrained_model)
        pretrained_models_dict[pretrained_model_dir] = {'tokenizer': tokenizer, 'model': model}

    model_class = get_pretrained_model_class_from_dir(pretrained_model_dir)
    return model_class.translate_to_sql(model, tokenizer, query, column_data_dict)
