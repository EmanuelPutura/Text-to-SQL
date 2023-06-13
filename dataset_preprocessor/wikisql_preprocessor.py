from datasets import load_dataset
from transformers import AutoTokenizer


class WikiSQLPreprocessor:
    def __init__(self, model_inputs_class, tokenizer):
        self.__model_inputs_class = model_inputs_class
        self.__tokenizer = tokenizer

        self.__train_data = load_dataset('wikisql', split='train+validation')
        self.__test_data = load_dataset('wikisql', split='test')

        self.__train_data = self.__train_data.map(self.__format_dataset, remove_columns=self.__train_data.column_names)
        self.__test_data = self.__test_data.map(self.__format_dataset, remove_columns=self.__test_data.column_names)

        self.__train_data = self.__train_data.map(self.__convert_to_features, batched=True, remove_columns=self.__train_data.column_names)
        self.__test_data = self.__test_data.map(self.__convert_to_features, batched=True, remove_columns=self.__test_data.column_names)

        columns = ['input_ids', 'attention_mask', 'labels', 'decoder_attention_mask']

        self.__train_data.set_format(type='torch', columns=columns)
        self.__test_data.set_format(type='torch', columns=columns)

    def train_data(self):
        return self.__train_data

    def test_data(self):
        return self.__test_data

    def __get_column_data_dict(self, row):
        return {'table_name': row['table']['name'], 'column_names': row['table']['header'], 'column_types': row['table']['types']}

    def __format_dataset(self, row):
        dataset_input = self.__model_inputs_class.format_natural_language_query(row['question'], self.__get_column_data_dict(row))
        return {'input': dataset_input, 'target': row['sql']['human_readable']}

    def __convert_to_features(self, row):
        input_encodings = self.__tokenizer.batch_encode_plus(row['input'], padding='max_length', truncation=True, max_length=64)
        target_encodings = self.__tokenizer.batch_encode_plus(row['target'], padding='max_length', truncation=True, max_length=64)

        encodings = {
            'input_ids': input_encodings['input_ids'],
            'attention_mask': input_encodings['attention_mask'],
            'labels': target_encodings['input_ids'],
            'decoder_attention_mask': target_encodings['attention_mask']
        }

        return encodings
