import json
from collections import Counter
import argparse
import requests


def fetch_json(mode, subreddit=None):

    if mode == 'local':
        with open("sample_data.json", "r") as file:
            return json.load(file)
    elif mode == 'http':
        if subreddit is None:
            raise ValueError("Subreddit must be provided for HTTP mode")

        url = f'https://reddit.com/user/{subreddit}.json'

        # Fetch the JSON from the URL
        response = requests.get(url)

        # Check for any errors in the HTTP response
        response.raise_for_status()  # Raises an error for bad status codes (e.g., 404, 500)

        # Return the parsed JSON content
        return response.json()


# Function to extract 'subreddit_name_prefixed' from the JSON data
def get_subreddit_counts(json_data):
    subreddit_names = []

    # Iterate over the 'children' elements in the JSON
    for child in json_data['data']['children']:
        subreddit_names.append(child['data']['subreddit_name_prefixed'])

    # Count occurrences using Counter
    return Counter(subreddit_names)


# Function to sort counts by frequency and alphabetically
def sort_subreddit_counts(subreddit_counts):
    return sorted(subreddit_counts.items(), key=lambda x: (-x[1], x[0]))


# Function to parse command-line arguments
def parse_args():
    parser = argparse.ArgumentParser(description="Count and sort subreddit names in a JSON file.")
    parser.add_argument('-mode', required=False, choices=['file', 'http'], default='file')
    parser.add_argument('-sr', '--subreddit', help="", required=False)
    parser.add_argument('-l', '--limit', help=".", required=False)
    parser.add_argument('-s', '--sort', help="", required=False, choices=['hot', 'new', 'top'], default='hot')
    parser.add_argument('-so', '--sort-options', help="", required=False, choices=['hour', 'day', 'week', 'month', 'year', 'all'])
    args = parser.parse_args()

    if args.sort == 'top' and not args.sort_options:
        parser.error("The --sort-options argument is required when --sort is set to 'top'.")

    return args


# Function to print the sorted counts as a bar chart
def print_bar_chart(sorted_subreddit_counts):
    max_label_length = max(len(subreddit) for subreddit, _ in sorted_subreddit_counts)
    max_count = max(count for _, count in sorted_subreddit_counts)

    for subreddit, count in sorted_subreddit_counts:
        # Normalize the bar size to fit within 50 characters
        bar = '█' * int((count / max_count) * 50)
        print(f"{subreddit.ljust(max_label_length)} | {bar} {count}")


# Execute
def main():
    # Parse command-line arguments
    args = parse_args()

    print(f'Mode: {args.mode}')
    print(f'Subreddit Name: {args.subreddit}')

    if args.subreddit:
        # Load the JSON data
        json_data = fetch_json(args.mode, subreddit=args.subreddit)

    # Get subreddit counts (with optional custom subreddit value)
    subreddit_counts = get_subreddit_counts(json_data)

    # Sort the counts
    sorted_subreddit_counts = sort_subreddit_counts(subreddit_counts)

    # # Print the sorted counts
    # for subreddit, count in sorted_subreddit_counts:
    #     print(f'{subreddit}: {count}')

    # print("\n")

    # Print the sorted counts as a bar chart
    print_bar_chart(sorted_subreddit_counts)


if __name__ == "__main__":
    main()
