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

    walls = (data['board']['width'], data['board']['height'])

    food = [(f['x'], f['y']) for f in data['board']['food']]
    
    numFood = len(food)

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


    #Snakes that are bigger than Dubby
    bigger_snakes = []
    for j in range(len(data["board"]["snakes"])):
        if data["board"]["snakes"][j]["name"] == "dubby": continue
        if len(data["board"]["snakes"][j]["body"]) >= you["size"]:
            bigger_snakes.append(data["board"]["snakes"][j]["name"])


    #TO-DO: Algorithm for finding food
    #       Coiling (utilize space when it's smaller than snake body)
    #       Fight snakes
    #       Passive mode


    #Prints relevent console information for debugging
    # print("Dubby: x =", you["head"][0], ", y =", you["head"][1])
    # print("Possible moves:", moves)
    # print("Closest food:", closest_food)
    # print("Bigger snakes:", bigger_snakes)


    try:
        random.seed()
        rand = random.choice(list(moves.keys()))
        return {
        'move': rand,
        'taunt': 'A simple taunt'
        }
    #No possible moves remaining, good game.
    except:
        return{
        'move': "up",
        'taunt': 'GG'
        }

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
    if (position[0] - 1 < 1):
        del moves["left"]
    if (position[0] + 1 >= board['width']):
        del moves["right"]
    if (position[1] - 1 < 1):
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


