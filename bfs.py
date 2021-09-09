import os, sys
import subprocess
import pygame
import random
import time
import numpy as np
ESCAPE = 27
KEYUP = 273
KEYDOWN = 274
KEYRIGHT = 275
KEYLEFT = 276

MOVE_UP = pygame.USEREVENT + 1
MOVE_DOWN = pygame.USEREVENT + 2
MOVE_LEFT = pygame.USEREVENT + 3
MOVE_RIGHT = pygame.USEREVENT + 4

# Creates an mxn grid, each square is of size SIZE
m = 40
n = 30
SIZE = 20
WIDTH = m * SIZE
HEIGHT = n * SIZE

class Head:
    """Head of the snake"""
    def __init__(self):
        self._direction = [0, 0]
        self._head_position = [10*SIZE, 10*SIZE]

    def update(self, pygame_event):
        """Moves the head according to the event"""
        if pygame_event.type in [pygame.KEYDOWN, MOVE_UP, MOVE_DOWN, MOVE_LEFT, MOVE_RIGHT]:
            if pygame_event.type == pygame.KEYDOWN:
                key = pygame_event.dict["key"]
                if (key == KEYUP or key == ord('w')) and self._direction != [0,SIZE]:
                    self._direction = [0,-SIZE]
                
                if (key == KEYDOWN or key == ord('s')) and self._direction != [0,-SIZE]:
                    self._direction = [0,SIZE]

                if (key == KEYLEFT or key == ord('a')) and self._direction != [SIZE,0]:
                    self._direction = [-SIZE,0]
                
                if (key == KEYRIGHT or key == ord('d')) and self._direction != [-SIZE,0]:
                    self._direction = [SIZE,0]
            if pygame_event.type == MOVE_UP and self._direction != [0,SIZE]:
                self._direction = [0,-SIZE]
            if pygame_event.type == MOVE_DOWN and self._direction != [0,-SIZE]:
                self._direction = [0,SIZE]
            if pygame_event.type == MOVE_LEFT and self._direction != [SIZE,0]:
                self._direction = [-SIZE,0]
            if pygame_event.type == MOVE_RIGHT and self._direction != [-SIZE,0]:
                self._direction = [SIZE,0]

        self._head_position[0] += self._direction[0]
        self._head_position[1] += self._direction[1]

if not pygame.font:
    print("Fonts disabled")

if not pygame.mixer:
    print("Sound disabled")

def coords_to_grid(pos):
    return [int(pos[0]/SIZE), n-1-int(pos[1]/SIZE)]

### Implementation of the BFS algorithm
def grid_bfs(grid, start, end):
    visited = [[False for _ in range(len(grid[0]))] for _ in range(len(grid))]
    queue = []
    queue.append(start)
    prev = [[None for _ in range(len(grid[0]))] for _ in range(len(grid))] # Stores the previous nodes in the path
    path = []
    while (len(queue) != 0):
        current_pos = queue[0]
        queue.pop(0)
        for neighbor in neighbors(grid,current_pos):
            neighbor_x,neighbor_y = neighbor
            if visited[neighbor_x][neighbor_y] == False:
                visited[neighbor_x][neighbor_y] = True
                prev[neighbor_x][neighbor_y] = current_pos
                queue.append([neighbor_x,neighbor_y])
                if [neighbor_x,neighbor_y] == end:
                    break
    pos = end
    path.append(end)
    while pos != start and pos != None:
        pos_x, pos_y = pos
        path.append(prev[pos_x][pos_y])
        pos = prev[pos_x][pos_y]
    return path

ds = [[0,-1],[0,1],[1,0],[-1,0]]
def formatting(path):
    ordered_moves = []
    if any([path[_]==None for _ in range(len(path))]):
        return [-1]
    i = 1
    while i < len(path):
        for k in range(0,4):
            if (np.array(path[i]) - np.array(path[i-1]) == np.array(ds[k])).all():
                ordered_moves.append(k)
        i+=1
    return ordered_moves

def neighbors(grid, pos):
    i,j = pos
    neighbors = []
    for [dx,dy] in ds:
        if (0 <=(i+dx) and i+dx < len(grid)) and (0<= j+dy and j+dy < len(grid[0])):
            if grid[i+dx][j+dy] == 0:
                neighbors.append([i+dx, j+dy])
    return neighbors
