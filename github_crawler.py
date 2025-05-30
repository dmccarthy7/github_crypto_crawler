import requests
import time
from github_crypto_scorer import fetch_user_data, fetch_repos, score_user

# --- GitHub Authentication ---
GITHUB_TOKEN = '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'  # Replace with your token
HEADERS = {'Authorization': f'token {GITHUB_TOKEN}'} if GITHUB_TOKEN else {}

# --- Crypto Projects to Crawl Contributors From ---
CRYPTO_REPOS = [
    ('ethereum', 'go-ethereum'),
    ('Uniswap', 'uniswap-v3-core'),
    ('paradigmxyz', 'foundry'),
    ('OpenZeppelin', 'openzeppelin-contracts'),
    ('aave', 'aave-v3-core')
]

def get_contributors(owner, repo):
    url = f'https://api.github.com/repos/{owner}/{repo}/contributors'
    print(f"📡 Requesting: {url}")
    print(f"🪪 Using headers: {HEADERS}")  # ← ADD THIS LINE
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
        return [user['login'] for user in response.json()]
    else:
        print(f"❌ Failed to fetch contributors for {owner}/{repo}: {response.status_code}")
        return []

def crawl_and_score(max_users=20):
    seen_users = set()
    scored_users = []
    count = 0

    for owner, repo in CRYPTO_REPOS:
        contributors = get_contributors(owner, repo)
        for username in contributors:
            if username in seen_users:
                continue
            seen_users.add(username)

            try:
                user_data = fetch_user_data(username, headers=HEADERS)
                repos = fetch_repos(username, headers=HEADERS)
                score = score_user(user_data, repos)
                scored_users.append((username, score))
                print(f"Scored {username}: {score}")
                count += 1
                if count >= max_users:
                    print(f"\nReached max of {max_users} users — stopping.")
                    return sorted(scored_users, key=lambda x: x[1], reverse=True)
                time.sleep(1)  # avoid hitting rate limits
            except Exception as e:
                print(f"Error scoring {username}: {e}")

    scored_users.sort(key=lambda x: x[1], reverse=True)
    return scored_users[:max_users]

if __name__ == '__main__':
    top_users = crawl_and_score(max_users=20)
    print("\nTop Scoring GitHub Users:")
    for rank, (user, score) in enumerate(top_users, 1):
        print(f"{rank}. {user}: {score}")
