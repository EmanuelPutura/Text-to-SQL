import torch
import logging
import re

from datasets import load_dataset


AGGREGATORS = ['MAX', 'MIN', 'COUNT', 'SUM', 'AVG']
COND_OPS = ['=', '>', '<']


# Query manipulation methods
def sql_get_between_select_and_from(query):
    start_index = query.upper().find('SELECT') + len('SELECT')
    end_index = query.upper().find('FROM TABLE')

    if start_index < 0 or end_index < 0 or start_index >= end_index:
        raise Exception('Invalid SQL human readable query.')

    return query[start_index:end_index].strip()


def sql_get_select_and_agg_index(query, columns):
    select_agg_str = sql_get_between_select_and_from(query)

    agg_index = 0
    column_name = ''

    for aggregator in AGGREGATORS:
        if select_agg_str.startswith(aggregator):
            agg_index = AGGREGATORS.index(aggregator) + 1

            column_name = select_agg_str[len(aggregator):].strip()
            if column_name[0] == '(' and column_name[-1] == ')' and column_name not in columns:
                column_name = column_name[1:-1]

            break

    if not agg_index:
        column_name = select_agg_str

    if column_name not in columns:
        raise Exception('Invalid SQL human readable query.')

    sel_index = columns.index(column_name)
    return [sel_index, agg_index]


def sql_get_all_where_conditions(query):
    start_index_after_where = query.find('WHERE') + len('WHERE')

    if start_index_after_where < 0:
        raise Exception('Invalid SQL human readable query.')
    elif start_index_after_where == len('WHERE') - 1:
        return []

    str_after_where = query[start_index_after_where:].strip()

    and_or_separators = r'\bAND\b|\bOR\b'
    raw_result = re.split(and_or_separators, str_after_where)
    return [r.strip() for r in raw_result if r.strip()]


def sql_get_encoded_where_conditions(query, columns):
    conds = {'column_index': [], 'operator_index': [], 'condition': []}
    all_where_conditions = sql_get_all_where_conditions(query)

    for condition in all_where_conditions:
        cond_separators = r'\s*( < | > | = )\s*'
        split_conditions = re.split(cond_separators, condition, maxsplit=1)
        split_conditions = [c.strip() for c in split_conditions if c.strip()]

        if len(split_conditions) != 3:
            raise Exception('Invalid SQL human readable query.')

        [column, operator, condition_arg] = split_conditions

        if column not in columns:
            raise Exception('Invalid SQL human readable query.')
        column_idx = columns.index(column)

        if operator not in COND_OPS:
            raise Exception('Invalid SQL human readable query.')
        operator_idx = COND_OPS.index(operator)

        conds['column_index'].append(column_idx)
        conds['operator_index'].append(operator_idx)
        conds['condition'].append(condition_arg)

    return conds


def encode_query_into_wikisql_sql_dict(query, table_header):
    result = {'human_readable': query}

    sql_agg_index = sql_get_select_and_agg_index(query, table_header)
    result['sel'] = sql_agg_index[0]
    result['agg'] = sql_agg_index[1]

    encoded_where_conditions = sql_get_encoded_where_conditions(query, table_header)
    result['conds'] = encoded_where_conditions

    return result


# Unit testing for the query manipulation methods
def test_sql_get_select_and_agg_index():
    sql_query1 = 'SELECT Column FROM table'
    assert sql_get_select_and_agg_index(sql_query1, ['Column']) == [0, 0]

    sql_query2 = 'SELECT Column2 FROM table'
    assert sql_get_select_and_agg_index(sql_query2, ['Column0', 'Column1', 'Column2']) == [2, 0]

    sql_query3 = 'SELECT Column1 FROM table'
    assert sql_get_select_and_agg_index(sql_query3, ['Column0', 'Column1', 'Column2']) == [1, 0]

    sql_query4 = 'SELECT COUNT(Column1) FROM table'
    assert sql_get_select_and_agg_index(sql_query4, ['Column0', 'Column1', 'Column2']) == [1, 3]

    sql_query5 = 'SELECT COUNT Column1 FROM table'
    assert sql_get_select_and_agg_index(sql_query5, ['Column0', 'Column1', 'Column2']) == [1, 3]

    sql_query6 = 'SELECT MIN (Column1) FROM table'
    assert sql_get_select_and_agg_index(sql_query6, ['Column0', 'Column1', 'Column2']) == [1, 2]


