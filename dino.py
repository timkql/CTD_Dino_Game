import sqlite3
from datetime import datetime
import random
import time
import curses
import os

JUMP_HEIGHT = 6
MAP_HEIGHT = 20
MAP_WIDTH = 200

# Database
def setup_database():
    """Setup score history database"""

    con = sqlite3.connect("dino.db")
    cur = con.cursor()
    res = cur.execute(
        "SELECT name FROM sqlite_master WHERE name='score_history'")
    if (res.fetchone() is None):
        cur.execute("CREATE TABLE score_history(username, date, score)")


def add_score_to_db(username: str, date: datetime, score: int):
    """Add player score data to database"""

    con = sqlite3.connect("dino.db")
    cur = con.cursor()
    cur.execute(
        f"INSERT INTO score_history (username, date, score) VALUES ('{username}', '{date}', {score})")


class Character:
    """Character Class"""

    sprite = '''
     .----.   @   @
   / .-"-.`.  \_/
   | | '\ \ \_/ )
 ,-\ `-.' /.'  /
'---`----'----'  
    '''
    score = 0
    username = ''
    date_created = None

    def __init__(self, username):
        self.username = username
        self.date_created = datetime.now()
        return


def generate_map_block(width):
    """Function to generate map blocks programatically about 200 characters wide 
    with constraint that character will always be able to survive (e.g. nothing above jump height, 
    map blocks must not create unclearable obstacles after combining)"""

    # using 0 for clear space 1 for obstacle
    HEIGHT = MAP_HEIGHT
    WIDTH = width
    map_block = []
    # Predefined map objects (with front and back spacing)
    cactus_small = [[0 for i in range(HEIGHT)] for j in range(26)]+[[0 if i>2 else 1 for i in range(HEIGHT)] for j in range(4)]+[[0 for i in range(HEIGHT)] for j in range(18)]
    cactus_tall = [[0 for i in range(HEIGHT)] for j in range(30)]+[[0 if i>4 else 1 for i in range(HEIGHT)] for j in range(2)]+[[0 for i in range(HEIGHT)] for j in range(22)]
    cactus_wide = [[0 for i in range(HEIGHT)] for j in range(30)]+[[0 if i>1 else 1 for i in range(HEIGHT)] for j in range(8)]+[[0 for i in range(HEIGHT)] for j in range(26)]
    bird = [[0 for i in range(HEIGHT)] for j in range(5)]+[[0 if i<(HEIGHT-6) or i>(HEIGHT-5) else 1 for i in range(HEIGHT)] for j in range(3)]+[[0 for i in range(HEIGHT)] for j in range(2)]
    obstacles  = [cactus_small,cactus_tall,cactus_wide,bird]
    
    while(1):
        obs = random.choice(obstacles)
        if(len(map_block)+len(obs)>WIDTH):
            map_block.extend([[0 for i in range(HEIGHT)]for j in range(WIDTH-len(map_block))])
            break
        else:
            map_block.extend(obs)
    return map_block

# def output_text_testing(text_list):
#     print(len(text_list))    
#     print(len(text_list[0]))
#     for i in range(len(text_list[0])-1,-1,-1):
#         print(''.join(["\u2588" if j==1 else " " for j in [t[i] for t in text_list]]))
    


def player_setup():
    """Setup a Character object. Prompts player to start by keying in username"""
    
    username = input("Enter your username to kick things off: ")
    return Character(username)


def start_game():
    """Game Engine that handles game operation, score calculation, player death"""

    setup_database()
    character = player_setup()
    # character = Character("Timbo")

    # Start curses application
    console = curses.initscr()
    curses.noecho()
    curses.cbreak()
    console.keypad(True)

    step, score, delay = 0, 0, 0.02
    map_block = generate_map_block(MAP_WIDTH*2)
    while True:
        # Generate next map block
        if(step == MAP_WIDTH):
                map_block = map_block[step:int(len(map_block)/2)+step] + generate_map_block(MAP_WIDTH)
                step = 0
                # Speed increases for each new map block until max speed
                if (delay > 0.005):
                    delay *= 0.95
        output_map_block = map_block[step:int(len(map_block)/2)+step]

        # Output map row by row
        console.clear()
        for i in range(len(output_map_block[0]) - 5, -1, -1):
            row = "".join(["\u2588" if j==1 else " " for j in [t[i] for t in output_map_block]])
            console.addstr(15-i, 0, row)
        console.refresh()
        
        step += 1
        score += 1
        time.sleep(delay)  

        if step == 100:
            break
    
    character.score = score
    add_score_to_db(character.username, datetime.now(), score)
    console.clear()
    console.addstr(0, 0, "FINAL SCORE: " + str(score))
    console.refresh()
    time.sleep(10)


    # Terminate curses application
    curses.nocbreak()
    console.keypad(False)
    curses.echo()
    curses.endwin()


start_game()
