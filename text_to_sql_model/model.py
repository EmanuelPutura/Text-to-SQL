import torch
import logging

from transformers import AutoTokenizer, T5ForConditionalGeneration
from transformers import Seq2SeqTrainer
from transformers import Seq2SeqTrainingArguments
from transformers import get_linear_schedule_with_warmup

from dataset_preprocessor.wikisql_preprocessor import WikiSQLPreprocessor
from eval.rouge_metrics import RougeMetrics


class TextToSQLModel:
    EPOCHS_NUMBER = 15
    BATCH_SIZE = 16

    def __init__(self, base_model_name, model_inputs_class, pretrained_path, device):
        self.__model_inputs_class = model_inputs_class
        self.__pretrained_path = pretrained_path
        self.__device = device

        self.__tokenizer = AutoTokenizer.from_pretrained(base_model_name, model_max_length=1024)
        self.__rouge_metrics = RougeMetrics(self.__tokenizer)
        self.__base_model = T5ForConditionalGeneration.from_pretrained(base_model_name)
        self.__base_model.to(self.__device)

        self.__wikisql_preprocessor = WikiSQLPreprocessor(model_inputs_class, self.__tokenizer)
        self.__train_data = self.__wikisql_preprocessor.train_data()
        self.__test_data = self.__wikisql_preprocessor.test_data()

        self.__logger = logging.getLogger('root')

    def train(self, save_model=True):
        training_args = Seq2SeqTrainingArguments(
            output_dir=self.__pretrained_path,
            per_device_train_batch_size=self.BATCH_SIZE,
            num_train_epochs=self.EPOCHS_NUMBER,
            per_device_eval_batch_size=self.BATCH_SIZE,
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
            model=self.__base_model,
            args=training_args,
            compute_metrics=self.__rouge_metrics.compute_metrics,
            train_dataset=self.__train_data,
            eval_dataset=self.__test_data,
        )

        trainer.evaluate()
        self.__logger.info('Evaluating the trainer finished successfully.')

        trainer.train()
        self.__logger.info('Training the text-to-SQL model finished successfully.')

        if save_model:
            self.__save_model(trainer)

    def __save_model(self, trainer):
        trainer.save_model(self.__pretrained_path)
        self.__tokenizer.save_pretrained(self.__pretrained_path)
        self.__logger.info('The text-to-SQL model has been successfully saved at path \'{}\'.'.format(self.__pretrained_path))
