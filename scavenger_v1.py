# written by Mauve, with slight improvements by vexi

import random
import os
import time
from enum import Enum
import sys
import tty
import termios

# GAME SETTINGS
# width and height of the map
WIDTH, HEIGHT = 30, 10
# step cost + step divider
STEP_COST = 1
STEP_DIVIDER = 3
# number of obstacles to place
MIN_NUM_OBSTACLES = 80
MAX_NUM_OBSTACLES = 120
# number of cores to collect
NUM_CORES = 20
# number of monsters to spawn
MIN_NUM_MONSTERS = 10
MAX_NUM_MONSTERS = 10


def getch():
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(sys.stdin.fileno())
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch

class GameState(Enum):
    PLAYING = 1
    VIEWING_RULES = 2
    VIEWING_LORE = 3
    SUCCESS = 4
    FAILED = 5

# penalty for not clearing the entire area??
# make core goal
# report on potential item value efficiency (algorithm)
# count how many bogeys defeated, some sort of penalty for killing too many bogeys in 1 instance?

class RogueLikeGame:
    COLOR_GREEN = '\033[92m'  # Green for player
    COLOR_RED = '\033[91m'    # Red for rare monsters
    COLOR_BLUE = '\033[94m'   # Blue for normal monsters
    COLOR_YELLOW = '\033[33m' # Yellow for common monsters
    COLOR_WHITE = '\033[37m'  # White for obstacles and empty spaces
    COLOR_DEFAULT = '\033[90m'  # dark blue for obstacles and empty spaces
    COLOR_RESET = '\033[0m'   # Reset to default color
    COLOR_PINK = '\033[35m'   # Pink for items
    def __init__(self, width, height, num_items_to_collect):
        self.width = width
        self.height = height
        self.player_x = 0
        self.player_y = 0
        self.exit_x = 0
        self.exit_y = 0
        self.num_items_to_collect = num_items_to_collect
        self.items_collected = 0
        self.total_items_collected = 0
        self.initial_items = 0
        self.initial_monsters = 0
        self.steps = 0
        self.monsters = []
        self.monsters_defeated = 0
        self.monster_levels = {'Common': 1, 'Normal': 2, 'Rare': 3}
        self.game_state = GameState.PLAYING
        self.prev_game_state = None
        self.min_steps_needed = 0
        self.max_steps_allowed = 0
        self.solution = []
        self.solution_step_count = 0
        self.solution_start_x = 0
        self.solution_start_y = 0
    

    def validate_level(self):
        start = (self.player_x, self.player_y)
        goal = (self.exit_x, self.exit_y)

        # Initialize the solution steps count
        self.solution_step_count = 0

        # Queue elements are tuples of the form (position, steps_taken, cores_collected, path)
        queue = [(start, 0, 0, [start])]
        visited = set([start])

        while queue:
            current, steps, cores, path = queue.pop(0)

            # Check if the current position is the goal and if the path is valid
            if current == goal and steps <= self.max_steps_allowed and cores * STEP_DIVIDER >= steps:
                self.solution = path  # Save the successful path
                self.solution_step_count = steps  # Save the steps count
                return True

            for dx in [-1, 0, 1]:
                for dy in [-1, 0, 1]:
                    if dx != 0 and dy != 0:
                        continue

                    neighbor = (current[0] + dx, current[1] + dy)

                    # Check if the neighbor is within bounds and not an obstacle
                    if 0 <= neighbor[0] < self.width and 0 <= neighbor[1] < self.height and self.level[neighbor[1]][neighbor[0]] != '#' and neighbor not in visited:
                        new_cores = cores
                        new_steps = steps + 1
                        new_path = path + [neighbor]  # Add neighbor to the path

                        # Check if the neighbor is a core and update cores collected
                        if self.level[neighbor[1]][neighbor[0]] == 'I':
                            new_cores += 1
                        # Check if the neighbor is a monster and update cores collected
                        elif self.level[neighbor[1]][neighbor[0]] in ['C', 'N', 'R']:
                            monster_level = self.get_monster_level_from_symbol(self.level[neighbor[1]][neighbor[0]])
                            new_cores += self.monster_levels[monster_level]

                        # Add neighbor to the queue
                        queue.append((neighbor, new_steps, new_cores, new_path))
                        visited.add(neighbor)

        return False


    def get_monster_level_from_symbol(self, symbol):
        # map symbols to monster levels
        symbol_level_map = {'C': 'Common', 'N': 'Normal', 'R': 'Rare'}
        return symbol_level_map.get(symbol, 'Common')  # default to 'Common' if symbol is not recognized

    def show_solution(self):
        if not hasattr(self, 'solution') or not self.solution:
            print("No solution available.")
            return

        # Get the starting coordinates of the solution path
        solution_start_x, solution_start_y = self.solution_start_x, self.solution_start_y

        # Iterate through each cell in the level
        for y in range(self.height):
            for x in range(self.width):
                position = (x, y)

                if position == (solution_start_x, solution_start_y):
                    print(f"{self.COLOR_GREEN}P{self.COLOR_RESET}", end=" ")
                elif position in self.solution and self.level[y][x] not in ['P', 'E']:
                    print(f"{self.COLOR_PINK}${self.COLOR_RESET}", end=" ")
                elif self.level[y][x] == 'P':
                    print(f"{self.COLOR_WHITE}E{self.COLOR_RESET}", end=" ")
                elif self.level[y][x] in ['C', 'N', 'R']:
                    color = self.get_monster_color(self.level[y][x])
                    print(f"{color}{self.level[y][x]}{self.COLOR_RESET}", end=" ")
                elif self.level[y][x] == '#':
                    print(f"{self.COLOR_DEFAULT}#{self.COLOR_RESET}", end=" ")
                elif self.level[y][x] == 'I':
                    print(f"{self.COLOR_WHITE}I{self.COLOR_RESET}", end=" ")
                else:
                    print(" ", end=" ")
            print()  # New line after each row

        input("Press any key to continue...")  # Pause to allow the user to view the solution



    def reconstruct_path(self, came_from, current):
        path = []
        while current is not None:
            path.append(current)
            current = came_from[current]
        return path[::-1]

    def generate_level(self, recursion_depth=0):
        MAX_RECURSION_DEPTH = 1000  # Define a maximum recursion depth

        if recursion_depth > MAX_RECURSION_DEPTH:
            raise Exception("Maximum recursion depth exceeded while generating level.")


        self.monsters.clear()
        self.solution.clear()

        # empty spaces
        self.level = [['.' for _ in range(self.width)] for _ in range(self.height)]

        # random location
        self.player_x = random.randint(0, self.width - 1)
        self.player_y = random.randint(0, self.height - 1)
        while self.level[self.player_y][self.player_x] != '.':
            self.player_x = random.randint(0, self.width - 1)
            self.player_y = random.randint(0, self.height - 1)

        self.level[self.player_y][self.player_x] = 'P'

        self.solution_start_x = self.player_x
        self.solution_start_y = self.player_y

        # exit
        while True:
            # at least 20 steps away from the player
            self.exit_x = random.randint(0, self.width - 1)
            self.exit_y = random.randint(0, self.height - 1)
            if abs(self.exit_x - self.player_x) + abs(self.exit_y - self.player_y) >= 10 and self.level[self.exit_y][self.exit_x] == '.':
                break

        # random obstacles
        num_obstacles = random.randint(MIN_NUM_OBSTACLES, MAX_NUM_OBSTACLES)
        for _ in range(num_obstacles):
            obstacle_x = random.randint(0, self.width - 1)
            obstacle_y = random.randint(0, self.height - 1)

            # Make sure obstacles are not placed on the player or the exit
            while (obstacle_x == self.player_x and obstacle_y == self.player_y and obstacle_x == self.exit_x and obstacle_y == self.exit_y):
                obstacle_x = random.randint(0, self.width - 1)
                obstacle_y = random.randint(0, self.height - 1)

            self.level[obstacle_y][obstacle_x] = '#'

        self.level[self.exit_y][self.exit_x] = 'E'

        # items/cores
        for _ in range(self.num_items_to_collect):
            while True:
                item_x = random.randint(0, self.width - 1)
                item_y = random.randint(0, self.height - 1)

                # make sure the item is not blocked by obstacles, the player, or the exit
                if (
                    self.level[item_y][item_x] == '.' and
                    (item_x != self.player_x or item_y != self.player_y) and
                    (item_x != self.exit_x or item_y != self.exit_y)
                ):
                    break

            self.level[item_y][item_x] = 'I'

        # bogeys on the map with random levels
        # change the upper limit of num_monsters to increase the chances of bogeys appearing
        num_monsters = random.randint(MIN_NUM_MONSTERS, MAX_NUM_MONSTERS)
        for _ in range(num_monsters):
            while True:
                monster_x = random.randint(0, self.width - 1)
                monster_y = random.randint(0, self.height - 1)
                monster_level = random.choice(list(self.monster_levels.keys()))

                # ensures monster is not blocked by obstacles, the player, the exit, or other monsters
                if (
                    self.level[monster_y][monster_x] == '.' and
                    (monster_x != self.player_x or monster_y != self.player_y) and
                    (monster_x != self.exit_x or monster_y != self.exit_y)
                ):
                    break

            # diff symbol diff monster
            monster_symbol = self.get_monster_symbol(monster_level)
            self.level[monster_y][monster_x] = monster_symbol
            self.monsters.append({'x': monster_x, 'y': monster_y, 'level': monster_level})

        # record the initial number of items
        self.initial_items = sum(row.count('I') for row in self.level)
        self.initial_monsters = len(self.monsters)
        
        # Calculate the maximum steps allowed
        max_cores = self.initial_items + self.initial_monsters
        self.max_steps_allowed = max_cores * STEP_DIVIDER

        if not self.validate_level():
            self.generate_level(recursion_depth + 1)
        
    def move_monsters(self):
        player_pos = (self.player_x, self.player_y)
        new_positions = []
        occupied_positions = {(m['x'], m['y']) for m in self.monsters}  # Current monster positions

        for monster in self.monsters:
            if self.is_monster_active(monster, player_pos):
                move_options = self.get_move_options(monster, occupied_positions)
                if move_options:
                    move_direction = random.choice(move_options)
                    new_x, new_y = monster['x'] + move_direction[0], monster['y'] + move_direction[1]
                    new_positions.append((monster, new_x, new_y))
                    occupied_positions.add((new_x, new_y))  # Reserve this spot

        # Move all monsters after calculating new positions
        for monster, new_x, new_y in new_positions:
            self.execute_monster_move(monster, new_x, new_y)

    def execute_monster_move(self, monster, new_x, new_y):
        # Ensure the new position is not currently occupied by the player
        if (new_x, new_y) == (self.player_x, self.player_y):
            return  # Do not move the monster if it would collide with the player

        # Clear the old monster position
        self.level[monster['y']][monster['x']] = '.'

        # Move the monster
        monster['x'], monster['y'] = new_x, new_y
        self.level[new_y][new_x] = self.get_monster_symbol(monster['level'])

    def get_move_options(self, monster, occupied_positions):
        move_options = []
        
        for dx in [-1, 0, 1]:  # only consider horizontal movements
            for dy in [-1, 0, 1]:  # only consider vertical movements
                if dx != 0 and dy != 0:  # no diagonal movements
                    continue

                new_x, new_y = monster['x'] + dx, monster['y'] + dy

                # check if the new position is within the boundaries and not an obstacle
                if 0 <= new_x < self.width and 0 <= new_y < self.height and self.level[new_y][new_x] == '.' and (new_x, new_y) not in occupied_positions:
                    move_options.append((dx, dy))

        return move_options

    # Call this method only after all monsters have moved
    def update_player_position(self, new_x, new_y):
        # Clear the old player position if it's not an item, monster, or exit
        if self.level[self.player_y][self.player_x] == 'P':
            self.level[self.player_y][self.player_x] = '.'
        
        # Set the new player position in the level
        self.level[new_y][new_x] = 'P'
        self.player_x, self.player_y = new_x, new_y



    def is_monster_active(self, monster, player_pos):
        proximity = self.calculate_proximity(monster, player_pos)
        move_frequency = self.monster_levels.get(monster['level'], 1)

        # Monsters move more frequently when the player is closer
        return proximity < move_frequency * 2  # Adjust as needed

    def calculate_proximity(self, monster, player_pos):
        return abs(monster['x'] - player_pos[0]) + abs(monster['y'] - player_pos[1])  # Manhattan Distance


    def animate_text(self, text, delay=0.1, end=True):
        for char in text:
            print(char, end='', flush=True)
            time.sleep(delay)
        if end:
            print()

    def combat(self, monster_level):
        monster_symbol = self.get_monster_symbol(monster_level)
        print(f"Combat! You encountered a {monster_level} bogey ({monster_symbol}).")
        
        # calculate the number of steps based on the monster's level
        steps_cost = self.monster_levels.get(monster_level, 0)
        print(f"Attacking a {monster_level} bogey costs {steps_cost} step(s).")
        
        while True:
            action = input("Choose your action (Attack[A]/Run[R]): ").upper()
            if action == 'A':
                print(f"You attacked the {monster_level} bogey!")
                # get the number of items dropped based on monster level
                items_dropped = self.monster_levels.get(monster_level, 0)
                print(f"You obtained {items_dropped} core(s) from the {monster_level} bogey.")
                
                # deduct steps based on the monster's level
                self.steps += steps_cost
                
                return items_dropped
            elif action == 'R':
                print("You ran away from the bogey.")
                return 0  # no items dropped if the player runs away
            else:
                print("Invalid action. Try again.")

    def clear_screen(self):
        # check the operating system and use the appropriate command to clear the console
        os.system('cls' if os.name == 'nt' else 'clear')

    def get_monster_symbol(self, monster_level):
        # map monster levels to symbols
        level_symbol_map = {'Common': 'C', 'Normal': 'N', 'Rare': 'R'}
        return level_symbol_map.get(monster_level, 'M')  # default to 'M' if level is not recognized

    def get_monster_color(self, monster_symbol):
        if monster_symbol == 'C':
            return self.COLOR_YELLOW  # Common monsters in white
        elif monster_symbol == 'N':
            return self.COLOR_BLUE   # Normal monsters in blue
        elif monster_symbol == 'R':
            return self.COLOR_RED    # Rare monsters in red
        return self.COLOR_WHITE

    def print_level(self):
        self.clear_screen()  # clear console screen
        
        #print the content of a 3x3 grid centered on the player handle out of bounds
        for y in range(self.player_y - 1, self.player_y + 2):
            for x in range(self.player_x - 1, self.player_x + 2):
                if 0 <= x < self.width and 0 <= y < self.height:
                    if self.level[y][x] == 'P':
                        print(f"{self.COLOR_GREEN}P{self.COLOR_RESET}", end=" ")
                    elif self.level[y][x] in ['C', 'N', 'R']:
                        color = self.get_monster_color(self.level[y][x])
                        print(f"{color}{self.level[y][x]}{self.COLOR_RESET}", end=" ")
                    elif self.level[y][x] == '#':
                        print(f"{self.COLOR_DEFAULT}#{self.COLOR_RESET}", end=" ")
                    elif self.level[y][x] == 'I':
                        print(f"{self.COLOR_WHITE}I{self.COLOR_RESET}", end=" ")
                    elif self.level[y][x] == 'E':
                        print(f"{self.COLOR_WHITE}E{self.COLOR_RESET}", end=" ")
                    else:
                        print(" ", end=" ")
                else:
                    print(" ", end=" ")
            print()
        # ASCII art and game board width (excluding the leading and trailing " ++")
        ascii_art_width_failed = 104
        ascii_art_width_success = 113

        header = f"Steps taken: {self.steps} | Cores collected: {self.items_collected} | Steps left: {STEP_DIVIDER * self.items_collected - self.steps}"

        if self.game_state == GameState.PLAYING:
            print(f"{self.COLOR_WHITE}{header:^5}{self.COLOR_RESET}")
            border_top_bottom = f"{self.COLOR_WHITE} ++" + "-" * (self.width * 2 + 2) + "++"

        elif self.game_state == GameState.FAILED:
            print(f"{self.COLOR_RED}{header:^5}{self.COLOR_RESET}")
            border_top_bottom = f"{self.COLOR_RED} ++" + "-" * (ascii_art_width_failed + 2) + "++"

        elif self.game_state == GameState.SUCCESS: 
            print(f"{self.COLOR_GREEN}{header:^5}{self.COLOR_RESET}")
            border_top_bottom = f"{self.COLOR_GREEN} ++" + "-" * (ascii_art_width_success + 2) + "++"
        print(border_top_bottom)

        if self.game_state == GameState.FAILED:
            # ASCII Art for FAILED
            print(f"{self.COLOR_RED} ++ ███▄ ▄███▓ ██▓  ██████   ██████  ██▓ ▒█████   ███▄    █      █████▒▄▄▄       ██▓ ██▓    ▓█████ ▓█████▄   ++")
            print(f"{self.COLOR_RED} ++ ▓██▒▀█▀ ██▒▓██▒▒██    ▒ ▒██    ▒ ▓██▒▒██▒  ██▒ ██ ▀█   █    ▓██   ▒▒████▄    ▓██▒▓██▒    ▓█   ▀ ▒██▀ ██▌ ++")
            print(f"{self.COLOR_RED} ++ ▓██    ▓██░▒██▒░ ▓██▄   ░ ▓██▄   ▒██▒▒██░  ██▒▓██  ▀█ ██▒   ▒████ ░▒██  ▀█▄  ▒██▒▒██░    ▒███   ░██   █▌ ++")
            print(f"{self.COLOR_RED} ++ ▒██    ▒██ ░██░  ▒   ██▒  ▒   ██▒░██░▒██   ██░▓██▒  ▐▌██▒   ░▓█▒  ░░██▄▄▄▄██ ░██░▒██░    ▒▓█  ▄ ░▓█▄   ▌ ++")
            print(f"{self.COLOR_RED} ++ ▒██▒   ░██▒░██░▒██████▒▒▒██████▒▒░██░░ ████▓▒░▒██░   ▓██░   ░▒█░    ▓█   ▓██▒░██░░██████▒░▒████▒░▒████▓  ++")
            print(f"{self.COLOR_RED} ++ ░ ▒░   ░  ░░▓  ▒ ▒▓▒ ▒ ░▒ ▒▓▒ ▒ ░░▓  ░ ▒░▒░▒░ ░ ▒░   ▒ ▒     ▒ ░    ▒▒   ▓▒█░░▓  ░ ▒░▓  ░░░ ▒░ ░ ▒▒▓  ▒  ++")
            print(f"{self.COLOR_RED} ++ ░  ░      ░ ▒ ░░ ░▒  ░ ░░ ░▒  ░ ░ ▒ ░  ░ ▒ ▒░ ░ ░░   ░ ▒░    ░       ▒   ▒▒ ░ ▒ ░░ ░ ▒  ░ ░ ░  ░ ░ ▒  ▒  ++")
            print(f"{self.COLOR_RED} ++ ░      ░    ▒ ░░  ░  ░  ░  ░  ░   ▒ ░░ ░ ░ ▒     ░   ░ ░     ░ ░     ░   ▒    ▒ ░  ░ ░      ░    ░ ░  ░  ++")
            print(f"{self.COLOR_RED} ++        ░    ░        ░        ░   ░      ░ ░           ░                 ░  ░ ░      ░  ░   ░  ░   ░     ++")
            print(f"{self.COLOR_RED} ++                                                                                                  ░       ++")
        elif self.game_state == GameState.SUCCESS:
            # ASCII Art for SAFE
            print(f"{self.COLOR_GREEN} ++ ███    ███ ██ ███████ ███████ ██  ██████  ███    ██     ███████ ██    ██  ██████  ██████ ███████ ███████ ███████  ++")
            print(f"{self.COLOR_GREEN} ++ ████  ████ ██ ██      ██      ██ ██    ██ ████   ██     ██      ██    ██ ██      ██      ██      ██      ██       ++")
            print(f"{self.COLOR_GREEN} ++ ██ ████ ██ ██ ███████ ███████ ██ ██    ██ ██ ██  ██     ███████ ██    ██ ██      ██      █████   ███████ ███████  ++")
            print(f"{self.COLOR_GREEN} ++ ██  ██  ██ ██      ██      ██ ██ ██    ██ ██  ██ ██          ██ ██    ██ ██      ██      ██           ██      ██  ++")
            print(f"{self.COLOR_GREEN} ++ ██      ██ ██ ███████ ███████ ██  ██████  ██   ████     ███████  ██████   ██████  ██████ ███████ ███████ ███████  ++")
        
        elif self.game_state == GameState.PLAYING:
            for row in self.level:
                print(" ++ ", end="")
                for cell in row:
                    if cell == 'P':
                        print(f"{self.COLOR_GREEN}P{self.COLOR_RESET}", end=" ")
                    elif cell in ['C', 'N', 'R']:
                        color = self.get_monster_color(cell)
                        print(f"{color}{cell}{self.COLOR_RESET}", end=" ")
                    elif cell == '#':
                        print(f"{self.COLOR_DEFAULT}#{self.COLOR_RESET}", end=" ")
                    elif cell == 'I':
                        print(f"{self.COLOR_WHITE}I{self.COLOR_RESET}", end=" ")
                    elif cell == 'E':
                        print(f"{self.COLOR_WHITE}E{self.COLOR_RESET}", end=" ")
                    else:
                        print(" ", end=" ")
                print(" ++")
        print(border_top_bottom)
        
    def animate_logo(self, logo, delay=1.0):
        for frame in logo:
            self.clear_screen()
            for line in frame.split('\n'):
                print(line)
                time.sleep(delay)

    def display_rules(self):
        self.clear_screen()
        rules = """
        Welcome to Scavenger!

        Rules:
        - Navigate the map using WASD keys.
        - Collect as many cores (I) as you can.
        - Defeat bogeys (C, N, R) to gain extra cores.
        - Common bogeys yield 1 core and cost 1 step.
        - Normal bogeys yield 2 cores and cost 2 steps.
        - Rare bogeys yield 3 cores and cost 3 steps.
        - Reach the exit (E) to finish the game.
        - Be cautious! The number of steps should not exceed 3 times the cores collected.

        Legend:
        P - Player
        E - Exit
        I - Core
        C, N, R - Common, Normal, Rare bogeys
        # - Obstacle
        """
        print(rules)
        print("Press any key to exit")
        getch()
        self.game_state = self.prev_game_state

    def display_lore(self):
        self.clear_screen()
        lore = """
        You are remote-controlling a voyager drone on a perilous area of a 
        planet in search for oxygen cores. Collect as many cores as you can. 
        You can choose to engage in combat with bogeys to obtain extra cores, 
        but remember that your drone can only handle so many steps.

        PROPERTY OF THE BUREAU OF ORBITAL OBSERVATIVES AND ENFORCEMENT
        MODEL: BOEE OXE9
        MANUFACTURED IN: 2170
        FIRMWARE: NYX OS 2.08
        STATUS: STABLE (NO MAINTENANCE REQUIRED)
        """
        print(lore)
        print("Press any key to resume the game")
        getch()
        self.game_state = self.prev_game_state

    def play(self):
        self.clear_screen()
        logo_frames = [
            r"""
   ______   _______  _______  _______    _______           _______  _______ 
  (  ___ \ (  ___  )(  ___  )(  ____ \  (  ___  )|\     /|(  ____ \(  ____ )
  | (   ) )| (   ) || (   ) || (    \/  | (   ) |( \   / )| (    \/| (    )|
  | (__/ / | |   | || |   | || (__      | |   | | \ (_) / | (__    | (____)|
  |  __ (  | |   | || |   | ||  __)     | |   | |  ) _ (  |  __)   (_____ ( 
  | (  \ \ | |   | || |   | || (        | |   | | / ( ) \ | (            ) )
  | )___) )| (___) || (___) || (____/\  | (___) |( /   \ )| (____/\/\____) |
  |/ \___/ (_______)(_______/(_______/  (_______)|/     \| (_______/\_______)
                                                          
            """
        ]
        while True:
            self.clear_screen()
            scavenger = [r"""
 __        __   _                             _____     
 \ \      / /__| | ___ ___  _ __ ___   ___   |_   _|__  
  \ \ /\ / / _ \ |/ __/ _ \| '_ ` _ \ / _ \    | |/ _ \ 
   \ V  V /  __/ | (_| (_) | | | | | |  __/    | | (_) |
  __\_/\_/ \___|_|\___\___/|_| |_| |_|\___|    |_|\___/ 
 / ___|  ___ __ ___   _____ _ __   __ _  ___ _ __       
 \___ \ / __/ _` \ \ / / _ \ '_ \ / _` |/ _ \ '__|      
  ___) | (_| (_| |\ V /  __/ | | | (_| |  __/ |         
 |____/ \___\__,_| \_/ \___|_| |_|\__, |\___|_|         
                                  |___/                 
    """]
            self.animate_logo(scavenger, delay=0.02)
            time.sleep(0.2)

            menu_text = "Powered by AstraShell\n1. Read Rules (H)\n2. Read Lore (L)\n3. Deploy Drone (D)\n4. Terminate (T)"
            self.animate_text(menu_text, delay=0.02)

            option = input("Select an option: ").upper()

            if option == 'H':
                self.display_rules()
            elif option == 'L':
                self.display_lore()
            elif option == 'D':
                break
            elif option == 'T':
                print("Clearing cache...")
                time.sleep(0.5)
                print("Shutting down")
                exit()  # terminate the program
            else:
                print("Invalid option. Please try again.")

        self.animate_logo(logo_frames, delay=0.02)
        time.sleep(0.5) 
        self.animate_text("Scanning Location...", delay=0.05)
        time.sleep(1)
        self.generate_level()
        self.animate_text("Validating Drone Coordinates... ", delay=0.05)
        time.sleep(1)
        self.animate_text("Establishing Link", delay=0.05, end=False)
        self.animate_text("....", delay=0.5)
        print("Connection established.")
        time.sleep(0.5)
        self.game_state = GameState.PLAYING

        while True:
            self.items_collected = 0
            self.steps = 0
            self.monsters_defeated = 0
            self.generate_level()
            self.print_level()
         
            emergency_exit = input("Enter 'E' for emergency exit, or any other key to continue: ").upper()

            if emergency_exit == 'E':
                print("Emergency exit activated. Deploying a new drone...")
                time.sleep(1)
                continue  # new game instance

            while True:
                # check if the player reached the exit
                if self.player_x == self.exit_x and self.player_y == self.exit_y:
                    if self.steps > STEP_DIVIDER * self.items_collected:
                        self.game_state = GameState.FAILED
                    else:
                        self.game_state = GameState.SUCCESS
                        
                    self.print_level()
                    print(f"You reached the exit with {self.items_collected} core(s) while defeating {self.monsters_defeated} bogey(s) in {self.steps} steps.")

                    # check for missed items and monsters
                    missed_items = self.num_items_to_collect - self.items_collected
                    missed_monsters = len(self.monsters)

                    if missed_items > 0:
                        print(f"You missed {missed_items} core(s) on the map.")
                    if missed_monsters > 0:
                        print(f"You avoided {missed_monsters} bogey(s) on the map.")

                    if missed_items == 0 and missed_monsters == 0:
                        print("You cleared the field, well done!")
                    
                    # check for drone malfunction condition
                    if self.game_state == GameState.FAILED:  # compare with three times the initial number of items
                        print("Drone malfunctioned, all cores lost, mission failed.")
                        self.items_collected = 0
                        self.total_items_collected = 0
                        break
                    else:
                        # update the total_items_collected attribute
                        self.total_items_collected += self.items_collected
                        print(f"You collected a total of {self.total_items_collected} core(s).")
                    break

                self.print_level()

                # if there's an item at the player's location
                if self.level[self.player_y][self.player_x] == 'I':
                    print("You found a core!")
                    self.items_collected += 1
                    self.level[self.player_y][self.player_x] = '.'  # Remove the collected item from the map

                # if there's a monster at the player's location
                for monster in self.monsters:
                    if self.player_x == monster['x'] and self.player_y == monster['y']:
                        monster_level = monster['level']
                        # combat occurs if the player bumps into a monster
                        items_dropped = self.combat(monster_level)
                        self.items_collected += items_dropped

                        # remove the defeated monster from the map
                        self.level[monster['y']][monster['x']] = '.'
                        self.monsters.remove(monster)
                        self.monsters_defeated += 1

                        break  # exit the loop after encountering and defeating one monster

                move = input("Enter (W/A/S/D) to move: ").upper()

                # save the player's current position for potential use in combat
                self.prev_player_x, self.prev_player_y = self.player_x, self.player_y

                new_player_x, new_player_y = self.player_x, self.player_y

                # update player position based on input
                if move == 'W' and self.player_y > 0:
                    new_player_y -= 1
                elif move == 'A' and self.player_x > 0:
                    new_player_x -= 1
                elif move == 'S' and self.player_y < self.height - 1:
                    new_player_y += 1
                elif move == 'D' and self.player_x < self.width - 1:
                    new_player_x += 1
                else:
                    print("Invalid move. Try again.")
                    continue

                # check if the new position is not an obstacle
                if self.level[new_player_y][new_player_x] != '#':
                    # clear the old player position
                    self.level[self.player_y][self.player_x] = '.'

                    # check if there's an item at the new position
                    if self.level[new_player_y][new_player_x] == 'I':
                        print("You found a core!")
                        self.items_collected += 1
                        self.level[new_player_y][new_player_x] = '.'  # remove the collected item from the map

                    # move monsters away from the player
                    self.move_monsters()
                    self.update_player_position(new_player_x, new_player_y)
                    
                    self.steps += STEP_COST
                else:
                    print("You cannot move through obstacles. Try again.")

            exit_game = False
            while not exit_game:
                print("Mission failed. Options:")
                print("1. Redeploy drone")
                print("2. Do not redeploy")
                print("3. Show solution")
                choice = input("Choose an option (1/2/3): ")

                if choice == '1':
                    self.game_state = GameState.PLAYING
                    break
                elif choice == '2':
                    print("Until next time.")
                    exit_game = True
                elif choice == '3':
                    self.show_solution()
                    continue  # After showing solution, ask again
                else:
                    print("Invalid input. Please enter '1', '2', or '3'.")


            if exit_game:
                break

if __name__ == "__main__":
    game = RogueLikeGame(width=WIDTH, height=HEIGHT, num_items_to_collect=NUM_CORES)
    game.play()