"""
Dubby v2.0 is the UVic AI's 2020 BattleSnake entry
"""
import os
import random
import time
import bottle
import traceback
import json
from . import functions as f


direction = None

@bottle.route('/')
def index():
    return "<h1>Dubby</h1>"

@bottle.route('/static/<path:path>')
def static(path):
    return bottle.static_file(path, root='static/')

@bottle.post('/ping')
def ping():
    return {}

@bottle.post('/end')
def end():
    return {}

@bottle.post('/start')
def start():
    headUrl = '%s://%s/static/head.png' % (
        bottle.request.urlparts.scheme,
        bottle.request.urlparts.netloc
    )

    print("\n\n\n\n\n\n")

    return {
        'color': '#EADA50',
        'taunt': 'A simple taunt',
        'head_url': headUrl
    }


@bottle.post('/move')
def move(data=None):
    random.seed()

    if not data:
        data = bottle.request.json

    # Get all the data
    you = data['you']

    you['body'] = [ (b['x'], b['y']) for b in you['body'] ]

    you['head'] = you['body'][0]

    you['size'] = len(you['body'])

    position = (you["head"][0], you["head"][1])

    food = [(f['x'], f['y']) for f in data['board']['food']]
    
    board = data['board']

    snakes = data["board"]["snakes"]

    #Desperation threshold
    hungry = False
    health = you["health"]
    if health <= 35:
        hungry = True

    just_ate = False
    if health == 100:
        just_ate = True

    #Locates snake tails
    tails = []
    for snake in snakes:
        tails.append((snake["body"][-1]['x'], snake["body"][-1]['y']))

    #Locates snake heads
    heads = []
    for snake in snakes:
        if snake["name"] != "dubby":
            heads.append((snake["body"][0]['x'], snake["body"][0]['y']))
    
    #Snakes that are bigger than Dubby
    bigger_snakes = []
    for snake in snakes:
        if snake["name"] == "dubby": continue
        if len(snake["body"]) >= you["size"]:
            bigger_snakes.append(snake["name"])

    #Used to initiate grow sequence (become bigger than other snakes)
    grow = False
    for snake in snakes:
        if snake["name"] == "dubby":
            continue
        if len(snake["body"]) >= you["size"] - 1:
            grow = True



    #All the available board space
    all_available = allAvailableSpace(board)

    #Used to convert positions to direction strings
    possible_moves = possibleMoves(position, all_available)

    if heads != []:
        #Predicting enemy moves for next turn
        enemy_possible_moves = possibleMoves(heads[0], all_available)

        possible_moves2 = possible_moves.copy()
        temp2 = []
        for x in enemy_possible_moves:
            for y in possible_moves:
                temp = all_available.copy()
                for t in tails:
                    temp.append(t)
                temp.remove(enemy_possible_moves[x])
                try:
                    temp.remove(possible_moves[y])
                except:
                    pass
                direction_area2 = directionArea(possible_moves[y], possibleMoves(possible_moves[y], temp), board, temp)
                b = False
                for z in direction_area2:
                    if direction_area2[z] > you["size"]:
                        b = True
                        break

                #Limiting path incoming! remove from available
                if b == False:
                    temp2.append(y)

        #Remove them from available
        for i in temp2:
            try:
                del possible_moves[i]
            except:
                pass









    safe_moves, limiting_moves, restricted_moves, dead_ends = safeMoves(position, all_available)
    safe_moves_str = positionToString(possible_moves, safe_moves)
    limiting_moves_str = positionToString(possible_moves, limiting_moves)
    restricted_moves_str = positionToString(possible_moves, restricted_moves)
    dead_ends_str = positionToString(possible_moves, dead_ends)

    attack_moves = attackMoves(position, board, snakes, bigger_snakes)
    attack_moves_str = positionToString(possible_moves, attack_moves)

    closest_food = closestFood(you, board, hungry)
    food_move = foodMove(position, closest_food)

    #Removes critical moves from safe_moves
    critical_moves =  criticalMoves(position, board, snakes, bigger_snakes)
    temp = []
    for i in critical_moves:
        if i not in possible_moves:
            temp.append(i)
    for i in temp:
        critical_moves.remove(i)



    for cm in critical_moves:
        if cm in safe_moves_str:
            safe_moves_str.remove(cm)
        if cm in limiting_moves_str:
            limiting_moves_str.remove(cm)
        if cm in restricted_moves_str:
            restricted_moves_str.remove(cm)
        if cm in dead_ends_str:
            dead_ends_str.remove(cm)


    # Lean function moves snake away when trying to stay safe
    closest_enemy = closestEnemy(position, snakes)
    lean_enemy_str = leanEnemy(position, closest_enemy)
    lean_board_str = leanBoard(position, board, closest_enemy)

    # if list(set(limiting_moves_str).intersection(set(lean_enemy_str))) != []:
    #     limiting_moves_str = list(set(limiting_moves_str).intersection(set(lean_enemy_str)))

    # if list(set(restricted_moves_str).intersection(set(lean_enemy_str))) != []:
    #     restricted_moves_str = list(set(restricted_moves_str).intersection(set(lean_enemy_str)))




    #should return a dictionary of directions with their fill space
    direction_area = directionArea(position, possible_moves, board, all_available)

    #take largest area unless it's critical
    area_list = []
    for da in direction_area:
        area_list.append(direction_area[da])
    area_list.sort(reverse = True)
    
    #area_list_str = []
    large_area_str = []
    small_area_str = []

    for i in range(len(area_list)):
        for x in direction_area:
            if direction_area[x] == area_list[i]:
                #area_list_str.append(x)
                if (area_list[i] > you["size"]) and (x not in large_area_str):
                    large_area_str.append(x)
                if area_list[i] <= you["size"] and (x not in small_area_str):
                    small_area_str.append(x)

    

    # if list(set(area_list_str).intersection(set(lean_move_str))) != []:
    #     area_list_str = list(set(area_list_str).intersection(set(lean_move_str)))     

    #print(hungry)
    # print(large_area_str)
    # print(lean_move_str)

    #NEED TO START BEING PREEMPTIVE, RUN FILL ON NEXT MOVES TO ELIMINATE MORE MOVES
    #Look at the next possible moves for all snakes (which bring them closer to us,
    #Perform fill for adjacent moves with each situation (safe to restricted), 
    #elminate moves which trap dubby in small pockets?

    #LEAN RESTRICTED OVER LIMITED?


    # print(hungry)
    # print(large_area_str)

    #try leaning first, otherwise take it
    #Priority -1: Avoid being trapped
    if (len(large_area_str) + len(small_area_str)) < 3: #BUG - Need to properly reduce large_area_str
        # for i in range(len(large_area_str)):
        #     if (large_area_str[i] not in critical_moves) and (large_area_str[i] in lean_enemy_str):
        #         return {
        #         'move': large_area_str[i],
        #         'taunt': 'A simple taunt'
        #         }
        for i in range(len(large_area_str)):
            if (large_area_str[i] not in critical_moves) and (large_area_str[i] in possible_moves):
                return {
                'move': large_area_str[i],
                'taunt': 'A simple taunt'
                }
        for i in range(len(small_area_str)):
            if (small_area_str[i] not in critical_moves) and (small_area_str[i] in possible_moves):
                return {
                'move': small_area_str[i],
                'taunt': 'A simple taunt'
                }

    # print(safe_moves_str)
    # print(limiting_moves_str)
    # print(restricted_moves_str)
    # print(critical_moves)


