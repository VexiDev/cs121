import random
import os
import time
from enum import Enum
import sys
import tty
import heapq
import noise
import numpy as np
import termios
import json
from collections import deque
import threading

#COLORS
COLOR_GREEN = '\033[92m'  # Green for player
COLOR_RED = '\033[91m'    # Red for rare monsters
COLOR_BLUE = '\033[96m'   # Blue for normal monsters
COLOR_YELLOW = '\033[33m' # Yellow for common monsters
COLOR_WHITE = '\033[37m'  # White for obstacles and empty spaces
COLOR_DEFAULT = '\033[90m'  # dark blue for obstacles and empty spaces
COLOR_RESET = '\033[0m'   # Reset to default color
COLOR_PINK = '\033[35m'   # Pink for items

# thresholds for level difficulties
NEWBIE_THRESHOLD = 0
JUNIOR_THRESHOLD = 3
INTERMEDIATE_THRESHOLD = 5
SENIOR_THRESHOLD = 8
EXPERT_THRESHOLD = 15

# GAME SETTINGS
# SEED
RANDOM_SEED = True
MAP_SEED = 5978315058
LEVEL_SEED = 1231314
# VALIDATION
MAX_VALIDATION_ATTEMPTS = 4

# Global variables
DIFFICULTY = "Newbie"
WIDTH, HEIGHT = 30, 30
STEP_COST, STEP_DIVIDER = 1, 4
NUM_CORES, ITEM_VALUE = 15, 1
MIN_NUM_MONSTERS, MAX_NUM_MONSTERS = 0, 0
EXIT_DISTANCE = 5

#debug - ENABLING DEBUG WILL INCREASE TIME TO GENERATE A VALID LEVEL
# display pathfinding algorithm when validating level
DEBUG_PATH = True
# display only when near exit
DEBUG_NEAR_EXIT = False 
# at what distance from the exit to display the debug map
DEBUG_EXIT_DISTANCE = 5 
# at what path length to display the debug map
DEBUG_PATH_LENGTH = 1 

def load_config(level_name):
    global WIDTH, HEIGHT
    global STEP_COST, STEP_DIVIDER
    global NUM_CORES, ITEM_VALUE
    global MIN_NUM_MONSTERS, MAX_NUM_MONSTERS
    global EXIT_DISTANCE
    global DIFFICULTY

    # Load the configuration file
    with open('config.json', 'r') as file:
        configs = json.load(file)

    # Set global variables based on the level name
    config = configs[level_name]["config"]

    width = config.get("width", 30)
    height = config.get("height", 30)
    WIDTH = width[0]
    HEIGHT = height[0]

    DIFFICULTY = level_name
    STEP_COST, STEP_DIVIDER = config.get("step_cost", 1), config.get("step_divider", 4)
    NUM_CORES, ITEM_VALUE = config.get("num_cores", 20), config.get("item_value", 1)
    MIN_NUM_MONSTERS, MAX_NUM_MONSTERS = config.get("min_num_monsters", 4), config.get("max_num_monsters", 6)
    EXIT_DISTANCE = config.get("exit_distance", 25)

def load_user_config(user):
    global WIDTH, HEIGHT

    if user.drone_range not in [1, 2, 3]:
        # Load config based on user level
        if user.level > 15:
            name = 'Expert'
        elif user.level > 8:
            name = 'Senior'
        elif user.level > 5:
            name = 'Intermediate'
        elif user.level > 3:
            name = 'Junior'
        else:
            name = 'Newbie'
        load_config(name)
        WIDTH += user.drone_range
        HEIGHT += user.drone_range
    else:
        # Load configuration for 'Newbie' level
        name = 'Newbie'
        load_config(name)

    return name

class User():
    def __init__(self, name):
        self.name = name
        self.score = 0
        self.level = 0
        self.xp = 0
        self.xp_to_next_level = 50
        self.money = 0
        self.drone_speed = 0
        self.drone_sneak = 0
        self.drone_range = 0
        self.drone_health = 0

    def level_up(self):
        self.level += 1
        self.score += 100 * self.level
        self.xp_to_next_level = self.level * 50
        if not self.xp >= self.xp_to_next_level:
            self.xp = 0
        self.money += 150 * self.level
        print(f"{COLOR_DEFAULT}\nAvailable Drone Upgrades:\n {COLOR_DEFAULT}- {COLOR_YELLOW}Speed\n {COLOR_DEFAULT}- {COLOR_YELLOW}Sneak\n {COLOR_DEFAULT}- {COLOR_YELLOW}Range\n{COLOR_DEFAULT}")
        upgrade = input(f"{COLOR_GREEN}Select an upgrade: {COLOR_YELLOW}").lower().strip()
        while upgrade not in ["speed", "sneak", "range"]:
            if upgrade == "speed":
                animate_text(f"{COLOR_GREEN}Upgrading drone speed {COLOR_YELLOW}{self.done_speed} {COLOR_GREEN}>> {COLOR_YELLOW}{self.drone_speed+1}", delay=0.1)
                self.drone_speed += 1
            elif upgrade == "sneak":
                self.drone_sneak += 1
            elif upgrade == "range":
                self.drone_range += 1
            else:
                #move cursor up 3 line and to the left
                sys.stdout.write("\033[F\033[F\033[F\033[D")
                print(f"{COLOR_RED}\nInvalid upgrade selected.{COLOR_DEFAULT}")
                upgrade = input(f"{COLOR_GREEN}Select an upgrade: {COLOR_YELLOW}").lower().strip()
        self.drone_health += 1

    def add_xp(self, xp):
        self.xp += xp
        if self.xp >= self.xp_to_next_level:
            self.level_up()

    def add_score(self, score):
        self.score += score

    def add_money(self, money):
        self.money += money

    def add_drone_speed(self, drone_speed):
        self.drone_speed += drone_speed

    def add_drone_sneak(self, drone_sneak):
        self.drone_sneak += drone_sneak

    def add_drone_range(self, drone_range):
        self.drone_range += drone_range

    def add_drone_health(self, drone_health):
        self.drone_health += drone_health

    def get_score(self):
        return self.score
    
    def get_level(self):
        return self.level
    
    def get_xp(self):
        return self.xp
    
    def get_xp_to_next_level(self):
        return self.xp_to_next_level
    
    def get_money(self):
        return self.money
    
    def get_drone_speed(self):
        return self.drone_speed
    
    def get_drone_sneak(self):
        return self.drone_sneak
    
    def get_drone_range(self):
        return self.drone_range
    
    def get_drone_health(self):
        return self.drone_health
    
    def get_stats(self):
        # open json file users.json, read stats from user with name, load stats into user object
        with open('users.json', 'r') as f:
            users = json.load(f)
            if self.name in users.keys():
                self.score = users[self.name]['score']
                self.level = users[self.name]['level']
                self.xp = users[self.name]['xp']
                self.xp_to_next_level = users[self.name]['xp_to_next_level']
                self.money = users[self.name]['money']
                self.drone_speed = users[self.name]['drone_speed']
                self.drone_sneak = users[self.name]['drone_sneak']
                self.drone_range = users[self.name]['drone_range']
                self.drone_health = users[self.name]['drone_health']
                f.close()
                return True
            else:
                users[self.name] = {}
                with open('users.json', 'w') as f:
                    json.dump(users, f)
                    f.close()
                    return False
        
    def save_stats(self, name=None, score=None, level=None, xp=None, xp_to_next_level=None, money=None, drone_speed=None, drone_sneak=None, drone_range=None, drone_health=None):
        
        name = self.name if name is None else name
        score = self.score if score is None else score
        level = self.level if level is None else level
        xp = self.xp if xp is None else xp
        xp_to_next_level = self.xp_to_next_level if xp_to_next_level is None else xp_to_next_level
        money = self.money if money is None else money
        drone_speed = self.drone_speed if drone_speed is None else drone_speed
        drone_sneak = self.drone_sneak if drone_sneak is None else drone_sneak
        drone_range = self.drone_range if drone_range is None else drone_range
        drone_health = self.drone_health if drone_health is None else drone_health
        # Open json file users.json, update stats for user with name, save stats to json file
        with open('users.json', 'r') as f:
            users = json.load(f)
            users[name]['score'] = score
            users[name]['level'] = level
            users[name]['xp'] = xp
            users[name]['xp_to_next_level'] = xp_to_next_level
            users[name]['money'] = money
            users[name]['drone_speed'] = drone_speed
            users[name]['drone_sneak'] = drone_sneak
            users[name]['drone_range'] = drone_range
            users[name]['drone_health'] = drone_health
            f.close()
            with open('users.json', 'w') as f:
                json.dump(users, f, indent=4)
                f.close()
                return True

                    


class LoadingAnimation:
    def __init__(self, message, delay=0.5):
        self.message = message
        self.delay = delay
        self.stop_animation = False
        self.thread = threading.Thread(target=self.run_animation)

    def start(self):
        self.thread.start()

    def stop(self):
        self.stop_animation = True
        self.thread.join()

    def run_animation(self):
        loading_sequence = [f'{COLOR_GREEN}–', f'{COLOR_GREEN}\\', f'{COLOR_GREEN}|', f'{COLOR_GREEN}/']
        iteration_count = 0
        while not self.stop_animation:
            sys.stdout.flush()
            for frame in loading_sequence:
                if self.stop_animation:
                    break
                sys.stdout.write('\r' + frame + ' ' + self.message)
                sys.stdout.flush()
                time.sleep(self.delay)
            iteration_count += 1
            if iteration_count == 20:
                sys.stdout.write(f'\r{self.message}{COLOR_YELLOW}Refining{COLOR_DEFAULT}\n')
                iteration_count = 0
            else:
                if self.stop_animation:
                    sys.stdout.write('\r' + self.message + f'{COLOR_GREEN}Complete{COLOR_DEFAULT}' + '\n')
                else:
                    sys.stdout.write('\r' + self.message)

