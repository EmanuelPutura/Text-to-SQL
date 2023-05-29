import unittest
from formatter.wikisql_formatter import sql_get_select_and_agg_index, sql_get_all_where_conditions, sql_get_encoded_where_conditions


class TestWikiSQLFormatter(unittest.TestCase):
    def test_sql_get_select_and_agg_index(self):
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

    def test_sql_get_all_where_conditions(self):
        sql_query1 = 'SELECT Column1 FROM table WHERE Column0 > 2'
        assert sql_get_all_where_conditions(sql_query1) == ['Column0 > 2']

        sql_query2 = 'SELECT Column2 FROM table WHERE Column0 > 2 AND Column1 < 5'
        assert sql_get_all_where_conditions(sql_query2) == ['Column0 > 2', 'Column1 < 5']

        sql_query3 = 'SELECT Column1 FROM table WHERE Column0 > 2 AND Column1 < 5 OR Column2 = \'Alexander\' AND Column4 = 2'
        assert sql_get_all_where_conditions(sql_query3) == ['Column0 > 2', 'Column1 < 5', 'Column2 = \'Alexander\'',
                                                            'Column4 = 2']

        sql_query4 = 'SELECT Column1 FROM table'
        assert sql_get_all_where_conditions(sql_query4) == []

    def test_sql_get_encoded_where_conditions(self):
        sql_query1 = 'SELECT Column1 FROM table WHERE Column0 > 2'
        assert sql_get_encoded_where_conditions(sql_query1, ['Column0', 'Column1', 'Column2']) == {'column_index': [0],
                                                                                                   'operator_index': [
                                                                                                       1],
                                                                                                   'condition': ['2']}

        sql_query2 = 'SELECT Column2 FROM table WHERE Column0 > 2 AND Column1 < 5'
        assert sql_get_encoded_where_conditions(sql_query2, ['Column0', 'Column1', 'Column2']) == {
            'column_index': [0, 1], 'operator_index': [1, 2], 'condition': ['2', '5']}

        sql_query3 = 'SELECT Column1 FROM table WHERE Column0 > 2 AND Column4 = 2 AND Column1 < 5 OR Column2 = \'Alexander\''
        assert sql_get_encoded_where_conditions(sql_query3, ['Column0', 'Column1', 'Column2', 'Column3', 'Column4']) == \
               {'column_index': [0, 4, 1, 2], 'operator_index': [1, 0, 2, 0],
                'condition': ['2', '2', '5', '\'Alexander\'']}

        sql_query4 = 'SELECT Column1 FROM table'
        assert sql_get_encoded_where_conditions(sql_query4, ['Column0', 'Column1']) == {'column_index': [],
                                                                                        'operator_index': [],
                                                                                        'condition': []}
