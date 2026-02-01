import requests
username= "PillGod25"
url=f"https://api.chess.com/pub/player/{username}/games/2025/12"
headers = {
    "User-Agent": "ChessBlunderTracker/1.0 (Contact: aiden.tg25@gmail.com)"
}
response=requests.get(url,headers=headers)
if response.status_code ==200:
    data=response.json()
    print(f"Found {len(data['games'])} games")
    print(data['games'][0]['pgn'][:200])
else:
    print("Failed to retrieve data")
    print(response.status_code)