#/usr/bin/env python

import pygame, random
from pygame.locals import *
import os
import time

class Maze:
    global myScreen
    iteration = 0
    file = open('maze/maze.csv','w+')
    file.write("iteration" + " , " + "cellStack"
                    + " , " + "badStack"
                    + " , " + "total searched"
                    + " , " + "empty squares"
                    + " , " + "percent path"
                    + " , " + "percent wrong" + "\n")
    file.close()
    def __init__(self, mazeLayer, solveLayer):
        self.mazeArray = []
        self.state = 'c'        # c = creating, s = solving, r = reset
        self.mLayer = mazeLayer # surface
        self.sLayer = solveLayer# surface
        self.mLayer.fill((0, 0, 0, 0))
        self.sLayer.fill((0, 0, 0, 0))
        
        for y in xrange(60): # 80 wide + 60 tall
            pygame.draw.line(self.mLayer, (0,0,0,255), (0, y*8), (640, y*8))
            for x in xrange(80):
                self.mazeArray.append(0)
                if ( y == 0 ):
                    pygame.draw.line(self.mLayer, (0,0,0,255), (x*8,0), (x*8,480))
        pygame.draw.rect(self.sLayer, (0,0,255,255), Rect(0,0,8,8))
        pygame.draw.rect(self.sLayer, (255,0,255,255), Rect((632),(472),8,8))
        # Maze Section
        self.totalCells = 4800 # 80 * 60
        self.currentCell = random.randint(0, self.totalCells-1)
        self.visitedCells = 1
        self.cellStack = []
        self.compass = [(-1,0),(0,1),(1,0),(0,-1)]

    def update(self):
        if self.state == 'c':
            if self.visitedCells >= self.totalCells:
                self.currentCell = 0 # set current to top-left
                self.cellStack = []
                self.badStack = set()
                pygame.image.save(myScreen,'maze/DFSmaze' + str(self.iteration) + '.jpg')
                self.state = 's'
                return
            moved = False
            while(self.visitedCells < self.totalCells):# and moved == False):#build here
                x = self.currentCell % 80
                y = self.currentCell / 80
                neighbors = []
                for i in xrange(4):
                    nx = x + self.compass[i][0]
                    ny = y + self.compass[i][1]
                    if ((nx >= 0) and (ny >= 0) and (nx < 80) and (ny < 60)):
                        if (self.mazeArray[(ny*80+nx)] & 0x000F) == 0:
                            nidx = ny*80+nx
                            neighbors.append((nidx,1<<i))
                if len(neighbors) > 0:
                    idx = random.randint(0,len(neighbors)-1)
                    nidx,direction = neighbors[idx]
                    dx = x*8
                    dy = y*8
                    if direction & 1:
                        self.mazeArray[nidx] |= (4)
                        pygame.draw.line(self.mLayer, (0,0,0,0), (dx,dy+1),(dx,dy+7))
                    elif direction & 2:
                        self.mazeArray[nidx] |= (8)
                        pygame.draw.line(self.mLayer, (0,0,0,0), (dx+1,dy+8),(dx+7,dy+8))
                    elif direction & 4:
                        self.mazeArray[nidx] |= (1)
                        pygame.draw.line(self.mLayer, (0,0,0,0), (dx+8,dy+1),(dx+8,dy+7))
                    elif direction & 8:
                        self.mazeArray[nidx] |= (2)
                        pygame.draw.line(self.mLayer, (0,0,0,0), (dx+1,dy),(dx+7,dy))
                    self.mazeArray[self.currentCell] |= direction
                    self.cellStack.append(self.currentCell)
                    self.currentCell = nidx
                    self.visitedCells = self.visitedCells + 1
                    moved = True
                else:
                    self.currentCell = self.cellStack.pop()
        elif self.state == 's':
            if self.currentCell == (self.totalCells-1): # have we reached the exit?            
                self.state = 'r'
                return
            moved = False
            while(self.currentCell != (self.totalCells-1)):#moved == False):
                x = self.currentCell % 80
                y = self.currentCell / 80
                neighbors = []
                directions = self.mazeArray[self.currentCell] & 0xF
                for i in xrange(4):
                    if (directions & (1<<i)) > 0:
                        nx = x + self.compass[i][0]
                        ny = y + self.compass[i][1]
                        if ((nx >= 0) and (ny >= 0) and (nx < 80) and (ny < 60)):              
                            nidx = ny*80+nx
                            if ((self.mazeArray[nidx] & 0xFF00) == 0): # make sure there's no backtrack
                                neighbors.append((nidx,1<<i))
                if len(neighbors) > 0:
                    idx = random.randint(0,len(neighbors)-1)
                    nidx,direction = neighbors[idx]
                    dx = x*8
                    dy = y*8
                    if direction & 1:
                        self.mazeArray[nidx] |= (4 << 12)
                    elif direction & 2:
                        self.mazeArray[nidx] |= (8 << 12)
                    elif direction & 4:
                        self.mazeArray[nidx] |= (1 << 12)
                    elif direction & 8:
                        self.mazeArray[nidx] |= (2 << 12)
                    pygame.draw.rect(self.sLayer, (0,255,0,255), Rect(dx,dy,8,8))
                    self.mazeArray[self.currentCell] |= direction << 8
                    self.cellStack.append(self.currentCell)
                    self.currentCell = nidx
                    moved = True
                else:
                    pygame.draw.rect(self.sLayer, (255,0,0,255), Rect((x*8),(y*8),8,8))
                    self.mazeArray[self.currentCell] &= 0xF0FF # not a solution
                    self.badStack.add(self.currentCell)
                    self.currentCell = self.cellStack.pop()
        elif self.state == 'r':
            print "length of cellStack: %s" % len(self.cellStack)
            print "length of badStack: %s" % len(self.badStack)
            directory = 'maze'
            if not os.path.exists(directory):
                os.makedirs(directory)
            pygame.image.save(myScreen,'maze/DFSmazeSolution' + str(self.iteration) + '.jpg')
            self.iteration = self.iteration + 1
            with open("maze/maze.csv", "a") as myfile:
                myfile.write(str(self.iteration-1) + " , "+ str(len(self.cellStack)) + " , " + 
                    str(len(self.badStack)) + " , " + 
                    str(len(self.badStack)+len(self.cellStack)) + " , " + 
                    str((80*60)-len(self.badStack)-len(self.cellStack)) + " , " + 
                    str("{0:.2f}".format(100*float((len(self.cellStack))/float((80*60))))) + " , " + 
                    str("{0:.2f}".format(100*float(len(self.badStack))/float((80*60)))) + " , " + "\n")
            #raw_input("Press Enter to continue...")
            #time.sleep(2)
            self.__init__(self.mLayer,self.sLayer)
            #os._exit(0)

    def draw(self, screen):
        screen.blit(self.sLayer, (0,0))
        screen.blit(self.mLayer, (0,0))

