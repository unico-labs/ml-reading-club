from collections import Counter
import os

import requests


GITHUB_URL = 'https://github.com'
GITHUB_API_URL = 'https://api.github.com'
REPO = 'unico-labs/ml-reading-club'



def format_comment(comment):
    return {
        'id': comment['id'],
        'user': comment['user']['login'],
        'body': comment['body'],
        'url': comment['url'],
        'issue': comment['issue_url'].split('/')[-1],
    }


def get_authorization_headers():
    try:
        token = os.environ['GITHUB_ACCESS_TOKEN']
        return {'Authorization': f'token {token}'}
    except KeyError:
        raise NameError(("GITHUB_ACCESS_TOKEN environment variable not set."
            " Get your token @ https://github.com/settings/tokens"))


def get_votes():
    url = f'{GITHUB_API_URL}/repos/{REPO}/issues/comments'

    response = requests.get(url, headers=get_authorization_headers())
    response.raise_for_status()
    comments = response.json()

    votes = [format_comment(comment) for comment in comments if comment['body'] == 'THIS']
    return votes


def delete_votes(votes):
    for vote in votes:
        response = requests.delete(vote['url'], headers=get_authorization_headers())
        response.raise_for_status()


def print_winners(votes):
    issues_url = f'{GITHUB_URL}/{REPO}/issues'
    counts = Counter([vote['issue'] for vote in votes])
    for issue_id, vote_count in counts.most_common(10):
        print(issue_id, vote_count, f'{issues_url}/{issue_id}')


def print_voters(votes):
    counts = Counter([vote['user'] for vote in votes])
    for user, votes in counts.items():
        print(user, votes)


votes = get_votes()

print("Winners")
print_winners(votes)
print()

print("Voters")
print_voters(votes)

# Deleting votes can't be undone!
# delete_votes(votes)
