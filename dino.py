import sqlite3
from datetime import datetime
import random
import time
import curses
import os

JUMP_HEIGHT = 6
MAP_HEIGHT = 20
MAP_WIDTH = 200

# Database Functions
def setup_database():
    """Setup score history database"""

    con = sqlite3.connect("dino.db")
    cur = con.cursor()
    res = cur.execute(
        f"SELECT name FROM sqlite_master WHERE name='score_history'")
    if (res.fetchone() is None):
        cur.execute("CREATE TABLE score_history(username, date, score)")
    cur.close()
    con.close()
    
def add_new_record_to_db(username: str, date: datetime, score: int):
    """Add player score data to database"""

    con = sqlite3.connect("dino.db")
    cur = con.cursor()
    cur.execute(
        f"INSERT INTO score_history (username, date, score) VALUES (?, ?, ?)", (username, date, score))
    con.commit()
    cur.close()
    con.close()
    
def get_record_for_username(username: str):
    """Get score for username"""

    con = sqlite3.connect("dino.db")
    cur = con.cursor()
    cur.execute(f"SELECT * FROM score_history WHERE username='{username}'")
    row = cur.fetchone()
    cur.close()
    con.close()
    if row:
        return Record(row[0], row[1], row[2])
    else:  
        return Record("", "", 0)
    
    
def update_score_for_username(username: str, score: int):
    """Update a row's score by username"""

    con = sqlite3.connect("dino.db")
    cur = con.cursor()
    cur.execute(f"UPDATE score_history SET score={score} WHERE username='{username}'")
    con.commit()
    cur.close()
    con.close()
    
def get_highest_score_record_for_device():
    """Get data for highest score on device"""

    con = sqlite3.connect("dino.db")
    cur = con.cursor()
    cur.execute(f"SELECT * FROM score_history ORDER BY score DESC LIMIT 1;")
    row = cur.fetchone()
    cur.close()
    con.close()
    if row:
        return Record(row[0], row[1], row[2])
    else:  
        return Record("", "", 0)
    
# Class Definitions
class Record:
    """Record Class"""
    username: str
    date: datetime
    score: int

    def __init__(self, username, date, score):
        self.username = username
        self.date = date
        self.score = score

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
    # Set getch() to be non blocking and return -1 when no input
    console.nodelay(True)

    step, score, delay = 0, 0, 0.02
    map_block = generate_map_block(MAP_WIDTH*2)
    while True:
        keyPress = console.getch()
        # Jump if user presses spacebar
        if keyPress == ord(" "):
            # TODO: John do what u must
            pass
        if keyPress == ord("k"):
            break

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

    # Terminate curses application
    console.clear()
    console.refresh()

    curses.nocbreak()
    console.keypad(False)
    curses.echo()
    curses.endwin()
    
    # Endgame
    character.score = score
    user_record: Record = get_record_for_username(character.username)
    # If user has no record in DB
    if user_record.username == "":
        add_new_record_to_db(character.username, datetime.now(), score)
    device_highest_record: Record = get_highest_score_record_for_device()

    # Display Score
    print("\n")
    display_text = ""
    if user_record.score < score:
        display_text += f"YOUR NEW HIGH SCORE: {str(score)} - - - "
        update_score_for_username(character.username, score)
    else:
        display_text += f"YOUR SCORE: {str(score)} YOUR HIGHEST SCORE: {user_record.score} - - - "

    if device_highest_record.score >= score:
        display_text += f"HIGHEST SCORE ON DEVICE: {str(device_highest_record.score)} BY {device_highest_record.username} ON {device_highest_record.date}"
    else: 
        display_text += f"NEW HIGHEST SCORE ON DEVICE: {str(character.score)} by {character.username} on {character.date_created}"
    print(display_text)

start_game()