class Level():
    def __init__(self, seed, map_seed, width, height):
        self.difficulty = DIFFICULTY
        self.width = width
        self.height = height
        self.num_items_to_collect = NUM_CORES
        self.monster_levels = {
            'Common': 1,
            'Normal': 2,
            'Rare': 3
        }
        self.monsters = []
        self.solution = []
        self.initial_items = 0
        self.initial_monsters = 0
        self.player_x = 0
        self.player_y = 0
        self.exit_x = 0
        self.exit_y = 0
        self.original_level = []
        self.solution_step_count = 0
        self.solution_cores_collected = 0
        self.solution_monsters_defeated = 0
        self.solution_start_x = 0
        self.solution_start_y = 0
        self.level = []
        self.seed = seed
        self.map_seed = map_seed

        #generate the level
        self.generate_level()

    def generate_noise_map(self, scale=10.0, octaves=6, persistence=0.5, lacunarity=2.0, base=0):
        world = np.zeros((self.height, self.width))
        for i in range(self.height):
            for j in range(self.width):
                world[i][j] = noise.pnoise2(i / scale, 
                                            j / scale, 
                                            octaves=octaves, 
                                            persistence=persistence, 
                                            lacunarity=lacunarity, 
                                            repeatx=self.width, 
                                            repeaty=self.height, 
                                            base=base)
        return world

    def show_solution(self):
        if not hasattr(self, 'solution') or not isinstance(self.solution, dict) or not self.solution.get('path'):
            print("No solution available.")
            return

        print(f"{COLOR_DEFAULT}Quick-Solution for coordinates {COLOR_GREEN}{self.map_seed}.0.{self.seed} {COLOR_DEFAULT}found in {COLOR_GREEN}{self.solution_step_count}{COLOR_DEFAULT} steps and collected {COLOR_GREEN}{self.solution_cores_collected}{COLOR_DEFAULT} cores.\n{COLOR_YELLOW}Remember collecting more cores and defeating more monsters will allow you to upgrade your drone!")

        path = self.solution['path']
        monster_defeats = self.solution['monster_defeats']
        item_pickups = self.solution['item_pickups']

        direction_symbols = {
            'up': '↑', 'down': '↓', 'left': '←', 'right': '→'
        }

        def get_direction(pos1, pos2):
            if pos1[0] == pos2[0]:  # Same column
                return 'down' if pos2[1] > pos1[1] else 'up'
            if pos1[1] == pos2[1]:  # Same row
                return 'right' if pos2[0] > pos1[0] else 'left'
            return None

        border_top_bottom = f"{COLOR_GREEN} ++" + "-" * (self.width * 2 + 2) + "++"
        print(border_top_bottom)

        for y in range(self.height):
            print(f"{COLOR_GREEN} ++{COLOR_RESET}", end=" ")
            for x in range(self.width):
                position = (x, y)

                if position in path:
                    pos_index = path.index(position)
                    symbol = None
                    if pos_index + 1 < len(path):
                        next_position = path[pos_index + 1]
                        direction = get_direction(position, next_position)
                        symbol = direction_symbols.get(direction)

                    if position == path[0]:
                        print(f"{COLOR_GREEN}P{COLOR_RESET}", end=" ")
                    elif position == path[-1]:
                        print(f"{COLOR_GREEN}E{COLOR_RESET}", end=" ")
                    elif any(position == defeat[0] for defeat in monster_defeats):
                        defeat_info = next(defeat for defeat in monster_defeats if defeat[0] == position)
                        print(f"{get_monster_color(defeat_info[1])}{defeat_info[1]}{COLOR_RESET}", end=" ")
                    elif position in item_pickups:
                        print(f"{COLOR_YELLOW}I{COLOR_RESET}", end=" ")
                    elif symbol:
                        print(f"{COLOR_PINK}{symbol}{COLOR_RESET}", end=" ")
                    else:
                        # Display the original level elements
                        self.display_level_element(x, y)
                else:
                    # Display the original level elements
                    self.display_level_element(x, y)

            print(f" {COLOR_GREEN}++")  # New line after each row

        print(border_top_bottom)  # Print the bottom border only once, after the loop


    def display_level_element(self, x, y):
        # This function displays the original elements of the level
        if self.level[y][x] in ['C', 'N', 'R']:
            print(f"{COLOR_DEFAULT}{self.level[y][x]}{COLOR_RESET}", end=" ")
        elif self.original_level[y][x] == '#':
            print(f"{COLOR_DEFAULT}#{COLOR_RESET}", end=" ")
        elif self.original_level[y][x] == 'I':
            print(f"{COLOR_DEFAULT}I{COLOR_RESET}", end=" ")
        else:
            print(" ", end=" ")

    def regenerate_positions(self):
        self.solution.clear()
        self.solution_step_count = 0
        self.solution_cores_collected = 0
        self.solution_monsters_defeated = 0
        self.solution_start_x = 0
        self.solution_start_y = 0
        self.monsters.clear()
        self.initial_items = 0
        self.initial_monsters = 0
        self.player_x = 0
        self.player_y = 0
        self.exit_x = 0
        self.exit_y = 0
        self.level.clear()
        
        random.seed(None)
        if RANDOM_SEED:
            self.seed = random.randint(0, 9999999999)
        else:
            pass

        random.seed(self.seed)
        # Reset the level to its original state (empty spaces and walls)
        self.level = [['#' if cell == '#' else '.' for cell in row] for row in self.original_level]

        # Clear existing monsters
        self.monsters.clear()

        # Regenerate player position
        self.player_x, self.player_y = random.choice([(x, y) for y in range(self.height) for x in range(self.width) if self.level[y][x] == '.'])
        self.level[self.player_y][self.player_x] = 'P'

        # Regenerate exit position
        while True:
            self.exit_x, self.exit_y = random.choice([(x, y) for y in range(self.height) for x in range(self.width) if self.level[y][x] == '.'])
            if abs(self.exit_x - self.player_x) + abs(self.exit_y - self.player_y) >= EXIT_DISTANCE:
                break
        self.level[self.exit_y][self.exit_x] = 'E'

        # Regenerate items
        item_positions = []
        def is_distance_maintained(new_position, existing_positions, min_distance=3):
            for position in existing_positions:
                if abs(new_position[0] - position[0]) + abs(new_position[1] - position[1]) <= min_distance - 1:
                    return False
            return True

        for _ in range(self.num_items_to_collect):
            valid_positions = [(x, y) for y in range(self.height) for x in range(self.width) 
                            if self.level[y][x] == '.' and is_distance_maintained((x, y), item_positions)]

            if valid_positions:
                item_x, item_y = random.choice(valid_positions)
                self.level[item_y][item_x] = 'I'
                item_positions.append((item_x, item_y))
            else:
                break  # Break the loop if no valid positions are left

        # Regenerate monsters
        num_monsters = random.randint(MIN_NUM_MONSTERS, MAX_NUM_MONSTERS)
        for _ in range(num_monsters):
            while True:
                monster_x, monster_y = random.choice([(x, y) for y in range(self.height) for x in range(self.width) if self.level[y][x] == '.'])
                monster_level = random.choice(list(self.monster_levels.keys()))
                if (
                    self.level[monster_y][monster_x] == '.' and
                    (monster_x != self.player_x or monster_y != self.player_y) and
                    (monster_x != self.exit_x or monster_y != self.exit_y)
                ):
                    break
            monster_symbol = get_monster_symbol(monster_level)
            self.level[monster_y][monster_x] = monster_symbol
            self.monsters.append({'x': monster_x, 'y': monster_y, 'level': monster_level, 'steps_taken': 0})

        # Update original level
        self.original_level.clear()
        self.original_level = [row[:] for row in self.level]

    def reconstruct_path(self, came_from, current):
        path = []
        while current is not None:
            path.append(current)
            current = came_from[current]
        return path[::-1]

    def generate_level(self):
        # empty spaces
        self.level = [['.' for _ in range(self.width)] for _ in range(self.height)]
        random.seed(self.map_seed)
        noise_map = self.generate_noise_map(scale=7, octaves=random.randint(3, 5), persistence=random.uniform(0.3, 0.6), lacunarity=random.uniform(1.0, 2.0), base=random.randint(0, 5))
        # noise_map = self.generate_noise_map(scale=50.0, octaves=3, persistence=0.4, lacunarity=2.0, base=self.seed)

        # Set a threshold for placing obstacles
        obstacle_threshold = 0.05  # Adjust this value as needed

        random.seed(self.seed)

        # Place obstacles based on the noise map
        for y in range(self.height):
            for x in range(self.width):
                if self.level[y][x] == '.' and noise_map[y][x] > obstacle_threshold:
                    if (x, y) != (self.player_x, self.player_y) and (x, y) != (self.exit_x, self.exit_y):
                        self.level[y][x] = '#'
                        

        # set random playercoordinates from the list of empty spaces where the player is not blocked by obstacles
        self.player_x, self.player_y = random.choice([(x, y) for y in range(self.height) for x in range(self.width) if self.level[y][x] == '.'])  
        self.level[self.player_y][self.player_x] = 'P'

        self.solution_start_x = self.player_x
        self.solution_start_y = self.player_y

        # set random player coordinates from the list of empty spaces where the player is not blocked by obstacles or the player
        while True:
            # at least 20 steps away from the player
            self.exit_x, self.exit_y = random.choice([(x, y) for y in range(self.height) for x in range(self.width) if self.level[y][x] == '.'])
            if abs(self.exit_x - self.player_x) + abs(self.exit_y - self.player_y) >= EXIT_DISTANCE:
                break

        self.level[self.exit_y][self.exit_x] = 'E'

        item_positions = []
        def is_distance_maintained(new_position, existing_positions, min_distance=3):
            for position in existing_positions:
                if abs(new_position[0] - position[0]) + abs(new_position[1] - position[1]) <= min_distance - 1:
                    return False
            return True

        for _ in range(self.num_items_to_collect):
            valid_positions = [(x, y) for y in range(self.height) for x in range(self.width) 
                            if self.level[y][x] == '.' and is_distance_maintained((x, y), item_positions)]

            if valid_positions:
                item_x, item_y = random.choice(valid_positions)
                self.level[item_y][item_x] = 'I'
                item_positions.append((item_x, item_y))
            else:
                break  # Break the loop if no valid positions are left

        # bogeys on the map with random levels in locations from the list of empty spaces where they are not blocked by obstacles, the player or the exit
        num_monsters = random.randint(MIN_NUM_MONSTERS, MAX_NUM_MONSTERS)
        for _ in range(num_monsters):
            while True:
                monster_x, monster_y = random.choice([(x, y) for y in range(self.height) for x in range(self.width) if self.level[y][x] == '.'])
                # monster level is random but weighted towards lower levels
                monster_level = random.choices(list(self.monster_levels.keys()), weights=[0.6, 0.3, 0.1])[0]

                # ensures monster is not blocked by obstacles, the player, the exit, or other monsters
                if (
                    self.level[monster_y][monster_x] == '.' and
                    (monster_x != self.player_x or monster_y != self.player_y) and
                    (monster_x != self.exit_x or monster_y != self.exit_y)
                ):
                    break

            # diff symbol diff monster
            monster_symbol = get_monster_symbol(monster_level)
            self.level[monster_y][monster_x] = monster_symbol
            self.monsters.append({'x': monster_x, 'y': monster_y, 'level': monster_level, 'steps_taken': 0})

        # record the initial number of items
        self.initial_items = sum(row.count('I') for row in self.level)
        self.initial_monsters = len(self.monsters)

        # copy self.level to self.original_level
        self.original_level = [row[:] for row in self.level]

