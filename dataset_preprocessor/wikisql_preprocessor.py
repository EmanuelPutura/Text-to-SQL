from datasets import load_dataset
from transformers import AutoTokenizer


class WikiSQLPreprocessor:
    def __init__(self, tokenizer):
        self.__tokenizer = tokenizer

        self.__train_data = load_dataset('wikisql', split='train+validation')
        self.__test_data = load_dataset('wikisql', split='test')

        self.__train_data = self.__train_data.map(self.__class__.__format_dataset, remove_columns=self.__train_data.column_names)
        self.__test_data = self.__test_data.map(self.__class__.__format_dataset, remove_columns=self.__test_data.column_names)

        self.__train_data = self.__train_data.map(self.__convert_to_features, batched=True, remove_columns=self.__train_data.column_names)
        self.__test_data = self.__test_data.map(self.__convert_to_features, batched=True, remove_columns=self.__test_data.column_names)

        columns = ['input_ids', 'attention_mask', 'labels', 'decoder_attention_mask']

        self.__train_data.set_format(type='torch', columns=columns)
        self.__test_data.set_format(type='torch', columns=columns)

    def train_data(self):
        return self.__train_data

    def test_data(self):
        return self.__test_data

    @staticmethod
    def __format_dataset(row):
        return {'input': 'translate to SQL: ' + row['question'], 'target': row['sql']['human_readable']}

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


class WikiSQLPreprocessorWithDatabaseSchema(WikiSQLPreprocessor):
    def __init__(self, tokenizer):
        super().__init__(tokenizer)

    @staticmethod
    def get_table_from_row(row):
        header = row['table']['header']
        data_types = row['table']['types']

        table_str = "Table(" + ", ".join([f"{h}: {t}" for h, t in zip(header, data_types)]) + ")"
        return table_str

    @staticmethod
    def __format_dataset(row):
        table_str = get_table_from_row(row)
        return {'input': table_str + ', translate to SQL: ' + row['question'], 'target': row['sql']['human_readable']}
