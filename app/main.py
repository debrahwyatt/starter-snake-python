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

    global direction


    # Get all the data
    you = data['you']

    you['body'] = [ (b['x'], b['y']) for b in you['body'] ]

    you['head'] = you['body'][0]

    you['size'] = len(you['body'])

    health = you["health"]

    walls = (data['board']['width'], data['board']['height'])

    food = [(f['x'], f['y']) for f in data['board']['food']]
    
    numFood = len(food)
    
    print(health)

    #Avoid walls by going clockwise   
    #Right wall avoidance
    if you['head'][0] == walls[1]-1:
        #Bottom right corner avoidance
        if you['head'][1] == walls[0]-1 and direction == "down":
            direction = "left"
            return {
                'move': "left"
                }
        else:
            direction = "down"
            return {
                'move': "down"
                }
    
    #Bottom Wall avoidance
    elif you['head'][1] == walls[0]-1:
        #Bottom left corner avoidance
        if you['head'][0] == 0 and direction == "left":
            direction = "up"
            return {
                'move': "up"
                }
        else:
            direction = "left"
            return {
                'move': "left"
                }

    #Left wall avoidance
    elif you['head'][0] == 0:
        #Top left corner avoidance
        if you['head'][1] == 0 and direction == "up":
            direction = "right"
            return {
                'move': "right"
                }
        else:
            direction = "up"
            return {
                'move': "up"
                }

    #Top wall avoidance
    elif you['head'][1] == 0:
        #Top right corner avoidance
        if you['head'][0] == walls[1]-1 and direction == "right":
            direction = "down"
            return {
                'move': "down"
                }
        else:
            direction = "right"
            return {
                'move': "right"
                }
    '''
    elif you['head'] == walls[0]:
        return 'move': "left"
    elif you['head'] == walls[0]:
        return 'move': "left"
    elif you['head'] == walls[0]:
        return 'move': "left"
    '''
    print(you['head'])
    print(walls)

    direction = "right"
    return {
        'move': "right",
        'taunt': 'A simple taunt'
    }





# Expose WSGI app (so gunicorn can find it)
application = bottle.default_app()

if __name__ == '__main__':
    bottle.run(
        application,
        host=os.getenv('IP', '0.0.0.0'),
        port=os.getenv('PORT', '8080'),
        debug = True)