def get_monster_level_from_symbol(symbol):
    # map symbols to monster levels
    symbol_level_map = {'C': 'Common', 'N': 'Normal', 'R': 'Rare'}
    return symbol_level_map.get(symbol, 'Common')  # default to 'Common' if symbol is not recognized


def bfs_path_exists(level, start, goal):
    queue = deque([start])
    visited = set([start])

    while queue:
        current = queue.popleft()

        if current == goal:
            return True

        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            neighbor = (current[0] + dx, current[1] + dy)
            if 0 <= neighbor[0] < level.width and 0 <= neighbor[1] < level.height:
                if level.level[neighbor[1]][neighbor[0]] != '#' and neighbor not in visited:
                    visited.add(neighbor)
                    queue.append(neighbor)

    return False

def validate_level(level, game_state, max_depth=100):
    start = (level.player_x, level.player_y)
    goal = (level.exit_x, level.exit_y)

    # Check for a possible path ignoring steps and cores
    if not bfs_path_exists(level, start, goal):
        return False

    def is_near_exit(current_position, goal_position, threshold=DEBUG_EXIT_DISTANCE):
        return manhattan_distance(current_position, goal_position) <= threshold
    
    pq = []
    heapq.heappush(pq, (0, start, 0, 0, [start], [], level.monsters.copy(), set()))
    visited = set()

    while pq:
        time.sleep(0.0000001)
        _, current, steps, cores, path, defeated_monsters, monsters, items_picked_up = heapq.heappop(pq)

        state = (current, tuple((m['x'], m['y']) for m in monsters))
        if state in visited or len(path) > max_depth:
            continue
        visited.add(state)

        updated_monsters = move_monsters(monsters.copy(), current, level.level, level.monster_levels, level.width, level.height)

        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            neighbor = (current[0] + dx, current[1] + dy)
            if 0 <= neighbor[0] < level.width and 0 <= neighbor[1] < level.height and level.level[neighbor[1]][neighbor[0]] != '#':
                # Calculating new cores based on the items and monsters defeated in the new path
                new_path = path + [neighbor]
                new_defeated_monsters = defeated_monsters.copy()
                new_monsters = updated_monsters.copy()
                new_items_picked_up = items_picked_up.copy()
                new_cores = cores
                new_steps = steps + STEP_COST

                cell_content = level.level[neighbor[1]][neighbor[0]]
                if cell_content == 'I' and neighbor not in items_picked_up:
                    new_items_picked_up.add(neighbor)
                elif cell_content in ['C', 'N', 'R']:
                    monster = next((m for m in new_monsters if m['x'] == neighbor[0] and m['y'] == neighbor[1]), None)
                    if monster:
                        monster_core_value = level.monster_levels[monster['level']]
                        # Always attack the monster
                        new_cores += monster_core_value
                        new_steps += monster_core_value  # Adding steps as per monster level
                        new_defeated_monsters.append((neighbor, cell_content))
                        new_monsters.remove(monster)

                monster_cores = sum(level.monster_levels[get_monster_level_from_symbol(defeat_info[1])] for defeat_info in new_defeated_monsters if defeat_info[0] in new_path)
                unique_item_cores = len(new_items_picked_up) * ITEM_VALUE

                new_cores = monster_cores + unique_item_cores

                # Heuristic calculation that makes the pathfinding algorithm greedy in this order monsters > items > exit
                # monster_reward = 0
                # for monster in new_monsters:
                #     distance_to_monster = manhattan_distance(neighbor, (monster['x'], monster['y']))
                #     monster_core_value = level.monster_levels[monster['level']]
                #     monster_reward += monster_core_value / (distance_to_monster + 1)

                # unpicked_item_count = sum(1 for y in range(level.height) for x in range(level.width)
                #                         if level.level[y][x] == 'I' and (x, y) not in new_items_picked_up)
                # heuristic = manhattan_distance(neighbor, goal) - new_cores + unpicked_item_count - monster_reward


                # Heuristic calculation that makes the pathfinding algorithm greedy in this order items > exit
                # unpicked_item_count = sum(1 for y in range(level.height) for x in range(level.width)
                #         if level.level[y][x] == 'I' and (x, y) not in new_items_picked_up)
                # heuristic = manhattan_distance(neighbor, goal) - new_cores + unpicked_item_count            


                # Heuristic calculation that makes the pathfinding algorithm focus on the exit and only the exit
                heuristic = manhattan_distance(neighbor, goal)

                if current == goal and cores * STEP_DIVIDER >= steps:
                    if DEBUG_PATH and game_state == GameState.PLAYING:
                        print(f"{COLOR_GREEN}At exit. Cores: {cores}, Steps: {steps}, Win Max: {cores * STEP_DIVIDER}")
                        time.sleep(1)
                    level.solution = {
                        'path': path,
                        'monster_defeats': defeated_monsters,
                        'item_pickups': list(items_picked_up)
                    }
                    level.solution_step_count = steps
                    level.solution_cores_collected = cores
                    return True

                if new_cores * STEP_DIVIDER >= new_steps:
                    # Push the updated monsters state along with other path information
                    heapq.heappush(pq, (heuristic, neighbor, new_steps, new_cores, new_path, new_defeated_monsters, new_monsters, new_items_picked_up))

        #print level to console
        if DEBUG_PATH and (not DEBUG_NEAR_EXIT or (DEBUG_NEAR_EXIT and is_near_exit(current, goal))) and steps > DEBUG_PATH_LENGTH and game_state == GameState.PLAYING:
            print("\033[H", end="")
            map_string = ""
            for y in range(level.height):
                for x in range(level.width):
                    if (x, y) == current:
                        map_string += f"{COLOR_GREEN}P{COLOR_RESET} "
                    elif (x, y) == goal:
                        map_string += f"{COLOR_GREEN}E{COLOR_RESET} "
                    elif any((x, y) == defeat[0] for defeat in defeated_monsters):
                        defeat_info = next(defeat for defeat in defeated_monsters if defeat[0] == (x, y))
                        map_string += f"{get_monster_color(defeat_info[1])}{defeat_info[1]}{COLOR_RESET} "
                    elif (x, y) in path and level.level[y][x] == 'I':
                        map_string += f"{COLOR_YELLOW}I{COLOR_RESET} "
                    elif (x, y) in path:
                        map_string += f"{COLOR_PINK}•{COLOR_RESET} "
                    elif (x, y) in [(m['x'], m['y']) for m in monsters]:
                        monster = next((m for m in monsters if m['x'] == x and m['y'] == y), None)
                        if monster:
                            monster_symbol = get_monster_symbol(monster['level'])
                            map_string += f"{COLOR_DEFAULT}{monster_symbol}{COLOR_RESET} "
                    elif level.level[y][x] == '#':
                        map_string += f"{COLOR_DEFAULT}#{COLOR_RESET} "
                    elif level.level[y][x] == 'I':
                        map_string += f"{COLOR_DEFAULT}I{COLOR_RESET} "
                    else:
                        map_string += "  "
                map_string += "\n"
            print(f"{map_string}"
                f"---Level Data---{' ' * 50}\n"
                f"Map Size: {level.width}x{level.height}{' ' * 50}\n"
                f"Current map seed: {level.map_seed}{' ' * 50}\n"
                f"Current level seed: {level.seed}{' ' * 50}\n"
                f"Monsters remaining: {len(monsters)}{' ' * 50}\n"
                f"Items remaining: {level.num_items_to_collect - len(items_picked_up)}{' ' * 50}\n"
                f"---Validation Data---{' ' * 50}\n"
                f"Current depth: {len(path)}{' ' * 50}\n"
                f"Max depth: {max_depth}{' ' * 50}\n"
                f"---Algorithm Data---{' ' * 50}\n"
                f"Current position: {current}{' ' * 50}\n"
                f"Current steps: {steps}{' ' * 50}\n"
                f"Current cores: {cores}{' ' * 50}\n"
                f"Monster defeats: {len(defeated_monsters)}{' ' * 50}\n"
                f"Items picked up: {len(items_picked_up)}{' ' * 50}\n"
                f"---Game Settings---{' ' * 50}\n"
                f"Difficulty: {DIFFICULTY}{' ' * 50}\n"
                f"Step cost: {STEP_COST}{' ' * 50}\n"
                f"Step divider: {STEP_DIVIDER}{' ' * 50}\n"
                f"Item value: {ITEM_VALUE}{' ' * 50}\n"
                f"Min monsters: {MIN_NUM_MONSTERS}{' ' * 50}\n"
                f"Max monsters: {MAX_NUM_MONSTERS}{' ' * 50}\n"
                f"Total cores: {NUM_CORES}{' ' * 50}\n"
                f"Exit distance: {EXIT_DISTANCE}{' ' * 50}\n"
                f"---------------{' ' * 50}\n\n", end="")
            sys.stdout.flush()

            time.sleep(0.001) 
    return False