myScreen = 0
def main():
    """Maze Main Function - Luke Arntson, Jan '09
        Written using - http://www.mazeworks.com/mazegen/mazetut/index.htm
    """
    global myScreen
    pygame.init()
    myScreen = pygame.display.set_mode((640, 480))
    pygame.display.set_caption('Labyrinth')
    pygame.mouse.set_visible(0)
    background = pygame.Surface(myScreen.get_size())
    background = background.convert()
    background.fill((255, 255, 255))
    mazeLayer = pygame.Surface(myScreen.get_size())
    mazeLayer = mazeLayer.convert_alpha()
    mazeLayer.fill((0, 0, 0, 0))
    solveLayer = pygame.Surface(myScreen.get_size())
    solveLayer = solveLayer.convert_alpha()
    solveLayer.fill((0, 0, 0, 0))
    newMaze = Maze(mazeLayer,solveLayer)
    myScreen.blit(background, (0, 0))
    pygame.display.flip()
    while 1:
        for event in pygame.event.get():
            if event.type == QUIT:
                return
            elif event.type == KEYDOWN and event.key == K_ESCAPE:
                return
        newMaze.update()
        myScreen.blit(background, (0, 0))
        newMaze.draw(myScreen)
        pygame.display.flip()

if __name__ == '__main__': main()