########################################
###### INITIATE PRIORITY SEQUENCE ######
########################################
    
    #Priority 0: Eat food when hungry
    if hungry == True:
        safe = set(safe_moves_str).intersection(set(food_move))
        if safe == set():
            limiting = set(limiting_moves_str).intersection(set(food_move))
            if limiting == set():
                if safe_moves_str == []:
                    if limiting_moves_str == []:
                        if restricted_moves_str == []:
                            if critical_moves == []:
                                desp = desperation(position, tails, heads)
                                rand = random.choice(desp)
                                return {
                                'move': rand,
                                'taunt': 'GG'
                                }
                            rand = random.choice(critical_moves)
                            return {
                            'move': rand,
                            }
                        rand = random.choice(restricted_moves_str)
                        return {
                        'move': rand,
                        }
                    rand = random.choice(limiting_moves_str)
                    return {
                    'move': rand,
                    }
                rand = random.choice(safe_moves_str)
                return {
                'move': rand,
                }
            rand = random.choice(tuple(limiting))
            return {
            'move': rand,
            }
        rand = random.choice(tuple(safe))
        return {
        'move': rand,
        }


    #Priority 1: Eat food to get larger (Safely)
    if grow == True:
        safe = set(safe_moves_str).intersection(set(food_move))
        limiting = set(limiting_moves_str).intersection(set(food_move))

        if safe != set():
            rand = random.choice(tuple(safe))
            return {
            'move': rand,
            }
        if limiting != set():
            rand = random.choice(tuple(limiting))
            return {
            'move': rand,
            }

    #Priority 2: Stay safe
    if safe_moves_str == []:

        #Priority 3: Attack snakes
        if attack_moves_str == []:
            #print(attack_moves_str)
            #Priority 4: Limiting moves
            if limiting_moves_str == []:

                #Priority 5: Restricted moves
                if restricted_moves_str == []:

                    #Priority 6: Critical moves
                    if critical_moves == []:

                        #Priority 7: Desperate moves
                        desp = desperation(position, possible_moves2, tails, heads)
                        rand = random.choice(desp)
                        return {
                        'move': rand,
                        'taunt': 'GG'
                        }
                    rand = random.choice(critical_moves)
                    return {
                    'move': rand,
                    }
                rand = random.choice(restricted_moves_str)
                return {
                'move': rand,
                }
            rand = random.choice(limiting_moves_str)
            return {
            'move': rand,
            }
        rand = random.choice(attack_moves_str)
        return {
        'move': rand,
        }
    rand = random.choice(safe_moves_str)
    return {
    'move': rand,
    }