def manhattan_distance(point_a, point_b):
    return abs(point_a[0] - point_b[0]) + abs(point_a[1] - point_b[1])



def move_monsters(monsters, player_pos, level, monster_levels, width, height):
    new_monsters = []
    occupied_positions = {(m['x'], m['y']) for m in monsters}

    for monster in monsters:
        if is_monster_active(monster, player_pos, monster_levels):
            fatigue_limit = get_fatigue_limit(monster['level'])
            if monster['steps_taken'] < fatigue_limit:
                move_options = get_move_options(monster, player_pos, occupied_positions, level, width, height)
                if move_options:
                    move_direction = random.choice(move_options)
                    execute_monster_move(monster, move_direction, player_pos, level)
                    monster['steps_taken'] += 1
            else:
                monster['steps_taken'] = 0
        new_monsters.append(monster)

    return new_monsters


def execute_monster_move(monster, move_direction, player_pos, level):
    new_x, new_y = monster['x'] + move_direction[0], monster['y'] + move_direction[1]
    if (new_x, new_y) != player_pos:
        level[monster['y']][monster['x']] = '.'
        level[new_y][new_x] = get_monster_symbol(monster['level'])
        monster['x'], monster['y'] = new_x, new_y

def get_fatigue_limit(monster_level):
    if monster_level == 'Common':
        return random.randint(1, 2)
    elif monster_level == 'Normal':
        return random.randint(2, 4)
    elif monster_level == 'Rare':
        return random.randint(3,5)


def get_move_options(monster, player_pos, occupied_positions, level, width, height):
    move_options = []
    player_x, player_y = player_pos

    # Directions where the monster can move
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

    for dx, dy in directions:
        new_x, new_y = monster['x'] + dx, monster['y'] + dy
        # Check if the new position is adjacent to the player
        if (new_x, new_y) == (player_x, player_y):
            continue  # Skip this option if it's next to the player

        # Check if the new position is valid for movement
        if 0 <= new_x < width and 0 <= new_y < height and level[new_y][new_x] == '.' and (new_x, new_y) not in occupied_positions:
            move_options.append((dx, dy))

    return move_options


def is_monster_active(monster, player_pos, monster_levels):
    proximity = calculate_proximity(monster, player_pos)
    move_frequency = monster_levels.get(monster['level'], 1)
    return proximity <= 2*move_frequency

def calculate_proximity(monster, player_pos):
    return abs(monster['x'] - player_pos[0]) + abs(monster['y'] - player_pos[1])

def animate_text(text, delay=0.1, end=True):
    for char in text:
        print(char, end='', flush=True)
        time.sleep(delay)
    if end:
        print()

def combat(monster_level, monster_levels):
    monster_symbol = get_monster_symbol(monster_level)
    print(f"Combat! You encountered a {monster_level} bogey ({monster_symbol}).")
    steps_cost = monster_levels.get(monster_level, 0)
    print(f"Attacking a {monster_level} bogey costs {steps_cost} step(s).")
    while True:
        action = input("Choose your action (Attack[A]/Run[R]): ").upper()
        if action == 'A':
            print(f"You attacked the {monster_level} bogey!")
            items_dropped = monster_levels.get(monster_level, 0)
            print(f"You obtained {items_dropped} core(s) from the {monster_level} bogey.")
            return items_dropped, steps_cost
        elif action == 'R':
            print("You ran away from the bogey.")
            return 0, 0
        else:
            print("Invalid action. Try again.")

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def get_monster_symbol(monster_level):
    level_symbol_map = {'Common': 'C', 'Normal': 'N', 'Rare': 'R'}
    return level_symbol_map.get(monster_level)

def get_monster_color(monster_symbol):
    if monster_symbol == 'C':
        return COLOR_YELLOW
    elif monster_symbol == 'N':
        return COLOR_BLUE
    elif monster_symbol == 'R':
        return COLOR_RED
    return COLOR_WHITE

