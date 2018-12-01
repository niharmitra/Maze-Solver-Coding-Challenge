import requests
import sys
import json

# EC2 server endpoint
endpoint = "http://ec2-34-216-8-43.us-west-2.compute.amazonaws.com"
# header specified for every request
header = {"content-type": "application/json"}

reverseDirs = {"UP": "DOWN", "DOWN":"UP", "LEFT":"RIGHT", "RIGHT":"LEFT"}

def main():
	# do stuff
	access_token = startGame(1)
	print("Started a game")
	# start mazes
	params = {'token': access_token}
	mazeStatus = requests.get(endpoint+"/game", params=params, headers=header)
	if (mazeStatus.status_code != requests.codes.ok):
		print("Error trying to start mazes", file=sys.stderr)
	for i in range(mazeStatus.json()["total_levels"]):
		print("Starting maze number "+str(i))
		solveMaze(params)
	print("Solved all "+ str(i) +" mazes")

def startGame(attemptNum):
	body = {"uid": "204993636"}
	print("POST request to ", endpoint+"/session", json.dumps(body), header)
	r = requests.post(endpoint+"/session", data=json.dumps(body), headers=header)
	if (r.status_code != requests.codes.ok):
		if (attemptNum > 3):
			print("Failed to start session", file=sys.stderr)
			sys.exit(1)
		return startGame(attemptNum+1)
	print ("Token received: " + r.json()["token"])
	return r.json()["token"]

def solveMaze(params):
	mazeStatus = requests.get(endpoint+"/game", params=params, headers=header)
	if (mazeStatus.status_code != requests.codes.ok):
		print("Error trying to get game data", file=sys.stderr)
	mazeStatus = mazeStatus.json()
	if (mazeStatus["status"] == "NONE"):
		print("Session ceased to exist", file=sys.stderr)
		sys.exit(1)
	if (mazeStatus["status"] == "GAME_OVER"):
		print("Out of bounds, game over")
		sys.exit(1)
	if (mazeStatus["status"] == "FINISHED"):
		print("Finished the mazes")
		return

	mazeUnsolved = True
	# store maze as data structure, maze[y][x]
	# origin = top left, x increase left y increase down
	# value increases with where we want to go
	# wall = 0, open = 1, unexplored = 2
	maze = []
	width = mazeStatus["maze_size"][0]
	height = mazeStatus["maze_size"][1]
	for i in range(height):
		maze.append([])
		for j in range(width):
			maze[i].append(2)
	# invert the x and y because y is row and x is column
	currentPosition = [mazeStatus["current_location"][1], mazeStatus["current_location"][0]]
	print("Starting position", currentPosition)
	print("maze size is ", str(width), str(height))
	maze[currentPosition[0]][currentPosition[1]] = 1
	# Start exploring the maze, keep track of position, map, stack of moves made
	stack = []
	if (DFS(maze, currentPosition, stack, width, height, params)):
		print("Solved a maze")
		return True

	# still not done, means this square failed us
	print("Couldn't solve maze")
	print(maze)
	sys.exit(1)
	return

def DFS(maze, currentPosition, stack, width, height, params):
	# current location is unknown
	# maze[currentPosition[0]][currentPosition[1]] = 1

	# DFS clockwise: up then right then down then left
	# First check bounds, then try to reach unexplored area
	# up => y-1
	if (currentPosition[0] >= 0 and
		maze[currentPosition[0]-1][currentPosition[1]] > 1):
			stack.append("UP")
			result = move("UP", currentPosition, params)
	# right => x+1
	elif (currentPosition[1] < width and 
		maze[currentPosition[0]][currentPosition[1]+1] > 1):
			stack.append("RIGHT")
			result = move("RIGHT", currentPosition, params)
	# down => y+1
	elif (currentPosition[0] < height and
		maze[currentPosition[0]+1][currentPosition[1]] > 1):
			stack.append("DOWN")
			result = move("DOWN", currentPosition, params)
	# left => x-1
	elif (currentPosition[0] >= 0 and
		maze[currentPosition[0]][currentPosition[1]-1] > 1):
			stack.append("LEFT")
			result = move("LEFT", currentPosition, params)
	# no unexplored options, backtrack
	else:
		print (stack)
		move(stack.pop(), currentPosition, params, reverse=True)
		return DFS(maze, currentPosition, stack, width, height, params)
	
	# check the results of the move if one was made
	if (result == "WALL"):
		maze[currentPosition[0]][currentPosition[1]] = 0
		move(stack.pop(), currentPosition, params, reverse=True)
		return DFS(maze, currentPosition, stack, width, height, params)
	elif (result == "END"):
		return True
	elif (result == "OUT_OF_BOUNDS"):
		print("Out of bounds ", currentPosition)
		maze[currentPosition[0]][currentPosition[1]] = 0
		move(stack.pop(), currentPosition, params, reverse=True)
		return DFS(maze, currentPosition, stack, width, height, params)
		sys.exit(1)
	elif (result == "SUCCESS"):
		maze[currentPosition[0]][currentPosition[1]] = 1
		return DFS(maze, currentPosition, stack, width, height, params)

	# something bad happened?
	print ("Should be unreachable code", file=sys.stderr)
	return False
	

# helper function to HTTP request, reverse for when undoing stack
def move(dir, currentPosition, params, reverse=False):
	if (reverse):
		dir = reverseDirs[dir]
	# modify current position
	if (dir == "UP"):
		currentPosition[0]-=1
	elif (dir == "RIGHT"):
		currentPosition[1]+=1
	elif (dir == "DOWN"):
		currentPosition[0]+=1
	elif (dir == "LEFT"):
		currentPosition[1]-=1

	# HTTP request the dir
	body = {"action": dir}
	move = requests.post(endpoint+"/game", params=params, headers=header, data=json.dumps(body))
	if (move.status_code != requests.codes.ok):
		print("Couldn't HTTP POST a move", file=sys.stderr)
		sys.exit(1)
	# WALL, SUCCESS, OUT_OF_BOUNDS, END
	print ("moving "+dir, "from ", currentPosition)
	return move.json()["result"]

# Start program execution
main()