################################
######### FUNCTIONS #############
#################################


# Returns the amount of available space is available
# depending on the direction taken
def directionArea(position, moves, board, all_available):  

    #creates a dictionary where the directions return
    # the size of free space available.
    d_lengths = {}
    for m in moves:
        if m == "up":
            d = (position[0], position[1] - 1)
        if m == "down":
            d = (position[0], position[1] + 1)
        if m == "left":
            d = (position[0] - 1, position[1])
        if m == "right":
            d = (position[0] + 1, position[1])
        d_lengths[m] = len(fill_recursion(all_available, board, d, [], []))
    return d_lengths


# Positioned exclusivly in directionArea as the recursive portion of fill algorithm. 
# Operates on first in first out.
def fill_recursion(all_available, board, position, unexplored = [], explored = []):

    #All adjacent squares
    moves = []
    moves.append((position[0], position[1] - 1))
    moves.append((position[0], position[1] + 1))
    moves.append((position[0] - 1, position[1]))
    moves.append((position[0] + 1, position[1]))

    #update the explored and unexplored portion
    explored.append(position)
    if position in unexplored:
        unexplored.remove(position)
        
    #add available squares to unexplored
    for i in moves:
        if i not in all_available:
            continue
        if i in explored:
            continue
        if i in unexplored:
            continue
        unexplored.append(i)
    
    #Recursion as long as there are unexplored squares
    if unexplored != []:
        try:
            return fill_recursion(all_available, board, unexplored[0], unexplored, explored)
        except:
            return explored
    return explored


def possibleMoves(position, all_available):
    possible_moves = {
        "right": (position[0] + 1, position[1]),
        "left": (position[0] - 1, position[1]),
        "down": (position[0], position[1] + 1),
        "up": (position[0], position[1] - 1),
    }

    temp = []
    for key in possible_moves:
        if possible_moves[key] not in all_available:
            temp.append(key)
    for key in temp:
        del possible_moves[key]
    return possible_moves


#Converts position list to string list
def positionToString(possible_moves, position_list):
    string_list = []
    for key in possible_moves:
        if possible_moves[key] in position_list:
            string_list.append(key)
    return string_list


