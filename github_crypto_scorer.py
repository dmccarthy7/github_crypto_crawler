import requests
from datetime import datetime, timezone
from dateutil.parser import parse as parse_date

CRYPTO_KEYWORDS = ['solidity', 'ethereum', 'web3', 'crypto', 'blockchain', 'zk', 'defi']
CRYPTO_LANGUAGES = ['Solidity', 'Rust', 'Go', 'Vyper', 'Haskell']

def fetch_user_data(username, headers):
    url = f'https://api.github.com/users/{username}'
    response = requests.get(url, headers=headers)
    print(f"Fetching {url} - Status code: {response.status_code}")
    if response.status_code != 200:
        raise Exception(f"Failed to fetch user data for {username}")
    return response.json()

def fetch_repos(username, headers):
    url = f'https://api.github.com/users/{username}/repos?per_page=100'
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        raise Exception(f"Failed to fetch repos for {username}")
    return response.json()

def calculate_recency_weight(updated_at):
    """Apply time decay: newer repos contribute more, older repos less"""
    from datetime import datetime, timezone
    months_since_update = (datetime.now(timezone.utc) - parse_date(updated_at)).days / 30
    if months_since_update < 6:
        return 1.0
    elif months_since_update < 12:
        return 0.75
    elif months_since_update < 24:
        return 0.5
    else:
        return 0.25

def score_user(user_data, repos):
    followers = user_data['followers']
    public_repos = user_data['public_repos']

    total_crypto_score = 0
    total_recency_weight = 0

    for repo in repos:
        stars = repo.get('stargazers_count', 0)
        language = repo.get('language')
        description = (repo.get('description') or '').lower()
        name = repo.get('name', '').lower()
        updated_at = repo.get('updated_at')

        if not updated_at:
            continue

        recency_weight = calculate_recency_weight(updated_at)
        total_recency_weight += recency_weight

        # Crypto relevance
        keyword_hit = any(keyword in (name + description) for keyword in CRYPTO_KEYWORDS)
        is_crypto_lang = language in CRYPTO_LANGUAGES
        crypto_factor = (1 if keyword_hit else 0) + (1 if is_crypto_lang else 0)

        # Crypto contribution quality: weighted by stars and recency
        repo_score = crypto_factor * (1 + stars / 10.0) * recency_weight
        total_crypto_score += repo_score

    avg_crypto_repo_score = (total_crypto_score / total_recency_weight) if total_recency_weight else 0

    score = (
        0.1 * followers +              # down-weighted
        0.1 * public_repos +
        0.6 * avg_crypto_repo_score +  # main contributor
        0.2 * total_crypto_score       # raw volume also matters
    )

    return round(score, 2)
