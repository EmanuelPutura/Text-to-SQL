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


def load_predictions_from_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        predictions = file.read().splitlines()
    return predictions


if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s : %(name)s - %(levelname)s : %(message)s')
    logger = logging.getLogger('root')
    logger.setLevel(logging.INFO)

    predictions = load_predictions_from_file('eval/predictions/pred_model1206_firefox1.txt')
    logger.info('All predictions were stored in memory ({} predictions in total).'.format(len(predictions)))

    db_file = 'data/test.db'
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