def print_level(level, game_state, steps, items_collected, min_steps_needed, width):
    clear_screen()  # clear console screen

    scavenger_logo= r"""
   ▄████████  ▄████████    ▄████████  ▄█    █▄     ▄████████ ███▄▄▄▄      ▄██████▄     ▄████████    ▄████████ 
  ███    ███ ███    ███   ███    ███ ███    ███   ███    ███ ███▀▀▀██▄   ███    ███   ███    ███   ███    ███ 
  ███    █▀  ███    █▀    ███    ███ ███    ███   ███    █▀  ███   ███   ███    █▀    ███    █▀    ███    ███ 
  ███        ███          ███    ███ ███    ███  ▄███▄▄▄     ███   ███  ▄███         ▄███▄▄▄      ▄███▄▄▄▄██▀ 
▀███████████ ███        ▀███████████ ███    ███ ▀▀███▀▀▀     ███   ███ ▀▀███ ████▄  ▀▀███▀▀▀     ▀▀███▀▀▀▀▀   
         ███ ███    █▄    ███    ███ ███    ███   ███    █▄  ███   ███   ███    ███   ███    █▄  ▀███████████ 
   ▄█    ███ ███    ███   ███    ███ ███    ███   ███    ███ ███   ███   ███    ███   ███    ███   ███    ███ 
 ▄████████▀  ████████▀    ███    █▀   ▀██████▀    ██████████  ▀█   █▀    ████████▀    ██████████   ███    ███ 
"""
    print(f"{COLOR_GREEN}{scavenger_logo}")
    # print(seed)
    #print the content of a 3x3 grid centered on the player handling out of bounds
    # for y in range(player_y - 1, player_y + 2):
    #     for x in range(player_x - 1, player_x + 2):
    #         if 0 <= x < WIDTH and 0 <= y < HEIGHT:
    #             if level[y][x] == 'P':
    #                 print(f"{COLOR_GREEN}P{COLOR_RESET}", end=" ")
    #             elif level[y][x] in ['C', 'N', 'R']:
    #                 color = get_monster_color(level[y][x])
    #                 print(f"{color}{level[y][x]}{COLOR_RESET}", end=" ")
    #             elif level[y][x] == '#':
    #                 print(f"{COLOR_DEFAULT}#{COLOR_RESET}", end=" ")
    #             elif level[y][x] == 'I':
    #                 print(f"{COLOR_WHITE}I{COLOR_RESET}", end=" ")
    #             elif level[y][x] == 'E':
    #                 print(f"{COLOR_GREEN}E{COLOR_RESET}", end=" ")
    #             else:
    #                 print(" ", end=" ")
    #         else:
    #             print(" ", end=" ")
    #     print()

    # ASCII art and game board width (excluding the leading and trailing " ++")
    ascii_art_width_failed = 104
    ascii_art_width_success = 100

    if game_state == GameState.PLAYING:
        print(f"                 {COLOR_GREEN}Steps taken: {steps} | Cores collected: {items_collected} | Win Gap: {STEP_DIVIDER * items_collected - steps:+} | Possible in {min_steps_needed} steps")
        border_top_bottom = f"          {COLOR_GREEN} ++" + "-" * (width * 2 + 2) + "++"

    elif game_state == GameState.FAILED:
        print(f"                 {COLOR_RED}Steps taken: {steps} | Cores collected: {items_collected} | Win Gap: {STEP_DIVIDER * items_collected - steps:+} | Possible in {min_steps_needed} steps")
        border_top_bottom = f"{COLOR_RED} ++" + "-" * (ascii_art_width_failed + 2) + "++"

    elif game_state == GameState.SUCCESS: 
        print(f"                 {COLOR_GREEN}Steps taken: {steps} | Cores collected: {items_collected} | Win Gap: {STEP_DIVIDER * items_collected - steps:+} | Possible in {min_steps_needed} steps")
        border_top_bottom = f"{COLOR_GREEN} ++" + "-" * (ascii_art_width_success + 2) + "++"
    print(border_top_bottom)

    if game_state == GameState.FAILED:
        # ASCII Art for FAILED
        print(f"{COLOR_RED} ++ ███▄ ▄███▓ ██▓  ██████   ██████  ██▓ ▒█████   ███▄    █      █████▒▄▄▄       ██▓ ██▓    ▓█████ ▓█████▄   ++")
        print(f"{COLOR_RED} ++ ▓██▒▀█▀ ██▒▓██▒▒██    ▒ ▒██    ▒ ▓██▒▒██▒  ██▒ ██ ▀█   █    ▓██   ▒▒████▄    ▓██▒▓██▒    ▓█   ▀ ▒██▀ ██▌ ++")
        print(f"{COLOR_RED} ++ ▓██    ▓██░▒██▒░ ▓██▄   ░ ▓██▄   ▒██▒▒██░  ██▒▓██  ▀█ ██▒   ▒████ ░▒██  ▀█▄  ▒██▒▒██░    ▒███   ░██   █▌ ++")
        print(f"{COLOR_RED} ++ ▒██    ▒██ ░██░  ▒   ██▒  ▒   ██▒░██░▒██   ██░▓██▒  ▐▌██▒   ░▓█▒  ░░██▄▄▄▄██ ░██░▒██░    ▒▓█  ▄ ░▓█▄   ▌ ++")
        print(f"{COLOR_RED} ++ ▒██▒   ░██▒░██░▒██████▒▒▒██████▒▒░██░░ ████▓▒░▒██░   ▓██░   ░▒█░    ▓█   ▓██▒░██░░██████▒░▒████▒░▒████▓  ++")
        print(f"{COLOR_RED} ++ ░ ▒░   ░  ░░▓  ▒ ▒▓▒ ▒ ░▒ ▒▓▒ ▒ ░░▓  ░ ▒░▒░▒░ ░ ▒░   ▒ ▒     ▒ ░    ▒▒   ▓▒█░░▓  ░ ▒░▓  ░░░ ▒░ ░ ▒▒▓  ▒  ++")
        print(f"{COLOR_RED} ++ ░  ░      ░ ▒ ░░ ░▒  ░ ░░ ░▒  ░ ░ ▒ ░  ░ ▒ ▒░ ░ ░░   ░ ▒░    ░       ▒   ▒▒ ░ ▒ ░░ ░ ▒  ░ ░ ░  ░ ░ ▒  ▒  ++")
        print(f"{COLOR_RED} ++ ░      ░    ▒ ░░  ░  ░  ░  ░  ░   ▒ ░░ ░ ░ ▒     ░   ░ ░     ░ ░     ░   ▒    ▒ ░  ░ ░      ░    ░ ░  ░  ++")
        print(f"{COLOR_RED} ++        ░    ░        ░        ░   ░      ░ ░           ░                 ░  ░ ░      ░  ░   ░  ░   ░     ++")
        print(f"{COLOR_RED} ++                                                                                                  ░       ++")
    elif game_state == GameState.SUCCESS:
        # # ASCII Art for SAFE
        # print(f"{COLOR_GREEN} ++ ███    ███ ██ ███████ ███████ ██  ██████  ███    ██     ███████ ██    ██  ██████  ██████ ███████ ███████ ███████  ++")
        # print(f"{COLOR_GREEN} ++ ████  ████ ██ ██      ██      ██ ██    ██ ████   ██     ██      ██    ██ ██      ██      ██      ██      ██       ++")
        # print(f"{COLOR_GREEN} ++ ██ ████ ██ ██ ███████ ███████ ██ ██    ██ ██ ██  ██     ███████ ██    ██ ██      ██      █████   ███████ ███████  ++")
        # print(f"{COLOR_GREEN} ++ ██  ██  ██ ██      ██      ██ ██ ██    ██ ██  ██ ██          ██ ██    ██ ██      ██      ██           ██      ██  ++")
        # print(f"{COLOR_GREEN} ++ ██      ██ ██ ███████ ███████ ██  ██████  ██   ████     ███████  ██████   ██████  ██████ ███████ ███████ ███████  ++")
        print(f"{COLOR_GREEN} ++ ___  ___ _____  _____  _____  _____  _____  _   _   _____  _   _  _____  _____  _____  _____  _____  ++")
        print(f"{COLOR_GREEN} ++ |  \/  ||_   _|/  ___|/  ___||_   _||  _  || \ | | /  ___|| | | |/  __ \/  __ \|  ___|/  ___|/  ___| ++")
        print(f"{COLOR_GREEN} ++ | .  . |  | |  \ `--. \ `--.   | |  | | | ||  \| | \ `--. | | | || /  \/| /  \/| |__  \ `--. \ `--.  ++")
        print(f"{COLOR_GREEN} ++ | |\/| |  | |   `--. \ `--. \  | |  | | | || . ` |  `--. \| | | || |    | |    |  __|  `--. \ `--. \ ++")
        print(f"{COLOR_GREEN} ++ | |  | | _| |_ /\__/ //\__/ / _| |_ \ \_/ /| |\  | /\__/ /| |_| || \__/\| \__/\| |___ /\__/ //\__/ / ++")
        print(f"{COLOR_GREEN} ++ \_|  |_/ \___/ \____/ \____/  \___/  \___/ \_| \_/ \____/  \___/  \____/ \____/\____/ \____/ \____/  ++")
    
    elif game_state == GameState.PLAYING:
        for row in level:
            print(f"{COLOR_GREEN}           ++ {COLOR_RESET}", end="")
            for cell in row:
                if cell == 'P':
                    print(f"{COLOR_GREEN}P{COLOR_RESET}", end=" ")
                elif cell in ['C', 'N', 'R']:
                    color = get_monster_color(cell)
                    print(f"{color}{cell}{COLOR_RESET}", end=" ")
                elif cell == '#':
                    print(f"{COLOR_DEFAULT}#{COLOR_RESET}", end=" ")
                elif cell == 'I':
                    print(f"{COLOR_WHITE}I{COLOR_RESET}", end=" ")
                elif cell == 'E':
                    print(f"{COLOR_GREEN}E{COLOR_RESET}", end=" ")
                else:
                    print(" ", end=" ")
            print(f" {COLOR_GREEN}++")
    print(border_top_bottom + COLOR_RESET)

def animate_logo(logo, color="", delay=1.0):
    for frame in logo:
        clear_screen()
        for line in frame.split('\n'):
            print(f"{color}{line}")
            time.sleep(delay)

def display_rules():
    scavenger_welcome_logo = [r"""
██╗    ██╗███████╗██╗      ██████╗ ██████╗ ███╗   ███╗███████╗    ████████╗ ██████╗     
██║    ██║██╔════╝██║     ██╔════╝██╔═══██╗████╗ ████║██╔════╝    ╚══██╔══╝██╔═══██╗    
██║ █╗ ██║█████╗  ██║     ██║     ██║   ██║██╔████╔██║█████╗         ██║   ██║   ██║    
██║███╗██║██╔══╝  ██║     ██║     ██║   ██║██║╚██╔╝██║██╔══╝         ██║   ██║   ██║    
╚███╔███╔╝███████╗███████╗╚██████╗╚██████╔╝██║ ╚═╝ ██║███████╗       ██║   ╚██████╔╝    
 ╚══╝╚══╝ ╚══════╝╚══════╝ ╚═════╝ ╚═════╝ ╚═╝     ╚═╝╚══════╝       ╚═╝    ╚═════╝     
███████╗ ██████╗ █████╗ ██╗   ██╗███████╗███╗   ██╗ ██████╗ ███████╗██████╗     ██████╗ 
██╔════╝██╔════╝██╔══██╗██║   ██║██╔════╝████╗  ██║██╔════╝ ██╔════╝██╔══██╗    ╚════██╗
███████╗██║     ███████║██║   ██║█████╗  ██╔██╗ ██║██║  ███╗█████╗  ██████╔╝     █████╔╝
╚════██║██║     ██╔══██║╚██╗ ██╔╝██╔══╝  ██║╚██╗██║██║   ██║██╔══╝  ██╔══██╗    ██╔═══╝ 
███████║╚██████╗██║  ██║ ╚████╔╝ ███████╗██║ ╚████║╚██████╔╝███████╗██║  ██║    ███████╗
╚══════╝ ╚═════╝╚═╝  ╚═╝  ╚═══╝  ╚══════╝╚═╝  ╚═══╝ ╚═════╝ ╚══════╝╚═╝  ╚═╝    ╚══════╝     
    """]
    clear_screen()
    rules = f"""{COLOR_DEFAULT}
    Rules:
    - Navigate the map using {COLOR_PINK}WASD{COLOR_DEFAULT} keys.
    - Collect as many cores {COLOR_PINK}(I){COLOR_DEFAULT} as you can.
    - Defeat bogeys {COLOR_PINK}(C, N, R){COLOR_DEFAULT} to gain extra cores.
    - Reach the exit {COLOR_PINK}(E){COLOR_DEFAULT} to finish the game.
    - {COLOR_RED}Be cautious!{COLOR_DEFAULT} The number of steps should not exceed {COLOR_PINK}{STEP_DIVIDER} times{COLOR_DEFAULT} the cores collected.

    Legend:
    {COLOR_GREEN}P{COLOR_DEFAULT} - Player
    {COLOR_GREEN}E{COLOR_DEFAULT} - Exit
    {COLOR_WHITE}I{COLOR_DEFAULT} - Core
    {COLOR_YELLOW}C{COLOR_DEFAULT}, {COLOR_BLUE}N{COLOR_DEFAULT}, {COLOR_RED}R{COLOR_DEFAULT} - Common, Normal, Rare bogeys
    # - Obstacle
    """
    animate_logo(scavenger_welcome_logo, color=COLOR_GREEN, delay=0.01)
    print(rules)
    print(f"{COLOR_PINK}Press any key to exit")
    getch()