#A last resort for survival, crashes snake into tails, or else heads
def desperation(position, possible_moves, tails, heads):
    move_t = []
    move_h = []

    if possible_moves != {}:
        random.seed()
        rand = random.choice(list(possible_moves.keys()))
        return rand

    #Crash into tail if possible
    if (position[0] + 1, position[1]) in tails:
        move_t.append("right")
    if (position[0] - 1, position[1]) in tails:
        move_t.append("left")
    if (position[0], position[1] - 1) in tails:
        move_t.append("up")
    if (position[0], position[1] + 1) in tails:
        move_t.append("down")          
    if move_t != []:
        random.seed()
        rand = random.choice(move_t)
        return rand

    #otherwise crash into head
    if (position[0] + 1, position[1]) in heads:
        move_h.append("right")
    if (position[0] - 1, position[1]) in heads:
        move_h.append("left")
    if (position[0], position[1] - 1) in heads:
        move_h.append("up")
    if (position[0], position[1] + 1) in heads:
        move_h.append("down") 
    if move_h != []:
        random.seed()
        rand = random.choice(move_h)
        return rand






#These can be game ending moves, commonly head-to-head with larger snake
def criticalMoves(position, board, snakes, bigger_snakes):
    critical_moves = []
    for snake in snakes:
        if snake["name"] in bigger_snakes:
            enemy_head = (snake['body'][0]['x'], snake['body'][0]['y'])
            
            if enemy_head == (position[0], position[1] - 2):
                critical_moves.append("up")
            if enemy_head == (position[0], position[1] + 2):
                critical_moves.append("down")
            if enemy_head == (position[0] - 2, position[1]):
                critical_moves.append("left")
            if enemy_head == (position[0] + 2, position[1]):
                critical_moves.append("right")

            if enemy_head == (position[0] + 1, position[1] + 1):
                critical_moves.append("down")
                critical_moves.append("right")
            if enemy_head == (position[0] - 1, position[1] + 1):
                critical_moves.append("down")
                critical_moves.append("left")
            if enemy_head == (position[0] - 1, position[1] - 1):
                critical_moves.append("left")
                critical_moves.append("up")
            if enemy_head == (position[0] + 1, position[1] - 1):
                critical_moves.append("up")
                critical_moves.append("right")

    return list(set(critical_moves))


#Attack snake 
def attackMoves(position, board, snakes, bigger_snakes):
    attack_moves = []
    for snake in snakes:
        if snake["name"] not in bigger_snakes:
            enemy_head = (snake['body'][0]['x'], snake['body'][0]['y'])
            
            if enemy_head == (position[0], position[1] - 2):
                attack_moves.append("up")
            if enemy_head == (position[0], position[1] + 2):
                attack_moves.append("down")
            if enemy_head == (position[0] - 2, position[1]):
                attack_moves.append("left")
            if enemy_head == (position[0] + 2, position[1]):
                attack_moves.append("right")

            if enemy_head == (position[0] + 1, position[1] + 1):
                attack_moves.append("down")
                attack_moves.append("right")
            if enemy_head == (position[0] - 1, position[1] + 1):
                attack_moves.append("down")
                attack_moves.append("left")
            if enemy_head == (position[0] - 1, position[1] - 1):
                attack_moves.append("left")
                attack_moves.append("up")
            if enemy_head == (position[0] + 1, position[1] - 1):
                attack_moves.append("up")
                attack_moves.append("right")

    return list(set(attack_moves))


def safeMoves(position, all_available):
    safe_moves = []
    limiting_moves = []
    restricted_moves = []
    dead_ends = []

    adjacent_moves = adjacentMoves(position, all_available)

    for am in adjacent_moves:
        if len(adjacentMoves(am, all_available)) == 3:
            safe_moves.append(am)
        if len(adjacentMoves(am, all_available)) == 2:
            limiting_moves.append(am)
        if len(adjacentMoves(am, all_available)) == 1:
            restricted_moves.append(am)        
        if len(adjacentMoves(am, all_available)) == 0:
            dead_ends.append(am)   

    return safe_moves, limiting_moves, restricted_moves, dead_ends


#returns all the positions that are available
def adjacentMoves(position, all_available):
    adjacent_moves = []

    if (position[0] + 1, position[1]) in all_available:
        adjacent_moves.append((position[0] + 1, position[1]))
    if (position[0] - 1, position[1]) in all_available:
        adjacent_moves.append((position[0] - 1, position[1]))
    if (position[0], position[1] + 1) in all_available:
        adjacent_moves.append((position[0], position[1] + 1))
    if (position[0], position[1] - 1) in all_available:
        adjacent_moves.append((position[0], position[1] - 1))                
    
    return adjacent_moves


