import unittest
from unittest.mock import patch, mock_open, MagicMock
import argparse
from collections import Counter
import json
import requests

from finder import fetch_json, get_subreddit_counts, sort_subreddit_counts, parse_args, print_bar_chart

class TestFunctions(unittest.TestCase):

    @patch('builtins.open', new_callable=mock_open, read_data='{"data": {"children": [{"data": {"subreddit_name_prefixed": "r/test"}}]}}')
    def test_fetch_json_local(self, mock_file):
        # Test fetch_json in 'local' mode
        result = fetch_json('local')
        self.assertEqual(result['data']['children'][0]['data']['subreddit_name_prefixed'], 'r/test')
        mock_file.assert_called_with('sample_data.json', 'r')

    @patch('requests.get')
    def test_fetch_json_http(self, mock_get):
        # Mock the HTTP response
        mock_response = MagicMock()
        mock_response.json.return_value = {'data': {'children': [{'data': {'subreddit_name_prefixed': 'r/test'}}]}}
        mock_get.return_value = mock_response

        result = fetch_json('http', subreddit='test')
        self.assertEqual(result['data']['children'][0]['data']['subreddit_name_prefixed'], 'r/test')
        mock_get.assert_called_with('https://reddit.com/user/test.json')

    def test_fetch_json_http_no_subreddit(self):
        # Test fetch_json in 'http' mode without a subreddit
        with self.assertRaises(ValueError):
            fetch_json('http')

    def test_get_subreddit_counts(self):
        # Test get_subreddit_counts with sample data
        json_data = {
            'data': {
                'children': [
                    {'data': {'subreddit_name_prefixed': 'r/test1'}},
                    {'data': {'subreddit_name_prefixed': 'r/test2'}},
                    {'data': {'subreddit_name_prefixed': 'r/test1'}},
                ]
            }
        }
        result = get_subreddit_counts(json_data)
        self.assertEqual(result, Counter({'r/test1': 2, 'r/test2': 1}))

    def test_sort_subreddit_counts(self):
        # Test sort_subreddit_counts with unsorted data
        counts = Counter({'r/b': 2, 'r/a': 2, 'r/c': 1})
        result = sort_subreddit_counts(counts)
        expected = [('r/a', 2), ('r/b', 2), ('r/c', 1)]
        self.assertEqual(result, expected)

    @patch('argparse.ArgumentParser.parse_args', return_value=argparse.Namespace(sort='top', sort_options='day', mode='http', subreddit='test', limit=None))
    def test_parse_args_top_with_sort_options(self, mock_args):
        # Test parse_args when sort is 'top' and sort-options are provided
        args = parse_args()
        self.assertEqual(args.sort, 'top')
        self.assertEqual(args.sort_options, 'day')

    @patch('argparse.ArgumentParser.parse_args', return_value=argparse.Namespace(sort='top', sort_options=None, mode='http', subreddit='test', limit=None))
    def test_parse_args_top_without_sort_options(self, mock_args):
        # Test parse_args when sort is 'top' but sort-options are missing
        with self.assertRaises(SystemExit):
            parse_args()

    @patch('sys.stdout', new_callable=unittest.mock.MagicMock)
    def test_print_bar_chart(self, mock_stdout):
        # Test printing bar chart
        sorted_subreddit_counts = [('r/test1', 2), ('r/test2', 1)]
        print_bar_chart(sorted_subreddit_counts)
        mock_stdout.write.assert_called()

if __name__ == '__main__':
    unittest.main()