def display_lore():
    scavenger_welcome_logo = [r"""
██╗    ██╗███████╗██╗      ██████╗ ██████╗ ███╗   ███╗███████╗    ████████╗ ██████╗     
██║    ██║██╔════╝██║     ██╔════╝██╔═══██╗████╗ ████║██╔════╝    ╚══██╔══╝██╔═══██╗    
██║ █╗ ██║█████╗  ██║     ██║     ██║   ██║██╔████╔██║█████╗         ██║   ██║   ██║    
██║███╗██║██╔══╝  ██║     ██║     ██║   ██║██║╚██╔╝██║██╔══╝         ██║   ██║   ██║    
╚███╔███╔╝███████╗███████╗╚██████╗╚██████╔╝██║ ╚═╝ ██║███████╗       ██║   ╚██████╔╝    
 ╚══╝╚══╝ ╚══════╝╚══════╝ ╚═════╝ ╚═════╝ ╚═╝     ╚═╝╚══════╝       ╚═╝    ╚═════╝     
███████╗ ██████╗ █████╗ ██╗   ██╗███████╗███╗   ██╗ ██████╗ ███████╗██████╗     ██████╗ 
██╔════╝██╔════╝██╔══██╗██║   ██║██╔════╝████╗  ██║██╔════╝ ██╔════╝██╔══██╗    ╚════██╗
███████╗██║     ███████║██║   ██║█████╗  ██╔██╗ ██║██║  ███╗█████╗  ██████╔╝     █████╔╝
╚════██║██║     ██╔══██║╚██╗ ██╔╝██╔══╝  ██║╚██╗██║██║   ██║██╔══╝  ██╔══██╗    ██╔═══╝ 
███████║╚██████╗██║  ██║ ╚████╔╝ ███████╗██║ ╚████║╚██████╔╝███████╗██║  ██║    ███████╗
╚══════╝ ╚═════╝╚═╝  ╚═╝  ╚═══╝  ╚══════╝╚═╝  ╚═══╝ ╚═════╝ ╚══════╝╚═╝  ╚═╝    ╚══════╝        
    """]
    clear_screen()
    lore = f"""{COLOR_DEFAULT}
    You are remote-controlling a voyager drone on a perilous area of a 
    planet in search for oxygen cores. Collect as many cores as you can. 
    You can choose to engage in combat with bogeys to obtain extra cores, 
    but remember that your drone can only handle so many steps.

    \033[1m{COLOR_YELLOW}PROPERTY OF THE BUREAU OF ORBITAL OBSERVATIVES AND ENFORCEMENT{COLOR_RESET}{COLOR_YELLOW}
    MODEL: BOEE OXE9
    MANUFACTURED IN: 2170
    FIRMWARE: NYX OS 2.08
    STATUS: STABLE (NO MAINTENANCE REQUIRED)
    """
    animate_logo(scavenger_welcome_logo, color=COLOR_GREEN, delay=0.01)
    print(lore)
    print(f"{COLOR_PINK}Press any key to resume the game")
    getch()


class GameState(Enum):
    STARTUP = 0
    PLAYING = 1
    VIEWING_RULES = 2
    VIEWING_LORE = 3
    SUCCESS = 4
    FAILED = 5
    MAIN_MENU = 6
    SELECTING_DIFFICULTY = 7
    BACKGROUND_TASK = 8


def getch():
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(sys.stdin.fileno())
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch

# Main function
def main(game_state, user=None):
    difficulty_levels = {
        'Newbie': 1,
        'Junior': 2,
        'Intermediate': 3,
        'Senior': 4,
        'Expert': 5
    }
    logo_frames = [
            r"""
  _____                             _______                      _                _ 
 |  __ \                           |__   __|                    (_)              | |
 | |  | | _ __  ___   _ __    ___     | |  ___  _ __  _ __ ___   _  _ __    __ _ | |
 | |  | || '__|/ _ \ | '_ \  / _ \    | | / _ \| '__|| '_ ` _ \ | || '_ \  / _` || |
 | |__| || |  | (_) || | | ||  __/    | ||  __/| |   | | | | | || || | | || (_| || |
 |_____/ |_|   \___/ |_| |_| \___|    |_| \___||_|   |_| |_| |_||_||_| |_| \__,_||_|
  ______  ______  ______  ______  ______  ______  ______  ______  ______  ______    
 |______||______||______||______||______||______||______||______||______||______|   
            ____    ___    ___   ______    ___         ______  ___                  
           |  _ \  / _ \  / _ \ |  ____|  / _ \       |  ____|/ _ \                 
           | |_) || | | || | | || |__    | | | |__  __| |__  | (_) |                
           |  _ < | | | || | | ||  __|   | | | |\ \/ /|  __|  \__, |                
           | |_) || |_| || |_| || |____  | |_| | >  < | |____   / /                 
           |____/  \___/  \___/ |______|  \___/ /_/\_\|______| /_/                  
                                                                                                                                                                                                      
 """
        ]
    scavenger_welcome_logo = [r"""
██╗    ██╗███████╗██╗      ██████╗ ██████╗ ███╗   ███╗███████╗    ████████╗ ██████╗     
██║    ██║██╔════╝██║     ██╔════╝██╔═══██╗████╗ ████║██╔════╝    ╚══██╔══╝██╔═══██╗    
██║ █╗ ██║█████╗  ██║     ██║     ██║   ██║██╔████╔██║█████╗         ██║   ██║   ██║    
██║███╗██║██╔══╝  ██║     ██║     ██║   ██║██║╚██╔╝██║██╔══╝         ██║   ██║   ██║    
╚███╔███╔╝███████╗███████╗╚██████╗╚██████╔╝██║ ╚═╝ ██║███████╗       ██║   ╚██████╔╝    
 ╚══╝╚══╝ ╚══════╝╚══════╝ ╚═════╝ ╚═════╝ ╚═╝     ╚═╝╚══════╝       ╚═╝    ╚═════╝     
███████╗ ██████╗ █████╗ ██╗   ██╗███████╗███╗   ██╗ ██████╗ ███████╗██████╗     ██████╗ 
██╔════╝██╔════╝██╔══██╗██║   ██║██╔════╝████╗  ██║██╔════╝ ██╔════╝██╔══██╗    ╚════██╗
███████╗██║     ███████║██║   ██║█████╗  ██╔██╗ ██║██║  ███╗█████╗  ██████╔╝     █████╔╝
╚════██║██║     ██╔══██║╚██╗ ██╔╝██╔══╝  ██║╚██╗██║██║   ██║██╔══╝  ██╔══██╗    ██╔═══╝ 
███████║╚██████╗██║  ██║ ╚████╔╝ ███████╗██║ ╚████║╚██████╔╝███████╗██║  ██║    ███████╗
╚══════╝ ╚═════╝╚═╝  ╚═╝  ╚═══╝  ╚══════╝╚═╝  ╚═══╝ ╚═════╝ ╚══════╝╚═╝  ╚═╝    ╚══════╝            
    """]

    # Main game loop
    while True:
        clear_screen()
        if game_state == GameState.STARTUP:
            #ask user to enter name
            name = input(f"{COLOR_DEFAULT}Please enter your name: {COLOR_GREEN}")
            #if name is empty, ask again
            while name == "":
                print(f"{COLOR_RED}Name cannot be empty")
                name = input(f"{COLOR_DEFAULT}Please enter your name: {COLOR_GREEN}")
            #if name is not empty, create user object with name and check if user exists
            user = User(name)
            if user.get_stats():
                clear_screen()
                animate_text(f"{COLOR_DEFAULT}Welcome back,{COLOR_GREEN} {user.name}{COLOR_DEFAULT}", delay=0.05)
                time.sleep(1)
                game_state = GameState.MAIN_MENU
                clear_screen()
            else:
                clear_screen()
                animate_text(f"{COLOR_DEFAULT}Welcome, {COLOR_GREEN}{user.name}{COLOR_DEFAULT}", delay=0.05)
                user.save_stats(drone_range=1, drone_speed=1, drone_sneak=1)
                time.sleep(1)
                game_state = GameState.PLAYING
                clear_screen()

        if game_state == GameState.MAIN_MENU:
            user.get_stats()
            user_level_name = load_user_config(user)
            # Check if level up is possible
            if user.xp >= user.xp_to_next_level:
                clear_screen()
                animate_text(f"{COLOR_GREEN}Congratulations! {COLOR_DEFAULT}You have leveled up to level {COLOR_GREEN}{user.level+1}{COLOR_DEFAULT}", delay=0.02)
                time.sleep(1)
                user.level_up()
                    
                user.save_stats(xp=user.xp, level=user.level, xp_to_next_level=user.xp_to_next_level, 
                                money=user.money, drone_speed=user.drone_speed, 
                                drone_sneak=user.drone_sneak, drone_range=user.drone_range, 
                                drone_health=user.drone_health)
            
                time.sleep(1)
                clear_screen()
            # Main menu
            animate_logo(scavenger_welcome_logo, color=COLOR_GREEN, delay=0.02)
            time.sleep(0.5)
            # Calculate the maximum width needed for the first column
            max_width = max(len(f"Name: {user.name}")+ 5,
                            len(f"Score: {user.score}")+ 5,
                            len(f"Level: {user.level}")+ 5,
                            len(f"XP: {user.xp}")+ 5,
                            len(f"1UP at: {user.xp_to_next_level}")+ 5,
                            len(f"Money: {user.money}")) + 5  

            # Calculate the maximum length of stat labels
            stat_labels = ["Name:", "Score:", "Level:", "XP:", "1UP at:", "Money:"]
            max_label_length = max(len(label) for label in stat_labels)

            # Display stats with consistent gap
            print(f"{COLOR_DEFAULT}---- {COLOR_BLUE}{user_level_name}{COLOR_DEFAULT} ----{' ' * (max_width - 14)}----- {COLOR_YELLOW}Drone{COLOR_DEFAULT} -----")
            print(f"{COLOR_DEFAULT}{stat_labels[0]:>{max_label_length}}{COLOR_BLUE} {user.name}{' ' * (max_width - len(f'{stat_labels[0]} {user.name}'))}{COLOR_DEFAULT}  Speed: {COLOR_YELLOW}Tier {user.drone_speed}")
            print(f"{COLOR_DEFAULT}{stat_labels[1]:>{max_label_length}}{COLOR_BLUE} {user.score}{' ' * (max_width - len(f'{stat_labels[1]} {user.score}'))}{COLOR_DEFAULT}   Sneak: {COLOR_YELLOW}Tier {user.drone_sneak}")
            print(f"{COLOR_DEFAULT}{stat_labels[2]:>{max_label_length}}{COLOR_BLUE} {user.level}{' ' * (max_width - len(f'{stat_labels[2]} {user.level}'))}{COLOR_DEFAULT}   Range: {COLOR_YELLOW}Tier {user.drone_range}")
            print(f"{COLOR_DEFAULT}{stat_labels[3]:>{max_label_length}}{COLOR_BLUE} {user.xp}{' ' * (max_width - len(f'{stat_labels[3]} {user.xp}')-2)}{COLOR_DEFAULT}-----------------")
            print(f"{COLOR_DEFAULT}{stat_labels[4]:>{max_label_length}}{COLOR_BLUE} {user.xp_to_next_level}{' ' * (max_width - len(f'{stat_labels[4]} {user.xp_to_next_level}'))}")
            print(f"{COLOR_DEFAULT}{stat_labels[5]:>{max_label_length}}{COLOR_BLUE} {user.money}{' ' * (max_width - len(f'{stat_labels[5]} {user.money}'))}\n{COLOR_DEFAULT}----------------\n")

            menu_text = f"{COLOR_DEFAULT}Powered by {COLOR_PINK}AstraShell{COLOR_DEFAULT}\n - Read Rules {COLOR_PINK}(H){COLOR_DEFAULT}\n - Read Lore {COLOR_PINK}(L){COLOR_DEFAULT}\n - Deploy Drone {COLOR_PINK}(D){COLOR_DEFAULT}\n - Terminate {COLOR_PINK}(T){COLOR_DEFAULT}"
            animate_text(menu_text, delay=0)

        elif game_state == GameState.PLAYING:
            animate_logo(scavenger_welcome_logo, color=COLOR_GREEN, delay=0.02)
            time.sleep(0.02)
            menu_text = f"{COLOR_DEFAULT}Powered by {COLOR_PINK}AstraShell{COLOR_DEFAULT}\n - Read Rules {COLOR_PINK}(H){COLOR_DEFAULT}\n - Read Lore {COLOR_PINK}(L){COLOR_DEFAULT}\n - Deploy Drone {COLOR_PINK}(D){COLOR_DEFAULT}\n - Terminate {COLOR_PINK}(T){COLOR_DEFAULT}"
            animate_text(menu_text, delay=0.02)

        option = input(f"Select an option: {COLOR_PINK}").upper()
        if option == 'H':
            display_rules()
        elif option == 'L':
            display_lore()
        elif option == 'D':
            game_state = GameState.SELECTING_DIFFICULTY
            clear_screen()
            break
        elif option == 'T':
            print(f"{COLOR_RED}Shutting down")
            time.sleep(0.25)
            print(f"{COLOR_BLUE}\nSee you soon!\n")
            time.sleep(0.25)
            exit()
        else:
            print(f"{COLOR_RED}Invalid option. Please try again.")

    while game_state == GameState.SELECTING_DIFFICULTY:
        # Select from available difficulties (based on level)
        print(f"{COLOR_GREEN}Available Difficulties:{COLOR_DEFAULT}")
        if user.level >= NEWBIE_THRESHOLD:
            print(f" - {COLOR_WHITE}Newbie{COLOR_GREEN} (Unlocked)")
        else:
            print(f" {COLOR_DEFAULT}- Newbie{COLOR_RED} (Level {NEWBIE_THRESHOLD})")

        if user.level >= 3:
            print(f" {COLOR_DEFAULT}- {COLOR_WHITE}Junior{COLOR_GREEN} (Unlocked)")
        else:
            print(f" {COLOR_DEFAULT}- Junior{COLOR_RED} (Level {JUNIOR_THRESHOLD})")

        if user.level >= 5:
            print(f" {COLOR_DEFAULT}- {COLOR_WHITE}Intermediate{COLOR_GREEN} (Unlocked)")
        else:
            print(f" {COLOR_DEFAULT}- Intermediate{COLOR_RED} (Level {INTERMEDIATE_THRESHOLD})")

        if user.level >= 8:
            print(f" {COLOR_DEFAULT}- {COLOR_WHITE}Senior{COLOR_GREEN} (Unlocked)")
        else:
            print(f" {COLOR_DEFAULT}- Senior{COLOR_RED} (Level {SENIOR_THRESHOLD})")

        if user.level >= 15:
            print(f"{COLOR_DEFAULT} - {COLOR_WHITE}Expert{COLOR_GREEN} (Unlocked)")
        else:
            print(f" {COLOR_DEFAULT}- Expert{COLOR_RED} (Level {EXPERT_THRESHOLD})")

        difficulty = input(f"{COLOR_GREEN}Select a difficulty: {COLOR_PINK}").lower().strip()
        #make first character uppercase
        try:
            difficulty = difficulty[0].upper() + difficulty[1:]
        except:
            pass

        # Check if difficulty is valid
        if difficulty not in ['Newbie', 'Junior', 'Intermediate', 'Senior', 'Expert']:
            clear_screen()
            print(f"{COLOR_RED}Invalid difficulty. Please try again.")
            continue
        elif difficulty == 'Newbie' and user.level < NEWBIE_THRESHOLD or difficulty == 'Junior' and user.level < JUNIOR_THRESHOLD or difficulty == 'Intermediate' and user.level < INTERMEDIATE_THRESHOLD or difficulty == 'Senior' and user.level < SENIOR_THRESHOLD or difficulty == 'Expert' and user.level < EXPERT_THRESHOLD:
            clear_screen()
            print(f"{COLOR_RED}You have not unlocked this difficulty yet!")
            continue
        else:
            load_config(difficulty)
            break

    animate_logo(logo_frames,color=COLOR_GREEN, delay=0.02)
    time.sleep(0.5)
    user_level_name = difficulty
    load_config(difficulty)
    animate_text(f"{COLOR_DEFAULT}Searching for Suitable Drop Location...", delay=0.05, end=False)
    animation = LoadingAnimation(f"{COLOR_DEFAULT}Searching for Suitable Drop Location...", delay=1)
    animation.start()
    level = pick_random_level(user_level_name, game_state)
        # print_level(level.level, game_state, 0, 0, 0)
        # print(f"                                        {COLOR_GREEN}Displaying level {COLOR_RED}{level.map_seed}.0.{level.seed}")
        # time.sleep(0.2)

    animation.stop()
    animate_text(f"{COLOR_DEFAULT}Setting Drone Coordinates...", delay=0.05, end=False)
    animate_text(f"{COLOR_GREEN}{level.map_seed}{COLOR_DEFAULT}.{COLOR_GREEN}0{COLOR_DEFAULT}.{COLOR_GREEN}{level.seed}", delay=0.02)
    time.sleep(1)
    animate_text(f"{COLOR_DEFAULT}Establishing Link", delay=0.05, end=False)
    animate_text(f"...", delay=0.5, end=False)
    print(f"{COLOR_GREEN}Established")
    time.sleep(1)
    game_state = GameState.PLAYING

    possible_xp = 0
    possible_money = 0
    possible_score = 0
    deployment_runs = 1

    # Main gameplay loop
    while game_state == GameState.PLAYING:
        level.items_collected = 0
        level.steps = 0
        level.monsters_defeated = 0
        print_level(level.level, game_state, level.steps, level.items_collected, level.solution_step_count, level.width)
        emergency_exit = input(f"{COLOR_YELLOW}Enter 'E' for emergency exit, or any other key to continue: {COLOR_RESET}").upper()
        if emergency_exit == 'E':
            if DEBUG_PATH and game_state == GameState.PLAYING:
                clear_screen()
            print(f"{COLOR_RED}Emergency exit activated. Deploying a new drone...{COLOR_GREEN}")
            animation = LoadingAnimation(f"{COLOR_DEFAULT}Searching for Suitable Drop Location...", delay=1)
            animation.start()
            user_level_name = difficulty
            load_config(difficulty)
            level = pick_random_level(user_level_name, game_state)
            animation.stop()
            continue  # Start a new level

        while True:
            move = input(f"{COLOR_GREEN}DRONE COMMAND TERMINAL (Enter [W/A/S/D] to move): ").upper()

            if move in ['W', 'A', 'S', 'D']:
                dx, dy = 0, 0
                if move == 'W':
                    dy = -1
                elif move == 'A':
                    dx = -1
                elif move == 'S':
                    dy = 1
                elif move == 'D':
                    dx = 1
                else:
                    continue

                new_player_x = level.player_x + dx
                new_player_y = level.player_y + dy

                if 0 <= new_player_x < level.width and 0 <= new_player_y < level.height:
                    if level.level[new_player_y][new_player_x] != '#':
                        # Check for item collection
                        if level.level[new_player_y][new_player_x] == 'I':
                            print("You found a core!")
                            level.items_collected += 1
                            # Do not remove the item here, as player will take this place

                        # Check for monster encounter
                        elif level.level[new_player_y][new_player_x] in ['C', 'N', 'R']:
                            monster = next((m for m in level.monsters if m['x'] == new_player_x and m['y'] == new_player_y), None)
                            if monster:
                                items_dropped, step_cost = combat(monster['level'], level.monster_levels)
                                level.items_collected += items_dropped
                                level.monsters.remove(monster)
                                # Do not remove the monster here, as player will take this place
                                level.steps += step_cost

                        # Increment step cost for normal movement
                        if level.level[new_player_y][new_player_x] == '.':
                            level.steps += STEP_COST

                        # Now update the player's position on the map
                        # Remove the player from the old position
                        level.level[level.player_y][level.player_x] = '.'
                        # Update player coordinates
                        level.player_x, level.player_y = new_player_x, new_player_y
                        # Place the player at the new position
                        level.level[level.player_y][level.player_x] = 'P'
                        

                    else:
                        print('There\'s an obstacle there!')

                else:
                    print('There\'s an obstacle there!')


            if level.player_x == level.exit_x and level.player_y == level.exit_y:
                if level.items_collected * STEP_DIVIDER < level.steps:
                    game_state = GameState.FAILED
                else:
                    game_state = GameState.SUCCESS

                print_level(level.level, game_state, level.steps, level.items_collected, level.solution_step_count, level.width)

                if game_state == GameState.SUCCESS:
                    print("You reached the exit successfully!")
                    print(f"Total items collected: {level.items_collected}")
                    possible_xp += level.items_collected*3 + (deployment_runs * user.level) + (difficulty_levels[difficulty] ** 2)
                    possible_money += level.items_collected + (deployment_runs * 3) + (difficulty_levels[difficulty] * 3)
                    possible_score += level.items_collected*level.steps + (deployment_runs * 5) + (difficulty_levels[difficulty] ** 3)
                    print(f"Extract now for {possible_xp} XP, {possible_money} money, and {possible_score} score.")
                    print(f"{COLOR_RED}Careful! Failing a level will reset all progress made during this deployment.{COLOR_GREEN}")
                elif game_state == GameState.FAILED:
                    possible_xp = level.items_collected
                    possible_score = (level.items_collected*level.steps)//3
                    print("Drone malfunctioned, Mission Failed.")
                    print(f"Total items collected: {level.items_collected}")
                    print(f"Extract now for {possible_xp} XP and {possible_score} score.")


                break

            print_level(level.level, game_state, level.steps, level.items_collected, level.solution_step_count, level.width)
            move_monsters(level.monsters, (level.player_x, level.player_y), level.level, level.monster_levels, level.width, level.height)

        if game_state == GameState.SUCCESS or game_state == GameState.FAILED:
            end_game = True
            while end_game:
                if game_state == GameState.FAILED:
                    print(f"\n{COLOR_PINK}Mission Options:{COLOR_DEFAULT}")
                    print("1. Search for another drop location")
                    print("2. Extract now")
                    print("3. Show quick-solution")
                    choice = input(f"{COLOR_PINK}Choose an option (1/2/3): ")
                else:
                    print(f"\n{COLOR_PINK}Mission Options:{COLOR_DEFAULT}")
                    print("1. Search for another drop location")
                    print("2. Extract now")
                    choice = input(f"{COLOR_PINK}Choose an option (1/2): ")
                if choice == '1':
                    load_config(difficulty)
                    if DEBUG_PATH and game_state == GameState.PLAYING:
                        clear_screen()
                    deployment_runs += 1
                    end_game = False
                    game_state = GameState.PLAYING
                    animation = LoadingAnimation(f"{COLOR_DEFAULT}Searching for Suitable Drop Location...", delay=1)
                    animation.start()
                    user_level_name = difficulty
                    load_config(difficulty)
                    level = pick_random_level(user_level_name, game_state)
                    animation.stop()
                elif choice == '2':
                    load_config(difficulty)
                    if DEBUG_PATH and game_state == GameState.PLAYING:
                        clear_screen()
                    #save user stats
                    xp = user.get_xp()
                    money = user.get_money()
                    score = user.get_score()
                    if game_state == GameState.SUCCESS:
                        xp += level.items_collected*3
                        money += level.items_collected
                        score += level.items_collected*level.steps
                        user.save_stats(score=score, xp=xp, money=money)
                    elif game_state == GameState.FAILED:
                        xp += level.items_collected
                        score += (level.items_collected*level.steps)//3
                    user.save_stats(score=score, xp=xp, money=money)
                    game_state = GameState.MAIN_MENU
                    end_game = False
                    main(game_state=GameState.MAIN_MENU, user=user)
                elif choice == '3' and game_state == GameState.FAILED:
                    load_config(difficulty)
                    if DEBUG_PATH and game_state == GameState.PLAYING:
                        clear_screen()
                    #move cursor up 5 lines
                    print("\033[F"*5)
                    level.show_solution()
                    # level.animate_solution()
                    continue  # After showing solution, ask again