#Generates all available nodes
def allAvailableSpace(board):
    all_available = []
    for i in range(1, board["height"]):
        for j in range(1, board["width"]):
            all_available.append((i,j))

    #removes obstacles for fill
    for snake in board["snakes"]:
        for body in snake["body"]:
            if (body['x'], body['y']) in all_available:
                del all_available[all_available.index((body['x'], body['y']))]

    return all_available


#takes the possible moves and returns the available adjacent spaces.
def obstacles(position, moves, board):

    #removes walls
    if (position[0] - 1 < 1):
        moves.remove("left")
    if (position[0] + 1 >= board['width']):
        moves.remove("right")
    if (position[1] - 1 < 1):
        moves.remove("up")
    if (position[1] + 1 >= board['height']):
        moves.remove("down")

    #removes the adjacent snake body obstacles
    for snake in board["snakes"]:
        for body in snake["body"]:
            try:
                if body == (position[0] - 1, position[1]):
                    moves.remove("left")
                if body == (position[0] + 1, position[1]):
                    moves.remove("right")
                if body == (position[0], position[1] - 1):
                    moves.remove("up")
                if body == (position[0], position[1] + 1):
                    moves.remove("down")
            except:
                pass

    return moves


#find the closest food
def closestFood(you, board, hungry):
    closest_food = {}
    distance_to_food = board['height']*2
    for i in board["food"]:
        #Avoid food along the edges, not always good
        if i['x'] > 0 and i['x'] < board['width'] - 1 and i['y'] > 0 and i['y'] < board['height'] - 1 and hungry == False:
            temp = abs(i["x"] - you["head"][0]) + abs(i["y"] - you["head"][1])
            if temp < distance_to_food:
                #New closest food
                distance_to_food = temp
                closest_food = i
        if hungry == True:
            temp = abs(i["x"] - you["head"][0]) + abs(i["y"] - you["head"][1])
            if temp < distance_to_food:
                #New closest food
                distance_to_food = temp
                closest_food = i
    return closest_food

#Need risky food and safe food
def foodMove(position, closest_food):
    food_move = []

    if closest_food != {}:
        #left and right
        if position[0] < closest_food["x"]:
            food_move.append("right")
        if position[0] > closest_food['x']:
            food_move.append("left")
        if position[1] > closest_food['y']:
            food_move.append("up")
        if position[1] < closest_food['y']:
            food_move.append("down")
    
    return food_move


#find the closest enemy
def closestEnemy(position, snakes):
    closest_enemy = None
    dist_to_enemy = 999
    for snake in snakes:
        if snake["name"] == "dubby": continue
        enemy_head = (snake['body'][0]['x'], snake['body'][0]['y'])
        temp = abs(enemy_head[0] - position[0]) + abs(enemy_head[1] - position[1])
        if temp < dist_to_enemy:
            dist_to_enemy = temp
            closest_enemy = enemy_head
    return closest_enemy

#Leans snake away from enemy
def leanEnemy(position, closest_enemy):
    lean_enemy = []

    if closest_enemy != ():
        #lean based on enemy position
        if position[0] < closest_enemy[0]:
            lean_enemy.append("left")
        if position[0] > closest_enemy[0]:
            lean_enemy.append("right")
        if position[1] > closest_enemy[1]:
            lean_enemy.append("down")
        if position[1] < closest_enemy[1]:
            lean_enemy.append("up")
    
    return lean_enemy

#Leans snake towards board centre
def leanBoard(position, board, closest_enemy):
    lean_board = []

    #lean based on board position
    if position[0] == closest_enemy[0]:
        if position[1] <= board["height"] / 2:
            lean_board.append("down")
        if position[1] > board["height"] / 2:
            lean_board.append("up")
    if position[1] == closest_enemy[1]:
        if position[0] <= board["width"] / 2:
            lean_board.append("right")
        if position[0] > board["width"] / 2:
            lean_board.append("left")
    
    return lean_board

############################
##### MAIN FUNCTION ########
############################

# Expose WSGI app (so gunicorn can find it)
application = bottle.default_app()

if __name__ == '__main__':
    bottle.run(
        application,
        host=os.getenv('IP', '0.0.0.0'),
        port=os.getenv('PORT', '8080'),
        debug = True)
