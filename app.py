import requests
import chess
import chess.pgn
import re
from io import StringIO
username=input("Enter chess.com username: ")
month=int(input("Enter month(1-12): "))
year=int(input("Enter year: "))
url=f"https://api.chess.com/pub/player/{username}/games/{year:04d}/{month:02d}"
headers = {
    "User-Agent": f"ChessBlunderTracker (Contact: {username})"
}
response=requests.get(url,headers=headers)
if response.status_code ==200:
    data=response.json()
    status={
        'total_games': 0,
        'wins': 0,
        'losses': 0,
        'draws': 0,
        'openings':{}
    }
    games=data.get('games',[])
    if not games:
        print(f"No games played in {month}/{year} for user {username}.")
    else:
        for i, game in enumerate(games[:], 1):
                status['total_games']+=1 
                print(f"Game {i}:")
                print(f"  White: {game['white']['username']}")
                print(f"  Black: {game['black']['username']}")
                user_color = 'white' if game['white']['username'].lower() == username.lower() else 'black'
                user_result = game[user_color]['result']
                print(f"  Result for {username} ({user_color}): {user_result}")
                if user_result == 'win':
                    status['wins'] += 1
                elif user_result in ['checkmated', 'timeout', 'resigned', 'abandoned']:
                    status['losses'] += 1
                else:
                    status['draws'] += 1
                if 'pgn' in game:
                    pgn = StringIO(game['pgn'])
                    chess_game = chess.pgn.read_game(pgn)
                    if chess_game:
                        variant=chess_game.headers.get('Variant','Standard')
                        print(f"  Variant: {variant}")
                        openingurl=chess_game.headers.get('ECOUrl','UNKNOWN')
                        opening=openingurl.split('/')[-1].replace('-',' ') if openingurl !='UNKNOWN' else 'UNKNOWN'
                        opening = re.split(r'\s+\d', opening)[0]
                        status['openings'][opening] = status['openings'].get(opening, 0) + 1
                        moves = list(chess_game.mainline_moves())
                        print(f"  Opening: {opening}")
                        print(f"  Moves: {len(moves)}")
                print()    
    print("Summary:")
    print(f"Total games: {status['total_games']}")
    print(f"Wins: {status['wins']}")
    print(f"Losses: {status['losses']}")
    print(f"Draws: {status['draws']}")
    print("Openings played:")
    print(f"Opening count: {len(status['openings'])}")
    for opening, count in status['openings'].items():
        print(f"  {opening}: {count}")
else:
    print("Failed to retrieve data")
    print(response.status_code)