def pick_random_level(difficulty, game_state):
    if RANDOM_SEED:
        #open levels.json and pick a random level, then load it, if there are no levels in the file, generate a new one
        with open('levels.json', 'r') as f:
            levels = json.load(f)
        f.close()
        if levels:
            random.seed(None)
            #levels format = {difficulty: [[map_seed, seed], [map_seed, seed], ...]}
            #pick random map_seed and seed from levels[difficulty]
            try:
                map_seed, seed = random.choice(levels[difficulty])
                level = Level(seed,map_seed, WIDTH, HEIGHT)
                #remove map_seed, seed from levels[difficulty]
                levels[difficulty].remove([map_seed, seed])
                #update levels.json
                with open('levels.json', 'w') as f:
                    json.dump(levels, f, indent=4)
                f.close()   
            except IndexError:
                random.seed(None)
                seed = random.randint(0, 9999999999)
                level = Level(seed,seed//2, WIDTH, HEIGHT)    
        else:
            random.seed(None)
            seed = random.randint(0, 9999999999)
            level = Level(seed,seed//2, WIDTH, HEIGHT)
    else:
        level = Level(LEVEL_SEED,LEVEL_SEED//2, WIDTH, HEIGHT)

    validation_attempts = 0
    while not validate_level(level, game_state):
        validation_attempts += 1
        if validation_attempts < MAX_VALIDATION_ATTEMPTS:
            level.regenerate_positions()
        else:
            random.seed(None)
            seed = random.randint(0, 9999999999) if RANDOM_SEED else LEVEL_SEED
            level = Level(seed,seed//2, WIDTH, HEIGHT)
            validation_attempts = 0

    return level

def background_level_generator_thread():
    difficulties = ['Newbie', 'Junior', 'Intermediate', 'Senior', 'Expert']
    while True:
        #pick random difficulty
        #generate levels in the background
        random.seed(None)
        difficulty = random.choice(difficulties)
        load_config(difficulty)
        seed = random.randint(0, 9999999999)
        level = Level(seed, seed//2, WIDTH, HEIGHT)
        time.sleep(0.00001)
        validation_attempts = 0

        while not validate_level(level, GameState.BACKGROUND_TASK):
            time.sleep(0.00001)
            validation_attempts += 1
            if validation_attempts < MAX_VALIDATION_ATTEMPTS:
                level.regenerate_positions()
            else:
                random.seed(None)
                seed = random.randint(0, 9999999999) if RANDOM_SEED else LEVEL_SEED
                level = Level(seed,seed//2, WIDTH, HEIGHT)
                time.sleep(0.00001)
                validation_attempts = 0

        #update levels.json with self.difficulty: [self.map_seed, self.seed]
        with open('levels.json', 'r') as f:
            levels = json.load(f)
        f.close()

        with open('levels.json', 'w') as f:
            levels[level.difficulty].append([level.map_seed,level.seed])
            json.dump(levels, f, indent=4)

        f.close()
        time.sleep(0.00001)



if __name__ == "__main__":
    #start thread that constatly runs background_level_generator_thread()
    t = threading.Thread(target=background_level_generator_thread)
    t.daemon = True
    t.start()
    main(GameState.STARTUP)