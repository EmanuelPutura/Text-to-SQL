import argparse
import torch
import logging
import importlib

from transformers import AutoTokenizer, T5ForConditionalGeneration
from transformers import Seq2SeqTrainer
from transformers import Seq2SeqTrainingArguments
from transformers import get_linear_schedule_with_warmup

from dataset_preprocessor.wikisql_preprocessor import WikiSQLPreprocessor
from eval.rouge_metrics import RougeMetrics


MODEL_INPUTS_MODULE_NAME = 'model_inputs.model_inputs'
EPOCHS_NUMBER = 15
BATCH_SIZE = 16


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

    PATH_TO_TRAINED_MODEL = args.pretrained_path

    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    logger.info('Running on \'%s\' device', device)

    tokenizer = AutoTokenizer.from_pretrained(base_model_name, model_max_length=1024)
    rouge_metrics = RougeMetrics(tokenizer)

    base_model = T5ForConditionalGeneration.from_pretrained(base_model_name)
    base_model.to(device)

    wikisql_preprocessor = WikiSQLPreprocessor(model_inputs_class, tokenizer)
    train_data = wikisql_preprocessor.train_data()
    test_data = wikisql_preprocessor.test_data()

    training_args = Seq2SeqTrainingArguments(
        output_dir=PATH_TO_TRAINED_MODEL,
        per_device_train_batch_size=BATCH_SIZE,
        num_train_epochs=EPOCHS_NUMBER,
        per_device_eval_batch_size=BATCH_SIZE,
        predict_with_generate=True,
        evaluation_strategy="epoch",
        do_train=True,
        do_eval=True,
        logging_steps=500,
        save_strategy="epoch",
        overwrite_output_dir=True,
        save_total_limit=3,
        load_best_model_at_end=True
    )

    trainer = Seq2SeqTrainer(
        model=base_model,
        args=training_args,
        compute_metrics=rouge_metrics.compute_metrics,
        train_dataset=train_data,
        eval_dataset=test_data,
    )

    trainer.evaluate()
    trainer.train()

    trainer.save_model(PATH_TO_TRAINED_MODEL)
    tokenizer.save_pretrained(PATH_TO_TRAINED_MODEL)
