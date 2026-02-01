import requests
import chess
import chess.pgn
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
    games=data.get('games',[])
    if not games:
        print(f"No games played in {month}/{year} for user {username}.")
    else:
        for i, game in enumerate(games[:], 1): 
                print(f"Game {i}:")
                print(f"  White: {game['white']['username']}")
                print(f"  Black: {game['black']['username']}")
                print(f"  Result(White): {game['white']['result']}")
                print(f"  Result(Black): {game['black']['result']}")
                
                if 'pgn' in game:
                    pgn = StringIO(game['pgn'])
                    chess_game = chess.pgn.read_game(pgn)
                    if chess_game:
                        moves = list(chess_game.mainline_moves())
                        print(f"  Moves: {len(moves)}")
                print()    

else:
    print("Failed to retrieve data")
    print(response.status_code)