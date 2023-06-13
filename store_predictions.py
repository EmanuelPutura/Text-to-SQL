import logging
import argparse
import torch
import importlib

from datasets import load_dataset
from transformers import AutoTokenizer, T5ForConditionalGeneration


MODEL_INPUTS_MODULE_NAME = 'model_inputs.model_inputs'


class WikiSQLPredictionsStorage:
    @staticmethod
    def store_predictions_in_file(model_inputs_class, model, tokenizer, evaluated_data, file_path, device):
        with open(file_path, 'w', encoding='utf-8') as file:
            index = 0

            for row in evaluated_data:
                column_data_dict = {'table_name': row['table']['name'], 'column_names': row['table']['header'], 'column_types': row['table']['types']}

                predicted_query = model_inputs_class.translate_to_sql(model, tokenizer, row['question'], column_data_dict, device)
                file.write(predicted_query + '\n')

                if index % 100 == 0:
                    logger.info('Storing predictions in file, row = {}'.format(index))
                index += 1


if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s : %(name)s - %(levelname)s : %(message)s')
    logger = logging.getLogger('root')
    logger.setLevel(logging.INFO)

    parser = argparse.ArgumentParser(
        prog='Text-to-SQL Predictions Storage Module',
        description='Module used for storing the predictions of a model in a given file',
    )

    parser.add_argument('--input-format-class', type=str, required=True, help='Specify the model input format, defined in a class from the model_inputs module')
    parser.add_argument('--file-path', type=str, required=True, help='Specify the path of the file where to store the model predictions')
    parser.add_argument('--pretrained-path', type=str, required=True, help='Specify the path to the pretrained model to evaluate')
    args = parser.parse_args()

    model_inputs_class_str = args.input_format_class
    module = importlib.import_module(MODEL_INPUTS_MODULE_NAME)
    model_inputs_class = getattr(module, model_inputs_class_str)

    FILE_PATH = args.file_path
    PATH_TO_TRAINED_MODEL = args.pretrained_path

    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    logger.info('Running on \'%s\' device', device)

    tokenizer = AutoTokenizer.from_pretrained(PATH_TO_TRAINED_MODEL)
    model = T5ForConditionalGeneration.from_pretrained(PATH_TO_TRAINED_MODEL)
    model.to(device)

    test_data = load_dataset('wikisql', split='test')
    WikiSQLPredictionsStorage.store_predictions_in_file(model_inputs_class, model, tokenizer, test_data, FILE_PATH, device)
