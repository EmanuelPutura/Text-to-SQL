import torch
import logging
import json
import re
import random

from datasets import load_dataset
from transformers import AutoTokenizer, T5ForConditionalGeneration

from lib.dbengine import DBEngine
from lib.query import Query
from lib.common import count_lines

from formatter.wikisql_formatter import encode_query_into_wikisql_sql_dict


def get_table_str_from_row_pretrained3(row_table):
  header = row_table['header']
  data_types = row_table['types']

  table_str = "Table(" + ", ".join([f"{h}: {t}" for h, t in zip(header, data_types)]) + ")"
  return table_str


def get_table_str_from_row_pretrained4_5(row_table):
    header = row_table['header']

    table_str = "Table(" + ", ".join([f"\'{h}\'" for h in header]) + ")"
    return table_str


def prepare_natural_language_query_pretrained1(query, *args):
    return query


def prepare_natural_language_query_pretrained2(query, *args):
    return 'translate to SQL: ' + query


def prepare_natural_language_query_pretrained3(query, dataset_row, *args):
    return 'translate to SQL the following natural language query: \'{}\', where the table is \'{}\''.format(query, get_table_str_from_row_pretrained3(dataset_row))


def prepare_natural_language_query_pretrained4_5(query, dataset_row, *args):
    return 'translate to SQL the following natural language query: \'{}\', where the table is \'{}\''.format(query, get_table_str_from_row_pretrained4_5(dataset_row))


def translate_to_sql(device, model, tokenizer, nat_lang_prepare_func, *args):
    inputs = tokenizer(nat_lang_prepare_func(*args), padding='longest', max_length=64, return_tensors='pt')
    input_ids = inputs.input_ids.to(device)
    attention_mask = inputs.attention_mask.to(device)
    output = model.generate(input_ids, attention_mask=attention_mask, max_length=64)

    return tokenizer.decode(output[0], skip_special_tokens=True)


def store_predictions_in_file(device, test_data, model, tokenizer, file_path='predictions/pred1.txt'):
    with open(file_path, 'w', encoding='utf-8') as file:
        index = 0

        for row in test_data:
            predicted_query = translate_to_sql(device, model, tokenizer, prepare_natural_language_query_pretrained4_5, row['question'], row['table'])
            file.write(predicted_query + '\n')

            if index % 100 == 0:
                logger.info('Storing predictions in file, row = {}'.format(index))
            index += 1


def store_predictions_in_file_from_backup(device, test_data, model, tokenizer, start_index, file_path='predictions/pred1.txt'):
    with open(file_path, 'a', encoding='utf-8') as file:
        index = start_index
        while index < len(test_data):
            row = test_data[index]

            predicted_query = translate_to_sql(device, model, tokenizer, prepare_natural_language_query_pretrained4_5, row['question'], row['table'])
            file.write(predicted_query + '\n')

            if index % 100 == 0:
                logger.info('Storing predictions in file, row = {}'.format(index))
            index += 1


def load_predictions_from_file(file_path='predictions/pred1.txt'):
    with open(file_path, 'r', encoding='utf-8') as file:
        predictions = file.read().splitlines()
    return predictions


