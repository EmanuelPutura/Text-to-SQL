from abc import ABCMeta, abstractmethod


class PretrainedModel(metaclass=ABCMeta):
    @classmethod
    @abstractmethod
    def format_natural_language_query(cls, query, column_data_dict):
        pass

    @staticmethod
    @abstractmethod
    def get_table_str(column_data_dict):
        pass

    @classmethod
    def translate_to_sql(cls, model, tokenizer, query, column_data_dict, device='cpu'):
        inputs = tokenizer(cls.format_natural_language_query(query, column_data_dict), padding='longest', max_length=64, return_tensors='pt')
        input_ids = inputs.input_ids.to(device)
        attention_mask = inputs.attention_mask.to(device)
        output = model.generate(input_ids, attention_mask=attention_mask, max_length=64)

        return tokenizer.decode(output[0], skip_special_tokens=True)


class PretrainedModel1(PretrainedModel):
    @staticmethod
    def get_table_str(column_data_dict):
        pass

    @classmethod
    def format_natural_language_query(cls, query, column_data_dict):
        return 'translate to SQL: {}'.format(query)


class PretrainedModel5(PretrainedModel):
    @staticmethod
    def get_table_str(column_data_dict):
        header = column_data_dict['column_names']

        table_str = "Table(" + ", ".join([f"\'{h}\'" for h in header]) + ")"
        return table_str

    @classmethod
    def format_natural_language_query(cls, query, column_data_dict):
        return 'translate to SQL the following natural language query: \'{}\', where the table is \'{}\''.format(query, cls.get_table_str(column_data_dict))