def test_sql_get_all_where_conditions():
    sql_query1 = 'SELECT Column1 FROM table WHERE Column0 > 2'
    assert sql_get_all_where_conditions(sql_query1) == ['Column0 > 2']

    sql_query2 = 'SELECT Column2 FROM table WHERE Column0 > 2 AND Column1 < 5'
    assert sql_get_all_where_conditions(sql_query2) == ['Column0 > 2', 'Column1 < 5']

    sql_query3 = 'SELECT Column1 FROM table WHERE Column0 > 2 AND Column1 < 5 OR Column2 = \'Alexander\' AND Column4 = 2'
    assert sql_get_all_where_conditions(sql_query3) == ['Column0 > 2', 'Column1 < 5', 'Column2 = \'Alexander\'', 'Column4 = 2']

    sql_query4 = 'SELECT Column1 FROM table'
    assert sql_get_all_where_conditions(sql_query4) == []


def test_sql_get_encoded_where_conditions():
    sql_query1 = 'SELECT Column1 FROM table WHERE Column0 > 2'
    assert sql_get_encoded_where_conditions(sql_query1, ['Column0', 'Column1', 'Column2']) == {'column_index': [0], 'operator_index': [1], 'condition': ['2']}

    sql_query2 = 'SELECT Column2 FROM table WHERE Column0 > 2 AND Column1 < 5'
    assert sql_get_encoded_where_conditions(sql_query2, ['Column0', 'Column1', 'Column2']) == {'column_index': [0, 1], 'operator_index': [1, 2], 'condition': ['2', '5']}

    sql_query3 = 'SELECT Column1 FROM table WHERE Column0 > 2 AND Column4 = 2 AND Column1 < 5 OR Column2 = \'Alexander\''
    assert sql_get_encoded_where_conditions(sql_query3, ['Column0', 'Column1', 'Column2', 'Column3', 'Column4']) == \
           {'column_index': [0, 4, 1, 2], 'operator_index': [1, 0, 2, 0], 'condition': ['2', '2', '5', '\'Alexander\'']}

    sql_query4 = 'SELECT Column1 FROM table'
    assert sql_get_encoded_where_conditions(sql_query4, ['Column0', 'Column1']) == {'column_index': [], 'operator_index': [], 'condition': []}

    sql_query5 = 'SELECT  col3 FROM table WHERE col5 = 1.4\u2009v AND col1 = 1333\u2009mhz'
    print(sql_get_encoded_where_conditions(sql_query5, ['col0', 'col1', 'col2', 'col3', 'col4', 'col5']))


if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s : %(name)s - %(levelname)s : %(message)s')
    logger = logging.getLogger('root')
    logger.setLevel(logging.INFO)

    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    logger.info('Running on \'%s\' device', device)

    # unit tests
    test_sql_get_select_and_agg_index()
    test_sql_get_all_where_conditions()
    test_sql_get_encoded_where_conditions()
    # exit(0)

    # load test dataset split
    test_data = load_dataset('wikisql', split='test')

    index = 0
    for row in test_data:
        human_readable = row['sql']['human_readable']

        sql_agg_index = sql_get_select_and_agg_index(human_readable, row['table']['header'])
        assert sql_agg_index == [row['sql']['sel'], row['sql']['agg']]

        encoded_where_conditions = sql_get_encoded_where_conditions(human_readable, row['table']['header'])
        try:
            assert encoded_where_conditions == row['sql']['conds']
        except AssertionError as e:
            row['sql']['conds']['condition'] = [cond.replace('\u2009', ' ') for cond in row['sql']['conds']['condition']]
            assert encoded_where_conditions == row['sql']['conds']

        encoded_sql_dict = encode_query_into_wikisql_sql_dict(human_readable, row['table']['header'])
        assert encoded_sql_dict == row['sql']

        if index % 1000 == 0:
            print("Encoded SQL dict: {}".format(encoded_sql_dict))

        index += 1
