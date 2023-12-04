# CTD 1D: Dino game documentation

## Initialization
### Library imports

```py
import sqlite3
from datetime import datetime
import random
import time
import curses
import os
```
### Constant parameters for game
```py

JUMP_SPEED = 0.5
FALL_SPEED = -0.4
JUMP_HEIGHT = 8
MAP_HEIGHT = 20
MAP_WIDTH = 200
LEFT_OFFSET = 5
```
## High score database 
### Setup

Check's if ```score_history``` table exists in the SQLite database, if not create the score_history table.
```py
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
```
### Add record
Adds a new record into the ```score_history``` table
```py
def add_new_record_to_db(username: str, date: datetime, score: int):
    """Add player score data to database"""

    con = sqlite3.connect("dino.db")
    cur = con.cursor()
    cur.execute(
        f"INSERT INTO score_history (username, date, score) VALUES (?, ?, ?)", (username, date, score))
    con.commit()
    cur.close()
    con.close()
```
### Get record
Gets a record from the ```score_history``` table for a username
```py
def get_record_for_username(username: str):
    """Get record for username"""

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
```
### Update score
Updates a ```score_history``` table record's score column for a username
```py
def update_score_for_username(username: str, score: int):
    """Update a row's score and score date by username"""

    con = sqlite3.connect("dino.db")
    cur = con.cursor()
    cur.execute(f"UPDATE score_history SET score={score} WHERE username='{username}'")
    cur.execute(f"UPDATE score_history SET date={datetime.now()} WHERE username='{username}'")
    con.commit()
    con.commit()
    cur.close()
    con.close()
```
### Get device highscore
Retrieves record for highest score column value from the ```score_history``` table
```py
    
def get_highest_score_record_for_device():
    """Retrieves record for highest score on device"""

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
    
```
## Record class
A ```score_history``` table record class
```py
# Class Definitions
class Record:
    """Record Class"""
    username: str
    date: datetime
    score: int
```
### Record constructor
```Record``` instance is initilized with username, date of highest score and highest score inputs
```py
    def __init__(self, username, date, score):
        self.username = username
        self.date = date
        self.score = score
```
## Character class
A character class containing score, username, game sprite, and in-game attributes.
```py
class Character:
    """Character Class"""

    sprite = '''
   __   
  (__\_ 
-{{_(|8)
   (__/ '''
    score = 0
    username = ''
    date_created = None
    y_pos = 0
    y_vel = 0
    game_speed = 22
    sprite_list = []
```
### Character constructor
```Character``` instance is initialized with a username input
```py
    def __init__(self, username):
        self.username = username
        self.date_created = datetime.now()
        self.sprite_list = [list(a) for a in self.sprite.split('\n')[1::]][::-1]
        return
```
### Reset function
Resets the velocity and position of the ```Character``` instance
```py
    def reset(self):
        self.y_pos = 0
        self.y_vel = 0
        
```
### Reset function
Starts a jump action if the sprite is not already jumping. Sets the vertical velocity to a positive value.
```py
    def jump(self):
        """Starts a jump by setting vertical velocity"""
        if(self.y_vel!=0 or self.y_pos !=0):    #Check if already jumping
            return
        self.y_vel = JUMP_SPEED
        return
```
### Update position function
Finds the next value for the y-position based on the current y-velocity. Flips the y-velocity once maximum y-position has been reached.
```py
    def update_y_pos(self):
        """Performs physics calculations to find the new vertical position of the sprite"""
        if(self.y_vel!=0 or self.y_pos>0):
            self.y_pos += self.y_vel # Update position based on v
            if(self.y_pos<=0): # Below floor, set v to 0
                self.y_pos=0
                self.y_vel=0
            else:
                if(self.y_pos>= JUMP_HEIGHT): # Hit max jump height
                    self.y_vel = FALL_SPEED
                    
        return
```
### Collision detection function
Slices part of the map to check if any part of the sprite is intersecting a map obstacle. Iterate through the sliced portion to check for intersections.
```py
    def check_coll(self, cur_map_block):
        """References the bottom left of the sprite, slices rectangle of size of sprite and check collision"""
        y_pos_int = int(round(self.y_pos))
        check_area = [j[y_pos_int:y_pos_int+len(self.sprite_list)] for j in cur_map_block[LEFT_OFFSET:LEFT_OFFSET+len(self.sprite_list[0])]] #slice the 2d map
        for k in check_area:
            for l in k:
               if(l==1):
                   return True # collided with object
        return False
```
### Character list function
Returns a 2D list of characters to be displayed. Replaces all characters taken up by the sprite after creating a 2D list for the map characters.
```py
    def ret_screen(self, cur_map_block):
        """Returns a 2D List of text characters to be rendered on-screen"""
        output_char_list = []
        for i in range(len(cur_map_block[0]) - 5, -1, -1):
            row = ["\u2588" if j==1 else " " for j in [t[i] for t in cur_map_block]]
            output_char_list.append(row)
        output_char_list.reverse()
        y_pos_int = int(round(self.y_pos))
        # Draw sprite onto the list
        for k in range(len(self.sprite_list)):
            for j in range(len(self.sprite_list[0])):
                output_char_list[k+y_pos_int][j+LEFT_OFFSET] = self.sprite_list[k][j]
        return output_char_list

```
## Function definitions
### Map generation
```py
def generate_map_block(width):
    """Function to generate map blocks programatically about 200 characters wide 
    with constraint that character will always be able to survive (e.g. nothing above jump height, 
    map blocks must not create unclearable obstacles after combining)"""

    # using 0 for clear space 1 for obstacle
    HEIGHT = MAP_HEIGHT
    WIDTH = width
    map_block = []
```
### Predefined map objects
Define various obstacles as 2d lists of 0 and 1 values. 1 means an obstacle is pre
```py
    # Predefined map objects (with front and back spacing)
    cactus_small = [[0 for i in range(HEIGHT)] for j in range(30)]+[[0 if i>2 else 1 for i in range(HEIGHT)] for j in range(4)]
    cactus_tall = [[0 for i in range(HEIGHT)] for j in range(38)]+[[0 if i>4 else 1 for i in range(HEIGHT)] for j in range(2)]
    cactus_wide = [[0 for i in range(HEIGHT)] for j in range(42)]+[[0 if i>1 else 1 for i in range(HEIGHT)] for j in range(8)]
    bird = [[0 for i in range(HEIGHT)] for j in range(5)]+[[0 if i<(HEIGHT-8) else 1 for i in range(HEIGHT)] for j in range(3)]
    obstacles  = [cactus_small,cactus_tall,cactus_wide,bird]
```
### Map generation loop
Extend the map block with new map objects. If a new map object would cause the block to hit maximum length, pad the right of the block with empty space instead.
```py
    # Randomly add map objects until the map width is reached
    while(True):
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
    
```
### Player setup
Prompts player to enter their username and initializes a new ```Character``` object with it.
```py

def player_setup():
    """Setup a Character object. Prompts player to start by keying in username"""
    
    username = input("Enter your username to kick things off: ")
    return Character(username)

```
## Main game function
### Game start
Set up the highscore database, then call ```player_setup()``` to instantiate the ```Character``` for the game
```py
def start_game():
    """Game Engine that handles game operation, score calculation, player death"""

    setup_database()
    character = player_setup()
    playing = True
```
### Main loop
Repeats the maingame as long as the player has not exited. Initializes display area and display with ```curses```
```py
    while playing:
        # Start curses application
        console = curses.initscr()
        curses.noecho()
        curses.cbreak()
        console.keypad(True)
        # Set getch() to be non blocking and return -1 when no input
        console.nodelay(True)

        step, score, delay = 0, 0, (1.0/character.game_speed)
        map_block = generate_map_block(MAP_WIDTH*2)
```
## Loop for game events
### Get keyboard input
Checks the character being input and react accordingly. Space bar causes the character to jump and pressing k exits the game.
```py
        while True:
            keyPress = console.getch()
            # Jump if user presses spacebar
            if keyPress == ord(" "):
                character.jump()
            if keyPress == ord("k"):
                break
```
### Generate map if required
Creates more map when the width of the map has been traversed and extends the map. Deletes the portions of the map that are passed.
```py
            # Generate next map block
            if(step == MAP_WIDTH):
                    map_block = map_block[step:int(len(map_block)/2)+step] + generate_map_block(MAP_WIDTH)
                    step = 0
                    # Speed increases for each new map block until max speed
                    if (delay > 0.005):
                        delay *= 0.9
            output_map_block = map_block[step:int(len(map_block)/2)+step]

            # Output map row by row
            
            console.clear()
            '''
            for i in range(len(output_map_block[0]) - 5, -1, -1):
                row = "".join(["\u2588" if j==1 else " " for j in [t[i] for t in output_map_block]])
                console.addstr(15-i, 0, row)
            '''
```
### Check for collision
Calls the ```check_coll``` method to see if the player has died. 
```py
            # check for death
            dead = character.check_coll(output_map_block)
            character.update_y_pos()
            if(dead):
                break
```
### Draw output
Generates map output using ```Character.ret_screen``` method and outputs game sprite and map in terminal
```py
            # draw screen
            out_screen = character.ret_screen(output_map_block)
            for i in range(len(out_screen) - 5, -1, -1):
                # print(i)
                row = ''.join(out_screen[i])
                console.addstr(15-i, 0, row)
            
            console.refresh()
            
            step += 1
            score += 1
            time.sleep(delay)  
```
### Close console after character death
Terminates curses application and calls ```curses.endwin()``` method to revert terminal to original state after character death
```py
        # Terminate curses application
        console.clear()
        console.refresh()

        curses.nocbreak()
        console.keypad(False)
        curses.echo()
        curses.endwin()

```
### Score display
Retrieves highest score of player with ```get_record_for_username()``` and device with ```get_highest_score_record_for_device()```. Creates record of player if username does not exist in ```score_history``` table
```py
        # Endgame
        character.score = score
        user_record: Record = get_record_for_username(character.username)
        # If user has no record in DB
        if user_record.username == "":
            add_new_record_to_db(character.username, datetime.now(), score)
        device_highest_record: Record = get_highest_score_record_for_device()
```
### Score display
Display player's score, high score, and highest score data on device after character death
```py
        # Display Score
        print("\n")
        display_text = ""
        if user_record.score < score:
            display_text += f"YOUR NEW HIGH SCORE: {str(score)} - - - "
            update_score_for_username(character.username, score)
        else:
            display_text += f"YOUR SCORE: {str(score)} - - - YOUR HIGHEST SCORE: {user_record.score} - - - "

        if device_highest_record.score >= score:
            display_text += f"HIGHEST SCORE ON DEVICE: {str(device_highest_record.score)} BY {device_highest_record.username} ON {device_highest_record.date}"
        else: 
            display_text += f"NEW HIGHEST SCORE ON DEVICE: {str(character.score)} by {character.username} on {character.date_created}"
        print(display_text)
```
### Restart game if required
Displayed after character death for player to restart and play game again if desired
```py
        replay = input("Enter Y to play again: ")
        character.reset()
        if (replay.lower()!='y'):
            break
```
## Call main game 
```py
start_game()

```
