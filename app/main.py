"""
Dubby is the UVic AI's 2020 BattleSnake entry
"""
import os
import random
import time
import bottle
import traceback
import json

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

    if not data:
        data = bottle.request.json

    # Get all the data
    you = data['you']

    you['body'] = [ (b['x'], b['y']) for b in you['body'] ]

    you['head'] = you['body'][0]

    you['size'] = len(you['body'])

    health = you["health"]

    food = [(f['x'], f['y']) for f in data['board']['food']]
    
    numFood = len(food)

    board = data['board']

    snakes = data["board"]["snakes"]

    us = (you["head"][0], you["head"][1])

    hungry = False
    #Locates snake tails
    tails = []
    for i in snakes:
        tails.append((i["body"][-1]['x'],i["body"][-1]['y']))

    #Locates snake heads
    heads = []
    for i in snakes:
        heads.append((i["body"][0]['x'],i["body"][0]['y']))

    if health < 15:
        hungry = True

    #possible moves with locations, remove options as required.
    moves = { "up": (you["head"][0], you["head"][1]-1),
    "down": (you["head"][0], you["head"][1]+1),
    "left": (you["head"][0]-1, you["head"][1]),
    "right": (you["head"][0]+1, you["head"][1])
    }

    #Removes obstaces from standard move list
    moves = obstacles(you["head"], moves, data["board"])


    #Fill algorithm eliminates common dead ends
    moves = fill(you["head"], moves, data["board"])


    #Find and eat food
    closest_food = closestFood(you, board, hungry)

    prefered_moves = []

    if closest_food != {}:
        #left and right
        if you["head"][0] < closest_food["x"]:
            prefered_moves.append("right")
        if you["head"][0] > closest_food['x']:
            prefered_moves.append("left")
        if you["head"][1] > closest_food['y']:
            prefered_moves.append("up")
        if you["head"][1] < closest_food['y']:
            prefered_moves.append("down")


    #Flee bigger snakes
    #Snakes that are bigger than Dubby
    bigger_snakes = []
    for j in range(len(snakes)):
        if len(snakes[j]["body"]) >= you["size"]:
            bigger_snakes.append(snakes[j]["name"])


    #Attack snake 
    for i in snakes:
        if i["name"] not in bigger_snakes:
            enemy = (i['body'][0]['x'], i['body'][0]['y'])
            us = (you["head"][0], you["head"][1])
            
            if enemy == (us[0], us[1] - 2):
                prefered_moves.append("up")
            if enemy == (us[0], us[1] + 2):
                prefered_moves.append("down")
            if enemy == (us[0] - 2, us[1]):
                prefered_moves.append("left")
            if enemy == (us[0] + 2, us[1]):
                prefered_moves.append("right")

            if enemy == (us[0] + 1, us[1] + 1):
                prefered_moves.append("down")
                prefered_moves.append("right")
            if enemy == (us[0] - 1, us[1] + 1):
                prefered_moves.append("down")
                prefered_moves.append("left")
            if enemy == (us[0] - 1, us[1] - 1):
                prefered_moves.append("left")
                prefered_moves.append("up")
            if enemy == (us[0] + 1, us[1] - 1):
                prefered_moves.append("up")
                prefered_moves.append("right")
    
    #Removes duplicates
    prefered_moves = list(set(prefered_moves))



    critical_moves = []
    #These can be game ending moves, not on par with adjacent wall tiles
    #Avoid dangerous moves 
    for i in snakes:
        if i["name"] in bigger_snakes:
            enemy = (i['body'][0]['x'], i['body'][0]['y'])
            
            if enemy == (us[0], us[1] - 2):
                critical_moves.append("up")
            if enemy == (us[0], us[1] + 2):
                critical_moves.append("down")
            if enemy == (us[0] - 2, us[1]):
                critical_moves.append("left")
            if enemy == (us[0] + 2, us[1]):
                critical_moves.append("right")

            if enemy == (us[0] + 1, us[1] + 1):
                critical_moves.append("down")
                critical_moves.append("right")
            if enemy == (us[0] - 1, us[1] + 1):
                critical_moves.append("down")
                critical_moves.append("left")
            if enemy == (us[0] - 1, us[1] - 1):
                critical_moves.append("left")
                critical_moves.append("up")
            if enemy == (us[0] + 1, us[1] - 1):
                critical_moves.append("up")
                critical_moves.append("right")

    #Removes duplicates
    critical_moves = list(set(critical_moves))

    dangerous_moves = []
    #wall adjacent squares are dangerous
    if hungry == False:
        if us[0] == 0:
            dangerous_moves.append("up")
            dangerous_moves.append("down")

        if us[0] == board['width']:
            dangerous_moves.append("up")
            dangerous_moves.append("down")

        if us[1] == 0:
            dangerous_moves.append("left")
            dangerous_moves.append("right")

        if us[1] == board['height']:
            dangerous_moves.append("left")
            dangerous_moves.append("right")


        if us[0] == 1:
            dangerous_moves.append("left")

        if us[0] == board['width'] - 2:
            dangerous_moves.append("right")

        if us[1] == 1:
            dangerous_moves.append("up")

        if us[1] == board['height'] - 2:
            dangerous_moves.append("down")

    #Removes duplicates
    dangerous_moves = list(set(dangerous_moves))

    #remove critical from everything
    crit = []
    for i in moves.keys():
        if i in critical_moves:
            crit.append(i)
    for i in crit:
        if i in moves:
            del moves[i]
    for i in crit:
        if i in prefered_moves:
            del prefered_moves[prefered_moves.index(i)]
    for i in crit:
        if i in dangerous_moves:
            del dangerous_moves[dangerous_moves.index(i)]

    #remove dangerous from everything
    riskey_moves = []
    for i in dangerous_moves:
        if i in moves.keys():
            riskey_moves.append(i)
    for i in riskey_moves:
        if i in moves:
            del moves[i]
    for i in riskey_moves:
        if i in prefered_moves:
            del prefered_moves[prefered_moves.index(i)]
                    
    #merges prefered moves with all moves
    temp = []
    for i in moves.keys():
        if i in prefered_moves:
            temp.append(i)
    prefered_moves = temp

    #Risky moves that are viable


    #Critical moves are a last resort



    #Remove moves which are dangerous
    for i in dangerous_moves:
        if i in moves:
            del moves[i]
        if i in prefered_moves:
            del prefered_moves[prefered_moves.index(i)]
    

    if health == 1:
        print("health")
    #TO-DO: 
    #       Coiling (utilize space when it's smaller than snake body)
    #       Passive mode
    #       Online dubby thinks tails are available squares
    #       Also thinks head to head with the same size snake is a good idea

    #Trys the prefered move set first
    try:
        random.seed()
        rand = random.choice(prefered_moves)
        #print("prefered", rand)
        return {
        'move': rand,
        'taunt': 'A simple taunt'
        }
    #If no prefered moves are feasible, any move is good.
    except:
        try:
            random.seed()
            rand = random.choice(list(moves.keys()))
            #print("move", rand)
            return {
            'move': rand,
            'taunt': 'A simple taunt'
            }
        #No possible moves remaining, crash into tails or heads, good game.
        except:

            try:
                random.seed()
                rand = random.choice(riskey_moves)
                #print("risky", rand)
                return {
                'move': rand,
                'taunt': 'A simple taunt'
                }
            except:
                try:
                    random.seed()
                    rand = random.choice(crit)
                    #print("risky", rand)
                    return {
                    'move': rand,
                    'taunt': 'A simple taunt'
                    }
                except:
                    move_t = []
                    move_h = []

                    #Crash into tail if possible
                    if (us[0] + 1, us[1]) in tails:
                        move_t.append("right")
                    if (us[0] - 1, us[1]) in tails:
                        move_t.append("left")
                    if (us[0], us[1] - 1) in tails:
                        move_t.append("up")
                    if (us[0], us[1] + 1) in tails:
                        move_t.append("down")          

                    #otherwise crash into head
                    if (us[0] + 1, us[1]) in heads:
                        move_h.append("right")
                    if (us[0] - 1, us[1]) in heads:
                        move_h.append("left")
                    if (us[0], us[1] - 1) in heads:
                        move_h.append("up")
                    if (us[0], us[1] + 1) in heads:
                        move_h.append("down") 

                    if move_t != []:
                        random.seed()
                        rand = random.choice(move_t)
                        return {
                        'move': rand,
                        'taunt': 'A simple taunt'
                        }

                    if move_h != []:
                        random.seed()
                        rand = random.choice(move_h)
                        return {
                        'move': rand,
                        'taunt': 'A simple taunt'
                        }

                    return{
                    'move': "up",
                    'taunt': 'GG'
                    }

