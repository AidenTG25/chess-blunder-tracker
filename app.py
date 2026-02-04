import requests
import chess
import chess.pgn
import re
from io import StringIO
import os
from dotenv import load_dotenv

load_dotenv()
engine_path = os.getenv("STOCKFISH")
if engine_path:
    engine = chess.engine.SimpleEngine.popen_uci(engine_path)
    engine_available = True
else:
    print("Stockfish not found. Please download STOCKFISH and set STOCKFISH environment variable.")
    engine_available = False


username=input("Enter chess.com username: ")
month=int(input("Enter month(1-12): "))
year=int(input("Enter year: "))
depth=int(input("Enter engine analysis depth: "))
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
                        if variant in ['Chess960','Horde','Racing Kings']:
                            opening =variant
                        status['openings'][opening] = status['openings'].get(opening, 0) + 1
                        moves = list(chess_game.mainline_moves())
                        move_num = 0
                        print(f"  Opening: {opening}")
                        print(f"  Moves: {len(moves)}")
                        if engine_available and i ==len(games):
                            board = chess_game.board()
                            pre_score=None
                            blunders = 0
                            blunder_phase={'opening': 0, 'middlegame': 0, 'endgame': 0}
                            for node in chess_game.mainline():
                                move = node.move
                                move_num += 1
                                is_white_move = (move_num % 2 == 1)
                                is_usermove = (user_color == 'white' and is_white_move) or (user_color == 'black' and not is_white_move)
                                
                                if is_usermove:
                                    info = engine.analyse(board, chess.engine.Limit(depth=depth))
                                    current_score = info["score"].white().score(mate_score=10000)
                                    if move_num <=30:
                                        phase = 'opening'
                                    elif move_num <=60:
                                        phase = 'middlegame'
                                    else:
                                        phase = 'endgame'
                                    if pre_score is not None and current_score is not None:
                                        if user_color == 'white':
                                            if pre_score - current_score >= 300:
                                                blunder_phase[phase] += 1
                                                blunders += 1
                                        else:
                                            if current_score - pre_score >= 300:
                                                blunder_phase[phase] += 1
                                                blunders += 1         
                                    pre_score = current_score  
                                board.push(move)                     
                            print(f"  Blunders detected by engine: {blunders}")
                            print(f"  Blunders by phase:")
                            for phase, count in blunder_phase.items():
                                print(f"    {phase.capitalize()}: {count}")
                        
                print()
        if engine_available:
            engine.quit()    
    print("  Summary:")
    print(f"  Total games: {status['total_games']}")
    print(f"  Wins: {status['wins']}")
    print(f"  Losses: {status['losses']}")
    print(f"  Draws: {status['draws']}")
    print()
    print(f"  Openings played:")
    sorted_openings = sorted(status['openings'].items(), key=lambda x: x[1], reverse=True)
    for opening, count in sorted_openings:
        print(f"  {opening}: {count}")
else:
    print("Failed to retrieve data")
    print(response.status_code)

