import sqlite3
import random
JUMP_HEIGHT = 6

# Database
def setup_database():
    """Setup score history database"""

    con = sqlite3.connect("dino.db")
    cur = con.cursor()
    res = cur.execute("SELECT name FROM sqlite_master WHERE name='score_history'")
    if (res.fetchone() is None):
        cur.execute("CREATE TABLE score_history(username, date, score)")

def add_score_to_db(username: str, date: str, score: int):
    """Add player score data to database"""
    con = sqlite3.connect("dino.db")
    cur = con.cursor()
    cur.execute(f"INSERT INTO score_history (username, date, score) VALUES ('{username}', {date}, {score})")


# TODO: Character Class 
# fields: username, date_created, score, sprite fields
# date_created should be automatically set when class instance is created
# sprite should be pre-set for simplicity (something simple 3 characters wide or around there)
class Character:
    some_variable = ""

# TODO: Function to generate map blocks programatically about 200 characters wide 
# with constraint that character will always be able to survive (e.g. nothing above jump height, 
# map blocks must not create unclearable obstacles after combining)
def generate_map_block():
    # using 0 for clear space 1 for obstacle
    HEIGHT = 20
    WIDTH = 200
    map_block = []
    # Predefined map objects (with front and back spacing)
    cactus_small = [[0 for i in range(HEIGHT)] for j in range(4)]+[[0 if i>2 else 1 for i in range(HEIGHT)] for j in range(4)]+[[0 for i in range(HEIGHT)] for j in range(2)]
    cactus_tall = [[0 for i in range(HEIGHT)] for j in range(5)]+[[0 if i>4 else 1 for i in range(HEIGHT)] for j in range(2)]+[[0 for i in range(HEIGHT)] for j in range(3)]
    cactus_wide = [[0 for i in range(HEIGHT)] for j in range(5)]+[[0 if i>1 else 1 for i in range(HEIGHT)] for j in range(8)]+[[0 for i in range(HEIGHT)] for j in range(4)]
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

def output_text_testing(text_list):
    print(len(text_list))    
    print(len(text_list[0]))
    for i in range(len(text_list[0])-1,-1,-1):
        print(''.join(["\u2588" if j==1 else " " for j in [t[i] for t in text_list]]))

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


#testing, ignore
output_text_testing(generate_map_block())