from collections import defaultdict
import getch
import numpy as np
import os
import time

# Libraries for keyboard input
import curses

class intCodeComputer:
    def __init__(self, filename, stdscr):
        
        # Setting an output screen
        self.stdscr=stdscr
        self.stdscr.clear()
            
        self.program = defaultdict(lambda:'0')
        with open(filename, 'r') as f:
            line = f.readline()
        for i, code in enumerate(line.split(',')):
            self.program[i] = code

        self.memory_location = 0  
        self.relative_base = 0
        self.intcode_dict = {'01':4, '02':4, '03':2, '04':2, '05':3, '06':3, '07':4, '08':4, 
                             '09':2, '99':0}
        
        self.screenOutputs = [] # List to store groups of 3 outputs
        self.nBlockTiles = 0
        self.gameScore = 0
        
        # To keep tabs on screen render size
        self.maxX = 0
        self.maxY = 0
        
        # I want to keep tabs on the paddle x and ball x coordinate
        self.paddleX = 0
        self.ballX = 0
        
        # To adjust render times 
        self.gameStart = 0
        
        # Dictionary to render tiles
        self.gameItemId = {'0':" ", '1':"#", '2':'=', '3':"-", '4':"o"}
        
    def process_parameter(self, parameter_mode, offset):
        if(parameter_mode == '0'):
            return self.program[int(self.program[self.memory_location + offset])]
        elif(parameter_mode == '1'):
            return self.program[self.memory_location + offset]
        elif(parameter_mode == '2'):
            relative_mode_parameter = int(self.program[self.memory_location + offset])
            return self.program[self.relative_base + relative_mode_parameter]
    
    # Renders game screen
    def renderOutput(self):
        x, y, tileId = self.screenOutputs
        
        # Game screen is getting updated
        if (x != '-1' and y != '0'):
            self.stdscr.addch(int(y), int(x), self.gameItemId[tileId])
            
            if (int(x) > self.maxX):
                self.maxX = int(x)
            if (int(y) > self.maxY):
                self.maxY = int(y)
            
            if(tileId == '2'):
                self.nBlockTiles += 1
                
            if(tileId == '4'):
                self.ballX = int(x)
               
            if(tileId == '3'): 
                self.paddleX = int(x)
                
        else: # gameScore is getting updated
            self.gameScore = tileId
        
        if self.gameStart:
            time.sleep(0.01)
            
        self.stdscr.refresh()
        
    def movePaddle(self):
        # Modify user input if any key press is detected. Else set it to zero
        #key = self.stdscr.getch()
        #if  (key == curses.KEY_LEFT):
        #    self.user_input = str(-1)
        #elif (key == curses.KEY_RIGHT):
        #    self.user_input = str(1)
        #else:
        #    self.user_input = str(0)
            
        #curses.flushinp()
        if (self.paddleX < self.ballX):
               self.user_input = '1'
        elif (self.paddleX > self.ballX):
               self.user_input = '-1'
        else:
               self.user_input = '0'
            
    def execute_program(self, user_input = None):
        self.user_input = user_input
        if(self.user_input):
            self.program[0] = str(self.user_input)
            
        # Once the loop starts, user_input is modified by key presses
        while(True):
            p_opcode = self.program[self.memory_location]
            p_opcode = p_opcode.zfill(5)
            a, b, c, de = p_opcode[0], p_opcode[1], p_opcode[2], p_opcode[3:]

            if(de == '01'):
                parameter1 = self.process_parameter(c, 1)
                parameter2 = self.process_parameter(b, 2) 
                parameter3 = int(self.program[self.memory_location+3])
                if(a == '2'):
                    parameter3 += self.relative_base
                    
                self.program[parameter3] = str(int(parameter1) + int(parameter2))
                self.memory_location += self.intcode_dict[de]
                continue

            if(de == '02'):
                parameter1 = self.process_parameter(c, 1) 
                parameter2 = self.process_parameter(b, 2)
                parameter3 = int(self.program[self.memory_location+3])
                if(a == '2'):
                    parameter3 += self.relative_base
                    
                self.program[parameter3] = str(int(parameter1) * int(parameter2))
                self.memory_location += self.intcode_dict[de]
                continue

            if(de == '03'):
                # This where the paddle moving is being controlled
                # The first time it tries to user input signifies start of the game
                if not self.gameStart:
                    self.gameStart = 1
                    
                self.movePaddle()
                if(c == '0'):
                    parameter1 = int(self.program[self.memory_location + 1])
                elif(c == '1'):
                    print("I shouldn't be here")
                    parameter1 = int(self.memory_location + 1)                    
                elif(c == '2'):
                    parameter1 = self.relative_base + int(self.program[self.memory_location + 1])
                    
                self.program[parameter1] = self.user_input                    
                self.memory_location += self.intcode_dict[de]
                continue

            if(de == '04'):
                # Instead of printing to console, we now render
                # output to a screen
                parameter1 = self.process_parameter(c, 1)
                self.screenOutputs.append(parameter1)
                #print("Here: {}".format(parameter1))
                
                if(len(self.screenOutputs) == 3):
                    self.renderOutput()
                    self.screenOutputs = []
                
                self.memory_location += self.intcode_dict[de]
                continue

            if(de == '05'):
                parameter1 = self.process_parameter(c, 1)
                parameter2 = self.process_parameter(b, 2)
                # print("Got here. Parameter 1, 2: {}, {}".format(parameter1, parameter2))

                if(int(parameter1) != 0):
                    self.memory_location = int(parameter2)
                else:        
                    self.memory_location += self.intcode_dict[de]

                continue

            if(de == '06'):
                parameter1 = self.process_parameter(c, 1)
                parameter2 = self.process_parameter(b, 2)

                if(int(parameter1) == 0):
                    self.memory_location = int(parameter2)
                else:        
                    self.memory_location += self.intcode_dict[de]

                continue

            if(de == '07'):
                parameter1 = int(self.process_parameter(c, 1))
                parameter2 = int(self.process_parameter(b, 2))
                parameter3 = int(self.program[self.memory_location+3])
                if(a == '2'):
                    parameter3 += self.relative_base

                if(parameter1 < parameter2):
                    self.program[parameter3] = '1'
                else:        
                    self.program[parameter3] = '0'

                self.memory_location += self.intcode_dict[de]
                continue

            if(de == '08'):
                parameter1 = int(self.process_parameter(c, 1))
                parameter2 = int(self.process_parameter(b, 2))
                parameter3 = int(self.program[self.memory_location+3])
                if(a == '2'):
                    parameter3 += self.relative_base
                    
                if(parameter1 == parameter2):
                    self.program[parameter3] = '1'
                else:        
                    self.program[parameter3] = '0'

                self.memory_location += self.intcode_dict[de]
                continue
            
            if(de == '09'):
                parameter1 = self.process_parameter(c, 1)
                self.relative_base += int(parameter1)
                self.memory_location += self.intcode_dict[de]
                continue                

            if(de == '99'):
                score_str = "\n\nNumber of blocks rendered: {}".format(self.nBlockTiles)
                self.stdscr.addnstr(self.maxY, 0, score_str, len(score_str))
                break

def main(stdscr):
    curses.noecho() # Don't echo user input to terminal
    # curses.cbreak() # Don't require endline to accept input
    curses.curs_set(0) # Hide cursor
    stdscr.keypad(True) # Make curses give "nice" values for keypad
    stdscr.nodelay(1) # Non blocking getch
    
    input_file = 'day13_input'
    myComputer = intCodeComputer(input_file, stdscr)
    myComputer.execute_program(2) # Free quarters - yay!
    curses.endwin()
    print('Final score: ', myComputer.gameScore)
    
curses.wrapper(main)