###

def main(render, savegif=False):
    # Start the screen for the game
    pygame.init()        
    my_clock = pygame.time.Clock()

    head = Head()
    head._direction = [0,0]
    snake = 5*[list(head._head_position)]
    snaketip = list(head._head_position)
    
    apple = [0,0]
    apple[0] = SIZE*np.random.randint(0,m)        
    apple[1] = SIZE*np.random.randint(0,n)
    
    # Create the grid for the first time:
    my_grid = [[0 for _ in range(0,n)] for _ in range(m)]
    
    score = 0
    counter = 0

    if render:
        main_surface = pygame.display.set_mode((WIDTH,HEIGHT))
    my_event = pygame.event.Event(pygame.NOEVENT)
    loops = 0
    direction = -1
    path = []


    # Prepares imagelist to save GIF:
    if savegif:
        imagelist = []
        filenamelist = []
        pic_count = 0

    while True:
        # Save GIF:
        if savegif:
            filenamelist.append("pic" + str(pic_count) + ".png")
            pygame.image.save(main_surface, filenamelist[pic_count])
            pic_count+=1

        if len(path) == 0:
        # Run BFS algorithm to find the path
            path = formatting(grid_bfs(my_grid, coords_to_grid(snaketip), coords_to_grid(apple)))
            continue
        direction = path.pop()
        
        # Update the grid on each new step
        my_grid = [[0 for _ in range(0,n)] for _ in range(m)]
        my_grid[coords_to_grid(apple)[0]][coords_to_grid(apple)[1]] = 1
        if direction != -1:
            my_event = pygame.event.Event(MOVE_UP + direction)
        if direction == -1:
            my_event = pygame.event.Event(MOVE_UP)

        if render:
            main_surface.fill((220,220,220))         
        head.update(my_event)

        snaketip=list(head._head_position)
        snake = snake[1:]
        snake.append(snaketip)

        
        if snaketip == apple:
            score += 1
            while snake.count(apple)>0:
                apple[0] = SIZE*(random.uniform(0,m)//1)
                apple[1] = SIZE*(random.uniform(0,n)//1)
            snake = snake + 2*[snaketip]
            #print(score)
        
        # Boundary checks
        if head._head_position[0] < 0:
            break
        elif head._head_position[0] >= WIDTH:
            break
        elif head._head_position[1] < 0:
            break
        elif head._head_position[1] >= HEIGHT:
            break
        # Check if snake bits itself
        if snake.count(snaketip)==2:
            break     

        # Refresh positions of snake on the grid
        for [x,y] in snake[:-1]:
            my_grid[coords_to_grid([x,y])[0]][coords_to_grid([x,y])[1]] = 1

        if render:
            for i in range(0,len(snake)):       
                main_surface.fill((0,180,0),snake[i]+[SIZE,SIZE])
            main_surface.fill((0,120,0),snake[len(snake)-1]+[SIZE,SIZE]) 
        
            main_surface.fill((200,0,0),apple+[SIZE,SIZE])
        
            pygame.display.flip()
            my_clock.tick(30)
    
    if savegif:
        #Combine into a GIF using ImageMagick's "convert"-command (called using subprocess.call()):
        convertexepath = "C:/Program Files/ImageMagick-7.1.0-Q16-HDRI/convert.exe"  # Hardcoded
        convertcommand = [convertexepath, "-delay", "10", "-size", str(800) + "x" + str(600)] + filenamelist + ["anim.gif"]
        subprocess.call(convertcommand)
        
        #Remove the PNG files (if they were meant to be temporary):
        for filename in filenamelist:
            os.remove(filename)


    pygame.quit()
    return score
    

if __name__ == "__main__":
    iterations = 1000
    results = []
    render = True
    for _ in range(iterations):
        if _%10 == 0:
            print(f"Iteration number {_}")
        result = main(render)
        results.append(result)

    from collections import Counter
    print(Counter(results))

    print(f"The mean score was {np.mean(results)}")
    print(f"The standard deviation was {np.std(results)}")