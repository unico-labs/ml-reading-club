from collections import Counter
import os
from typing import List, Tuple, Set

import argparse
import bs4
import requests


# CLI Argument Parsing
def get_args() -> dict:
    view_choices = [
        'winners', 'voters', 'clear']
    default_view = 'voters'

    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--view', default=default_view, choices=view_choices,
        help=("Selects how election votes must be seen. "
              f"Must be one of {view_choices}. "
              f"Defaults to {default_view}."))
    parser.add_argument(
        '--vote-body', default='THIS')
    parser.add_argument(
        '--users', type=str, nargs='+',
        help=("Non-empty list of user names to be considered "
              "when iterating over votes"))
    parser.add_argument(
        '--issues', type=str, nargs='+',
        help=("Non-empty list of issues IDs to be considered "
              "when iterating over votes"))
    parser.add_argument(
        '--max-user-votes', default=3,
        help="How many papers can an user vote for by election.")
    parser.add_argument(
        '--organization', default='unico-labs')
    parser.add_argument(
        '--repository', default='ml-reading-club')
    parser.add_argument(
        '--token-env-variable', default='GITHUB_ACCESS_TOKEN')
    parser.add_argument(
        '--api-url', default='https://api.github.com')
    parser.add_argument(
        '--github-url', default='https://github.com')

    return vars(parser.parse_args())
ARGS = get_args()  # noqa: E305


# API Authorization
def get_authorization_headers() -> dict:
    token_var_name = ARGS['token_env_variable']
    try:
        token = os.environ[token_var_name]
    except KeyError:
        raise NameError((
            f'{token_var_name} environment variable not set. '
            'Get your token @ https://github.com/settings/tokens. '
            'Also, assert the token has full control over repositories, '
            'and it is configured via SSO to '
            f'access the target organization {ARGS["organization"]}'))
    else:
        return {'Authorization': f'token {token}'}


# API Requests
def request_repo_comments() -> List[dict]:
    url = (f'{ARGS["api_url"]}/repos/{ARGS["organization"]}'
           f'/{ARGS["repository"]}/issues/comments')

    response = requests.get(url, headers=get_authorization_headers())
    response.raise_for_status()

    return response.json()


def request_collaborators() -> List[dict]:
    url = (f'{ARGS["api_url"]}/repos/{ARGS["organization"]}'
           f'/{ARGS["repository"]}/collaborators')
    response = requests.get(url, headers=get_authorization_headers())
    response.raise_for_status()
    return response.json()


def request_vote_delete(vote: dict) -> None:
    requests.delete(
        vote['url'],
        headers=get_authorization_headers()
    ).raise_for_status()


# Requests Formatting
def format_comment(comment: dict) -> dict:
    return {
        'id': comment['id'],
        'user': comment['user']['login'],
        'body': comment['body'],
        'url': comment['url'],
        'issue': comment['issue_url'].split('/')[-1],
    }


# Controller functions
def get_comments() -> List[dict]:
    return list(map(format_comment, request_repo_comments()))


def get_votes(comments: List[dict]) -> List[dict]:
    votes = list(filter(lambda comment: comment['body'] == 'THIS', comments))
    if ARGS['users']:
        votes = list(filter(
            lambda vote: vote['user'] in ARGS['users'], votes))
    if ARGS['issues']:
        votes = list(filter(
            lambda vote: vote['issue'] in ARGS['issues'], votes))
    return votes


def get_collaborators(comments: List[dict]) -> Set[str]:
    return set(map(lambda user: user['login'], request_collaborators()))


def get_absent_voters(votes: List[dict], active_users: List[str]) -> Set[str]:
    return active_users.difference(
        set(map(lambda vote: vote['user'], votes)))


def delete_votes(votes: List[dict]) -> None:
    for vote in votes:
        request_vote_delete(vote)


def count_votes_on_issues(
    votes: List[dict]
) -> List[Tuple]:
    return Counter([vote['issue'] for vote in votes]).most_common(10)