if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s : %(name)s - %(levelname)s : %(message)s')
    logger = logging.getLogger('root')
    logger.setLevel(logging.INFO)

    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    logger.info('Running on \'%s\' device', device)

    # load the pretrained model
    PATH_TO_TRAINED_MODEL = "../pretrained/pretrained4"

    tokenizer = AutoTokenizer.from_pretrained(PATH_TO_TRAINED_MODEL)
    model = T5ForConditionalGeneration.from_pretrained(PATH_TO_TRAINED_MODEL)
    model.to(device)

    test_data = load_dataset('wikisql', split='test')

    # store_predictions_in_file(device, test_data, model, tokenizer, 'predictions/pred_pretrained5.txt')
    # store_predictions_in_file_from_backup(device, test_data, model, tokenizer, 8184)
    predictions = load_predictions_from_file('predictions/pred_pretrained5.txt')
    logger.info('All predictions were stored in memory ({} predictions in total).'.format(len(predictions)))

    db_file = '../data/test.db'
    engine = DBEngine(db_file)

    grades = []
    exact_match = []
    ordered = False

    row_no = 0
    wrong_ex_no = 0
    wrong_match_no = 0
    exceptions = 0

    for row in test_data:
        row_no += 1

        if row_no % 100 == 0:
            print('Row no.: {}, Wrong ex. no.: {}, Wrong match no.: {}, Exceptions so far: {}'.format(row_no, wrong_ex_no, wrong_match_no, exceptions))
            print('Ex_accuracy: {}, Lf_accuracy: {}'.format(sum(grades) / len(grades), sum(exact_match) / len(exact_match)))
            print('Full_ex_accuracy: {}, Full_lf_accuracy: {}\n'.format((sum(grades)) / (len(grades) + exceptions), (sum(exact_match)) / (len(exact_match) + exceptions)))

        # eliminate special char from where conditions
        row['sql']['conds']['condition'] = [cond.replace('\u2009', ' ') for cond in row['sql']['conds']['condition']]
        human_readable = row['sql'].pop('human_readable')

        column_idx_lst = row['sql']['conds']['column_index']
        operator_idx_lst = row['sql']['conds']['operator_index']
        condition_lst = row['sql']['conds']['condition']

        wikisql_conds_dict = []
        for i in range(len(column_idx_lst)):
            wikisql_conds_dict.append([column_idx_lst[i], operator_idx_lst[i], condition_lst[i]])

        row['sql']['conds'] = wikisql_conds_dict

        table_id = row['table']['id']
        if not table_id.startswith('table'):
            table_id = 'table_{}'.format(table_id.replace('-', '_'))

        correct_result_repr = Query.from_dict(row['sql'], ordered=ordered)
        correct_result = engine.execute_query(table_id, correct_result_repr, lower=True)

        # predicted_query = human_readable
        # predicted_query = translate_to_sql(device, model, tokenizer, prepare_natural_language_query_pretrained4_5, row['question'], row['table'])
        predicted_query = predictions[row_no - 1]

        try:
            predicted_wikisql_format = encode_query_into_wikisql_sql_dict(predicted_query, row['table']['header'])
        except Exception as e:
            exceptions += 1
            continue

        predicted_wikisql_format.pop('human_readable')

        predicted_column_idx_lst = predicted_wikisql_format['conds']['column_index']
        predicted_operator_idx_lst = predicted_wikisql_format['conds']['operator_index']
        predicted_condition_lst = predicted_wikisql_format['conds']['condition']

        wikisql_predicted_conds_dict = []
        for i in range(len(predicted_column_idx_lst)):
            wikisql_predicted_conds_dict.append([predicted_column_idx_lst[i], predicted_operator_idx_lst[i], predicted_condition_lst[i]])

        predicted_wikisql_format['conds'] = wikisql_predicted_conds_dict

        predicted_repr = Query.from_dict(predicted_wikisql_format, ordered=ordered)
        predicted_result = engine.execute_query(table_id, predicted_repr, lower=True)

        correct = correct_result == predicted_result
        match = human_readable.lower() == predicted_query.lower()

        if not correct:
            wrong_ex_no += 1
        if not match:
            wrong_match_no += 1

        grades.append(correct)
        exact_match.append(match)

    print('\n----- FINAL METRICS -----')
    print('Row no.: {}, Wrong ex. no.: {}, Wrong match no.: {}, Exceptions so far: {}'.format(row_no, wrong_ex_no, wrong_match_no, exceptions))
    print('Ex_accuracy: {}, Lf_accuracy: {}'.format(sum(grades) / len(grades), sum(exact_match) / len(exact_match)))
    print('Full_ex_accuracy: {}, Full_lf_accuracy: {}\n'.format((sum(grades)) / (len(grades) + exceptions), (sum(exact_match)) / (len(exact_match) + exceptions)))
