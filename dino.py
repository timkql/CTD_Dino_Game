import sqlite3
from datetime import datetime

JUMP_HEIGHT = 6

# Database


def setup_database():
    """Setup score history database"""

    con = sqlite3.connect("dino.db")
    cur = con.cursor()
    res = cur.execute(
        "SELECT name FROM sqlite_master WHERE name='score_history'")
    if (res.fetchone() is None):
        cur.execute("CREATE TABLE score_history(username, date, score)")


def add_score_to_db(username: str, date: str, score: int):
    """Add player score data to database"""
    con = sqlite3.connect("dino.db")
    cur = con.cursor()
    cur.execute(
        f"INSERT INTO score_history (username, date, score) VALUES ('{username}', {date}, {score})")


# TODO: Character Class
# fields: username, date_created, score, sprite fields
# date_created should be automatically set when class instance is created
# sprite should be pre-set for simplicity (something simple 3 characters wide or around there)
class Character:
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

# TODO: Function to generate map blocks programatically about 200 characters wide
# with constraint that character will always be able to survive (e.g. nothing above jump height,
# map blocks must not create unclearable obstacles after combining)


def generate_map_block():
    """Function to generate map blocks programatically"""
    pass

# TODO: Prompts player to start by keying in username


def player_setup():
    """Setup a Character object"""
    username = input("Enter your username to kick things off:")
    return Character()

# TODO: Game Engine that handles game operation, score calculation, player death


def start_game(character: Character):
    """Game Engine"""
    pass


# Main program
setup_database()
character = player_setup()
start_game(character)