def count_votes_by_users(
    votes: List[dict],
    sorted: bool = False
) -> List[Tuple]:
    count_list = list(Counter([vote['user'] for vote in votes]).items())
    if sorted:
        count_list.sort(key=lambda user, count: count, reverse=True)
    return count_list


# Output Formatting
def stringify_names(
    names: List[str],
    sep: str = ', '
) -> str:
    if len(names) == 1:
        return str(names[0])
    else:
        return sep.join(names[:-1]) + f'and {names[-1]}'


def stringify_winner(
    issue_id: str,
    vote_count: int,
    voters: List[str] = None
) -> str:
    issue_url = (f'https://github.com/{ARGS["organization"]}'
                 f'/{ARGS["repository"]}/issues/{issue_id}')

    response = requests.get(issue_url, headers=get_authorization_headers())
    response.raise_for_status()

    html = bs4.BeautifulSoup(response.text, features='lxml')
    issue_title = html.find('main').find('span', class_='js-issue-title').text

    short_result = (f'{issue_title} (#{issue_id}) has received '
                    f'{vote_count} votes. ({issue_url})')
    if voters:
        return (f'{short_result}\n\t'
                f'Voters are {stringify_names(voters)}.')
    else:
        return short_result


def stringify_voter_count(voter_id: str, vote_count: int) -> str:
    plurals = "s" if vote_count > 1 else ""
    return f'{voter_id} voted on {vote_count} paper{plurals}'


def stringify_under_voter(voter_id: str, vote_count: int) -> str:
    plurals_count = "s" if vote_count > 1 else ""
    votes_diff = ARGS["max_user_votes"] - vote_count
    plurals_diff = "s" if votes_diff > 1 else ""
    return (
        f'{voter_id} voted on {vote_count} paper{plurals_count} only '
        f'(is eligible for {votes_diff} more vote{plurals_diff})')


def stringify_over_voter(voter_id: str, vote_count: int) -> str:
    plurals_count = "s" if vote_count > 1 else ""
    votes_diff = vote_count - ARGS["max_user_votes"]
    plurals_diff = "s" if votes_diff > 1 else ""
    return (
        f'{voter_id} votes on {vote_count} paper{plurals_count} '
        f'({votes_diff} vote{plurals_diff} could be removed)')


# View Functions
def winners_view(votes: List[dict]) -> None:
    for issue_id, vote_count in count_votes_on_issues(votes):
        print(stringify_winner(issue_id, vote_count))


def voters_view(
    votes: List[dict],
    comments: List[dict]
) -> None:
    for user_id, vote_count in count_votes_by_users(votes):
        if vote_count > ARGS['max_user_votes']:
            print(stringify_over_voter(user_id, vote_count))
        elif vote_count == ARGS['max_user_votes']:
            print(stringify_voter_count(user_id, vote_count))
        elif vote_count < ARGS['max_user_votes']:
            print(stringify_under_voter(user_id, vote_count))

    active_users = get_collaborators(comments)
    absent_voters = get_absent_voters(votes, active_users)
    if len(absent_voters) == 0:
        print("All active users voted the present election.")
    else:
        print(absent_voters)
        verb = "has" if len(absent_voters) == 1 else "have"
        print(f'Also, {stringify_names(list(absent_voters))} '
              f'{verb} not voted yet.')


def delete_view(votes: List[dict]) -> None:
    if ARGS['issues']:
        votes_str = stringify_names(ARGS['issues'])
    else:
        votes_str = 'all votes'

    if ARGS['users']:
        users_str = stringify_names(ARGS['users'])
    else:
        users_str = 'all users'

    if 'y' == input(
            ('Deleting votes cannot be undone! '
             'Are you sure you want to delete '
             f'{votes_str} for {users_str}? (y)')).lower():
        delete_votes(votes)


if __name__ == '__main__':
    comments = get_comments()
    votes = get_votes(comments)

    if len(votes) == 0:
        print("There are no votes at the moment.")
    elif ARGS['view'] == 'winners':
        winners_view(votes)
    elif ARGS['view'] == 'voters':
        voters_view(votes, comments)
    elif ARGS['view'] == 'clear':
        delete_view(votes)
