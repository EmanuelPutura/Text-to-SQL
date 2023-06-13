import argparse
import torch
import logging
import importlib

from text_to_sql_model.model import TextToSQLModel


MODEL_INPUTS_MODULE_NAME = 'model_inputs.model_inputs'


if __name__ == "__main__":
    logging.basicConfig(format='%(asctime)s : %(name)s - %(levelname)s : %(message)s')
    logger = logging.getLogger('root')
    logger.setLevel(logging.INFO)

    parser = argparse.ArgumentParser(
        prog='Text-to-SQL',
        description='ML models used for the Text-to-SQL task',
    )

    parser.add_argument('--base-model', type=str, required=True, help='Specify the model you want to fine tune', choices=['t5', 'code-t5'])
    parser.add_argument('--input-format-class', type=str, help='Specify the model input format, defined in a class from the model_inputs module')
    parser.add_argument('--pretrained-path', type=str, help='Specify where to store the model after training')
    args = parser.parse_args()

    base_model_name = {
        't5': 't5-small',
        'code-t5': 'Salesforce/codet5-small',
    }.get(args.base_model, 't5-small')

    model_inputs_class_str = args.input_format_class
    module = importlib.import_module(MODEL_INPUTS_MODULE_NAME)
    model_inputs_class = getattr(module, model_inputs_class_str)

    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    logger.info('Running on \'%s\' device', device)

    model = TextToSQLModel(base_model_name, model_inputs_class, args.pretrained_path, device)
    model.train(save_model=True)