#find the closest food
def closestFood(you, board, hungry):
    closest_food = {}
    distance_to_food = board['height']*2
    for i in board["food"]:
        #Avoid food along the edges
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

# Takes available moves and removes those
# directions where space is smaller than the snake.
# Takes the snakes initial position, moves, and board data,
# returns the available moves
def fill(position, moves, board):
    
    #Generates the nodes for fill
    all_available = []
    for i in range(1, board["height"]):
        for j in range(1, board["width"]):
            all_available.append((i,j))

    #removes obstacles for fill
    for snake in board["snakes"]:
        for body in snake["body"]:
            if (body['x'], body['y']) in all_available:
                del all_available[all_available.index((body['x'], body['y']))]
    
    #creates a dictionary where the directions return
    # the size of free space available.
    temp = {}
    for m in moves:
        temp[m] = len(fill_recursion(all_available, board, moves[m], [], []))

    #find the largest area
    longest = 0
    directions = []
    for i in temp:
        if temp[i] >= longest:
            longest = temp[i]

    #combine results which utilize the largest area
    for i in temp:
        if temp[i] == longest:
            directions.append(i)

    #Deletes moves where area is small
    temp = []
    for i in moves:
        if i not in directions:
            temp.append(i)
    for i in temp:
        del moves[i]

    return moves

#Used exclusively in fill as the recursive portion of fill. operates on first
#in first out.
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
        del unexplored[unexplored.index(position)]
        
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


#takes a position and returns the available adjacent spaces.
def obstacles(position, moves, board):
    if (position[0] - 1 < 0):
        del moves["left"]
    if (position[0] + 1 >= board['width']):
        del moves["right"]
    if (position[1] - 1 < 0):
        del moves["up"]
    if (position[1] + 1 >= board['height']):
        del moves["down"]

    temp = []

    #Finds the adjacent snake body obstacles
    for j in range(len(board["snakes"])):
        for i in board["snakes"][j]["body"]:
            for key in moves:
                if (i["x"], i["y"]) == moves[key]:
                    temp.append(key)
    #Deletes these moves from available options
    for i in range(len(temp)):
        del moves[temp[i]]

    return moves


# Expose WSGI app (so gunicorn can find it)
application = bottle.default_app()

if __name__ == '__main__':
    bottle.run(
        application,
        host=os.getenv('IP', '0.0.0.0'),
        port=os.getenv('PORT', '8080'),
        debug = True)


