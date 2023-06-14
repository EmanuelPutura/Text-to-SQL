import torch
import logging
import json
import re
import random
import argparse

from datasets import load_dataset

from lib.dbengine import DBEngine
from lib.query import Query
from lib.common import count_lines

from formatter.wikisql_formatter import WikiSQLFormatter


def load_predictions_from_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        predictions = file.read().splitlines()
    return predictions


if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s : %(name)s - %(levelname)s : %(message)s')
    logger = logging.getLogger('root')
    logger.setLevel(logging.INFO)

    parser = argparse.ArgumentParser(
        prog='Text-to-SQL',
        description='WikiSQL evaluation script',
    )

    parser.add_argument('--predictions-path', type=str, required=True, help='Specify the location of the model predictions')
    args = parser.parse_args()

    predictions_path = args.predictions_path
    test_data = load_dataset('wikisql', split='test')

    predictions = load_predictions_from_file(predictions_path)
    logger.info('All predictions were stored in memory ({} predictions in total).'.format(len(predictions)))

    db_file = 'data/test.db'
    engine = DBEngine(db_file)

    grades = []
    exact_match = []
    ordered = False

    row_no = 0
    wrong_ex_no = 0
    wrong_match_no = 0
    all_exceptions = 0
    invalid_column_exceptions = 0

    for row in test_data:
        row_no += 1

        if row_no % 100 == 0:
            print('Row no.: {}, Wrong ex. no.: {}, Wrong match no.: {}, Invalid column exceptions: {}, All exceptions: {}'.format(row_no, wrong_ex_no, wrong_match_no, invalid_column_exceptions, all_exceptions))
            print('Ex_accuracy: {}, Lf_accuracy: {}'.format(sum(grades) / len(grades), sum(exact_match) / len(exact_match)))
            print('Full_ex_accuracy: {}, Full_lf_accuracy: {}\n'.format((sum(grades)) / (len(grades) + all_exceptions), (sum(exact_match)) / (len(exact_match) + all_exceptions)))

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
            predicted_wikisql_format = WikiSQLFormatter.encode_query_into_wikisql_sql_dict(predicted_query, row['table']['header'])
        except Exception as e:
            if str(e) == 'Invalid SQL human readable query.':
                invalid_column_exceptions += 1

            all_exceptions += 1
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
    print('Row no.: {}, Wrong ex. no.: {}, Wrong match no.: {}, Invalid column exceptions: {}, All exceptions: {}'.format(row_no, wrong_ex_no, wrong_match_no, invalid_column_exceptions, all_exceptions))
    print('Ex_accuracy: {}, Lf_accuracy: {}'.format(sum(grades) / len(grades), sum(exact_match) / len(exact_match)))
    print('Full_ex_accuracy: {}, Full_lf_accuracy: {}\n'.format((sum(grades)) / (len(grades) + all_exceptions), (sum(exact_match)) / (len(exact_match) + all_exceptions)))
