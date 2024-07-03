## Assignment 1
## AYSENUR GÜLLER 27796
## MELTEM CEYLANTEKİN 28089
#%%
import copy
import heapq
import time
import resource
from tabulate import tabulate


DIRECTION = ['UP','DOWN','LEFT','RIGHT']
epsilon = 1e-5

class Node:
    #This is the node structure that hods states
    def __init__(self, state, f_function, h_function, g_functiom, parent=None, direction=None):
        self.state = state  # Matrix representing the state
        self.f_function = f_function    # f_function()= g(n)+h(n)
        self.h_function= h_function #Heuristic function cost
        self.g_function= g_functiom #Movement step cost + parent cost
        self.parent = parent  # Reference to the parent Node
        self.direction = direction  # String representing the direction
    def __lt__(self, other):
        return self.f_function < other.f_function

class PriorityQueue:
    #This is the Priority Queue that used as frontier data structure
    def __init__(self):
        self.heap = []
        self.counter = 0  # Tiebreaker counter

    def push(self, node):
        heapq.heappush(self.heap, (node.f_function, self.counter, node))
        self.counter += 1

    def pop(self, state_to_remove=None):
        if self.heap:
            if state_to_remove:
                # Remove the node with the specified state
                index_to_remove = next(
                    i for i, (_, _, node) in enumerate(self.heap) if node.state == state_to_remove
                )
                return self.heap.pop(index_to_remove)[2]
            else:
                return heapq.heappop(self.heap)[2]
        else:
            raise IndexError("pop from an empty priority queue")

    def is_empty(self):
        return len(self.heap) == 0
    
    def contains_state(self, state):
        return any(node[2].state == state for node in self.heap)
    
    def get_existing_node(self, state):
        return next((node[2] for node in self.heap if node[2].state == state), None)
    
    def __str__(self):
        return "\n".join(str(node[2].state) for node in self.heap)

class ClosedList:
    def __init__(self):
        self.nodes = []

    def add_node(self, node):
        self.nodes.append(node)
    
    def remove_node(self, state):
        state_tuple = tuple(map(tuple, state))
        self.nodes = [node for node in self.nodes if node.state != state_tuple]

    def contains_state(self, state):
    # Check if any node in the list has a state equal to the argument's state
        return any(existing_node.state == state for existing_node in self.nodes)
    
    def get_existing_node(self, state):
        return next((existing_node for existing_node in self.nodes if existing_node.state == state), None)


def print_state(board):
#This function prints states as matrix format
    for row in board:
        print("[", end=" ")
        for element in row:
            print(f"'{element}' ", end=" ")
        print("]")

def print_path_info_reversed(node):
    """When solution founded, prints the states and directions in reverse order from the root to the goal node."""
    path = []  # Create an empty list to store states and directions
    while node is not None:
        path.append((node.state, node.direction,node.f_function,node.h_function,node.g_function))  # Append state and direction to the list
        node = node.parent
    
    # Print the path in reverse order
    if path:
        print("Path (from root):")
        for state, direction,f,h,g in reversed(path):
            if(direction==None):
                print("Root Node")
            else:
                print("Direction:", direction)
            print("F value:",f )
            print("H value:",h )
            print("G value:",g )
            print("State:")
            print_state(state)
            print("------------------------------------------")

 
def findAgentPosition(board):
    #Find the position of agent which denoted by 'S'
    for i in range(len(board)):
        for j in range(len(board[i])):
            if board[i][j] == 'S':
                return (i, j) 
    return None 

def is_goal(board):
    # If there is no 0 in the board, returns tru
    return all('0' not in row for row in board)

def color_board(board,x,y,color):
     #Color the cell at given x,y with given color
     board[x][y]=color
     return board

def step_cost(direction, matrix):
    #Calculates the cost of the possible movement
    directions = {
        'UP': (-1, 0),
        'DOWN': (1, 0),
        'LEFT': (0, -1),
        'RIGHT': (0, 1)
    }

    start_cell = findAgentPosition(matrix)
    row, col = start_cell
    cost = 0

    while 0 <= (row+directions[direction][0]) < len(matrix) and 0 <= (col+ directions[direction][1]) < len(matrix[0]) and matrix[row+ directions[direction][0]][col+directions[direction][1]] != 'X':
        matrix=color_board(matrix,row,col,'1') #Color the board with agent positioning
        cost += 1
        row += directions[direction][0]
        col += directions[direction][1]
    matrix=color_board(matrix,row,col,'S')
    return max(cost, epsilon)  # Ensure the cost is ≥ ε
   
def heuristic(board,admissibility) :
    #Takes parameter to decide admissible and inadmissible heuristic
    if(admissibility=="inadmissible") :
        #Inadmissible heuristic which overestimate the true cost 
        num_to_color=len(board)*len(board[0])
        return num_to_color
    else:
        #Admissible heuristic function which never overestimate the true cost
        num_uncolored = 0
        for row in board:
            num_uncolored += row.count('0')
        return num_uncolored
    
def  SUCC_H(parent,admissibility):
    #For each direction, creates successor nodes
    successors=[]
    for direction in DIRECTION:
        curr_board= parent.state
        parent_cost=parent.g_function  
        new_board=copy.deepcopy(curr_board)
        move_cost=step_cost(direction,new_board)
        if(move_cost==epsilon):
            continue
        else:    
            h_function= heuristic(new_board,admissibility)
            g_function=move_cost+parent_cost
            f_function= g_function+h_function
            succ_Node= Node(new_board,f_function,h_function,g_function,parent,direction)
            successors.append(succ_Node)
    return successors
      

def A_Star(board,admissibility):
    expanded_node_count=0
    total_distance=0
    closed_list = ClosedList()
    frontier = PriorityQueue()
    initial_node=Node(board,0+heuristic(board,admissibility),heuristic(board,admissibility),0,None,None)
    frontier.push(initial_node)

    while not frontier.is_empty():
        expanded_node=frontier.pop()
        expanded_node_count+=1
        """print("Expanded Node:")"""
        """print_state(expanded_node.state)
        print(expanded_node.f_function)"""
        if(not expanded_node.g_function==None):
            total_distance+=expanded_node.g_function
        if(is_goal(expanded_node.state)):
             #return solution
            total_travel=0
            if(not expanded_node.g_function==None):
                total_travel=expanded_node.g_function
            print("Solution founded")
            print_path_info_reversed(expanded_node)
            return total_distance,expanded_node_count,total_travel
            break
        else:
            for s in SUCC_H(expanded_node,admissibility):
                if not (closed_list.contains_state(s.state) or frontier.contains_state(s.state)):    
                    frontier.push(s)
                elif(frontier.contains_state(s.state)):
                    exists_node=frontier.get_existing_node(s.state)
                    if(exists_node.f_function > s.f_function):
                        frontier.pop(exists_node.state)
                        frontier.push(s)
                elif(closed_list.contains_state(s.state)):
                    exists_node= closed_list.get_existing_node(s.state)
                    if(exists_node.f_function > s.f_function):
                        closed_list.remove_node(exists_node.state)
                        frontier.push(s)
                    
            closed_list.add_node(expanded_node)
        while(frontier.is_empty()):
            print("No solution founded!")
            return total_distance,expanded_node_count,0
     

################## EASYYYY
#One way to choose (Only one successor)
easy1 = [
    ['X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X'],
    ['X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X'],
    ['X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X'],
    ['X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X'],
    ['X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X'],
    ['X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X'],
    ['X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X'],
    ['X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X'],
    ['X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X'],
    ['0', '0', '0', '0', '0', '0', '0', '0', '0', 'S', 'X', 'X'],
    ['X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X'],
    ['X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X']
]

#Two possible way (Two successors)
easy2=[
    ['X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', '0','X','X'],
    ['X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', '0','X','X'],
    ['X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', '0','X','X'],
    ['X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', '0','X','X'],
    ['X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', '0','X','X'],
    ['X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', '0','X','X'],
    ['X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', '0','X','X'],
    ['X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', '0','X','X'],
    ['X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', '0','X','X'],
    ['S', '0', '0', '0', '0', '0', '0', '0', '0', '0','X','X'],
    ['X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X','X','X'],
    ['X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X','X','X']
]

easy3=[
    ['S', '0', 'X', 'X','X', 'X', 'X', 'X', 'X', 'X','X','X'],
    ['X', '0', 'X', 'X','X', 'X', 'X', 'X', 'X', 'X','X','X'],
    ['X', '0', 'X', 'X','X', 'X', 'X', 'X', 'X', 'X','X','X'],
    ['X', '0', 'X', 'X','X', 'X', 'X', 'X', 'X', 'X','X','X'],
    ['X', '0', 'X', 'X','X', 'X', 'X', 'X', 'X', 'X','X','X'],
    ['X', '0', 'X', 'X','X', 'X', 'X', 'X', 'X', 'X','X','X'],
    ['X', '0', 'X', 'X','X', 'X', 'X', 'X', 'X', 'X','X','X'],
    ['X', '0', 'X', 'X','0', 'X', 'X', 'X', 'X', 'X','X','X'],
    ['X', '0', 'X', 'X','0', 'X', 'X', 'X', 'X', 'X','X','X'],
    ['X', '0', 'X', 'X','0', 'X', 'X', 'X', 'X', 'X','X','X'],
    ['X', '0', 'X', 'X','0', 'X', 'X', 'X', 'X', 'X','X','X'],
    ['X', '0', '0', '0','0', 'X', 'X', 'X', 'X', 'X','X','X']
]

#No Solution Board (No solution)
easy4=[
    ['S', '0', 'X', 'X','X', 'X', 'X', 'X', 'X', 'X','X','X'],
    ['X', '0', 'X', 'X','X', 'X', 'X', 'X', 'X', 'X','X','X'],
    ['X', '0', 'X', 'X','X', 'X', 'X', 'X', 'X', 'X','X','X'],
    ['X', '0', 'X', 'X','X', 'X', 'X', 'X', 'X', 'X','X','X'],
    ['X', '0', 'X', 'X','X', 'X', 'X', 'X', '0', 'X','X','X'],
    ['X', '0', 'X', 'X','X', 'X', 'X', 'X', 'X', 'X','X','X'],
    ['X', '0', 'X', 'X','X', 'X', 'X', 'X', 'X', 'X','X','X'],
    ['X', '0', 'X', 'X','X', 'X', 'X', 'X', 'X', 'X','X','X'],
    ['X', '0', 'X', 'X','X', 'X', 'X', 'X', 'X', 'X','X','X'],
    ['X', '0', 'X', 'X','X', 'X', 'X', 'X', 'X', 'X','X','X'],
    ['X', '0', 'X', 'X','X', 'X', 'X', 'X', 'X', 'X','X','X'],
    ['X', '0', 'X', 'X','X', 'X', 'X', 'X', 'X', 'X','X','X']
]

easy5 = [
    ['0', 'X', 'X', 'X','X', 'X', 'X', 'X', 'X', 'X','X','X'],
    ['0', 'X', 'X', 'X','X', 'X', 'X', 'X', 'X', 'X','X','X'],
    ['0', 'X', 'X','X', 'X', 'X', 'X', 'X', 'X', 'X','X','X'],
    ['0', 'X', 'X','X', 'X', 'X', 'X', 'X', 'X', 'X','X','X'],
    ['0', '0', 'S', '0','0', 'X', 'X', 'X', 'X', 'X','X','X'],
    ['X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X','X','X'],
    ['X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X','X','X'],
    ['X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X','X','X'],
    ['X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X','X','X'],
    ['X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X','X','X'],
    ['X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X','X','X'],
    ['X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X','X','X']
    ]

########################### NORMAL
#Made sequantial decision comparing easy1
normal1= [
    ['X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X'],
    ['X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X'],
    ['X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X'],
    ['X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X'],
    ['0', '0', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X'],
    ['0', '0', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X'],
    ['0', '0', '0', '0', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X'],
    ['0', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X'],
    ['0', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X'],
    ['0', '0', '0', '0', '0', '0', '0', '0', '0', 'S', 'X', 'X'],
    ['X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X'],
    ['X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X']
]

normal2=[
    ['X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X'],
    ['X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X'],
    ['X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X'],
    ['X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X'],
    ['X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', '0'],
    ['X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', '0'],
    ['X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', '0'],
    ['X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', '0'],
    ['X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', '0'],
    ['0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0'],
    ['X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'S', 'X'],
    ['X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X']
]
normal3=[
    ['S', '0', '0', '0','0', 'X', 'X', 'X', 'X', 'X','X','X'],
    ['X', '0', 'X', 'X','0', 'X', 'X', 'X', 'X', 'X','X','X'],
    ['X', '0', 'X', 'X','0', 'X', 'X', 'X', 'X', 'X','X','X'],
    ['X', '0', 'X', 'X','0', 'X', 'X', 'X', 'X', 'X','X','X'],
    ['X', '0', 'X', 'X','X', 'X', 'X', 'X', 'X', 'X','X','X'],
    ['X', '0', 'X', 'X','X', 'X', 'X', 'X', 'X', 'X','X','X'],
    ['X', '0', 'X', 'X','X', 'X', 'X', 'X', 'X', 'X','X','X'],
    ['X', '0', 'X', 'X','X', 'X', 'X', 'X', 'X', 'X','X','X'],
    ['X', '0', 'X', 'X','X', 'X', 'X', 'X', 'X', 'X','X','X'],
    ['X', '0', 'X', 'X','X', 'X', 'X', 'X', 'X', 'X','X','X'],
    ['X', '0', 'X', 'X','X', 'X', 'X', 'X', 'X', 'X','X','X'],
    ['X', '0', 'X', 'X','X', 'X', 'X', 'X', 'X', 'X','X','X']
]
normal4=[
    ['S', '0', 'X', '0','0', '0', '0', '0', '0', 'X','X','X'],
    ['X', '0', '0', '0','X', 'X', 'X', 'X', '0', 'X','X','X'],
    ['X', 'X', 'X', '0','X', 'X', 'X', 'X', '0', 'X','X','X'],
    ['X', '0', '0', '0','X', 'X', 'X', 'X', '0', 'X','X','X'],
    ['X', '0', 'X', 'X','X', 'X', 'X', 'X', '0', 'X','X','X'],
    ['X', '0', 'X', 'X','X', 'X', 'X', 'X', 'X', 'X','X','X'],
    ['X', '0', 'X', 'X','X', 'X', 'X', 'X', 'X', 'X','X','X'],
    ['X', '0', 'X', 'X','X', 'X', 'X', 'X', 'X', 'X','X','X'],
    ['X', '0', 'X', 'X','X', 'X', 'X', 'X', 'X', 'X','X','X'],
    ['X', '0', 'X', 'X','X', 'X', 'X', 'X', 'X', 'X','X','X'],
    ['X', '0', 'X', 'X','X', 'X', 'X', 'X', 'X', 'X','X','X'],
    ['X', '0', 'X', 'X','X', 'X', 'X', 'X', 'X', 'X','X','X']
]
normal5 = [
    ['0', 'X', 'X', 'X','0', '0', '0', 'X', 'X', 'X','X','X'],
    ['0', 'X', 'X', 'X','0', 'X', '0', 'X', 'X', 'X','X','X'],
    ['0', 'X', 'X','X', '0', 'X', '0', 'X', 'X', 'X','X','X'],
    ['0', 'X', 'X','X', '0', 'X', '0', 'X', 'X', 'X','X','X'],
    ['0', '0', 'S', '0','0', '0', '0', 'X', 'X', 'X','X','X'],
    ['0', 'X', 'X', 'X', 'X', 'X', '0', 'X', 'X', 'X','X','X'],
    ['0', 'X', 'X', 'X', 'X', 'X', '0', 'X', 'X', 'X','X','X'],
    ['0', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X','X','X'],
    ['0', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X','X','X'],
    ['0', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X','X','X'],
    ['X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X','X','X'],
    ['X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X','X','X']
]

############### DIFFICULT
difficult1= [
    ['X', 'X', 'S', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X'],
    ['X', 'X', '0', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X'],
    ['0', '0', '0', '0', '0', '0', '0', 'X', 'X', 'X', 'X', 'X'],
    ['0', 'X', 'X', '0', 'X', 'X', '0', 'X', 'X', 'X', 'X', 'X'],
    ['0', 'X', 'X', '0', 'X', 'X', '0', 'X', 'X', 'X', 'X', 'X'],
    ['0', '0', '0', '0', 'X', 'X', '0', '0', '0', '0', 'X', 'X'],
    ['X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', '0', 'X', 'X'],
    ['X', 'X', 'X', 'X', '0', '0', 'X', 'X', 'X', '0', 'X', 'X'],
    ['X', 'X', 'X', 'X', 'X', '0', '0', '0', 'X', '0', 'X', 'X'],
    ['X', 'X', 'X', 'X', 'X', 'X', 'X', '0', '0', '0', 'X', 'X'],
    ['X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X'],
    ['X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X']
 ]

difficult2= [
    ['X', 'X', 'X', 'X', '0', 'S', '0', 'X', 'X', 'X', 'X', 'X'],
    ['X', 'X', 'X', 'X', '0', 'X', 'X', 'X', 'X', 'X', 'X', 'X'],
    ['0', '0', '0', '0', '0', '0', '0', 'X', 'X', 'X', 'X', 'X'],
    ['0', 'X', 'X', '0', 'X', 'X', '0', 'X', 'X', 'X', 'X', 'X'],
    ['0', 'X', 'X', '0', 'X', 'X', '0', 'X', 'X', 'X', 'X', 'X'],
    ['0', '0', '0', '0', 'X', 'X', '0', '0', '0', '0', 'X', 'X'],
    ['X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', '0', 'X', 'X'],
    ['X', 'X', 'X', 'X', '0', '0', 'X', 'X', 'X', '0', 'X', 'X'],
    ['X', 'X', 'X', 'X', 'X', '0', '0', '0', 'X', '0', 'X', 'X'],
    ['X', 'X', 'X', 'X', 'X', 'X', 'X', '0', '0', '0', 'X', 'X'],
    ['X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X'],
    ['X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X']
 ]
difficult3= [
    ['X', 'X', 'X', 'X', '0', 'S', '0', 'X', 'X', 'X', 'X', 'X'],
    ['X', 'X', 'X', 'X', '0', 'X', 'X', 'X', 'X', 'X', 'X', 'X'],
    ['0', '0', '0', '0', '0', '0', '0', 'X', 'X', 'X', 'X', 'X'],
    ['0', 'X', 'X', '0', 'X', 'X', '0', 'X', 'X', 'X', 'X', 'X'],
    ['0', 'X', 'X', '0', 'X', 'X', '0', 'X', 'X', 'X', 'X', 'X'],
    ['0', '0', '0', '0', 'X', 'X', '0', '0', '0', '0', 'X', 'X'],
    ['X', 'X', 'X', '0', 'X', 'X', 'X', 'X', 'X', '0', 'X', 'X'],
    ['X', 'X', 'X', '0', '0', '0', 'X', 'X', 'X', '0', 'X', 'X'],
    ['X', 'X', 'X', 'X', 'X', '0', '0', '0', 'X', '0', 'X', 'X'],
    ['X', 'X', 'X', 'X', 'X', 'X', 'X', '0', '0', '0', 'X', 'X'],
    ['X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X'],
    ['X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X']
 ]
difficult4= [
    ['X', 'X', 'X', 'X', '0', 'S', '0', '0', '0', '0', 'X', 'X'],
    ['X', 'X', 'X', 'X', '0', 'X', 'X', 'X', 'X', '0', 'X', 'X'],
    ['0', '0', '0', '0', '0', '0', '0', 'X', 'X', '0', 'X', 'X'],
    ['0', 'X', 'X', '0', 'X', 'X', '0', 'X', 'X', '0', 'X', 'X'],
    ['0', 'X', 'X', '0', 'X', 'X', '0', 'X', 'X', '0', 'X', 'X'],
    ['0', '0', '0', '0', 'X', 'X', '0', '0', '0', '0', 'X', 'X'],
    ['X', 'X', 'X', '0', 'X', 'X', 'X', 'X', 'X', '0', 'X', 'X'],
    ['X', 'X', 'X', '0', '0', '0', 'X', 'X', 'X', '0', 'X', 'X'],
    ['X', 'X', 'X', 'X', 'X', '0', '0', '0', 'X', '0', 'X', 'X'],
    ['X', 'X', 'X', 'X', 'X', 'X', 'X', '0', '0', '0', 'X', 'X'],
    ['X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X'],
    ['X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X']
 ]
difficult5= [
    ['X', 'X', 'X', 'X', '0', 'S', '0', '0', '0', '0', '0', '0'],
    ['X', 'X', 'X', 'X', '0', 'X', '0', 'X', 'X', '0', 'X', 'X'],
    ['0', '0', '0', '0', '0', '0', '0', 'X', 'X', '0', 'X', 'X'],
    ['0', 'X', 'X', 'X', 'X', 'X', '0', 'X', 'X', '0', 'X', 'X'],
    ['0', 'X', 'X', 'X', 'X', 'X', '0', 'X', 'X', '0', 'X', 'X'],
    ['0', '0', '0', '0', '0', 'X', '0', '0', '0', '0', 'X', 'X'],
    ['X', 'X', 'X', '0', '0', 'X', 'X', 'X', 'X', '0', 'X', 'X'],
    ['X', 'X', 'X', '0', '0', '0', 'X', 'X', 'X', '0', 'X', 'X'],
    ['X', 'X', 'X', '0', 'X', '0', '0', 'X', 'X', '0', 'X', 'X'],
    ['0', '0', '0', '0', 'X', 'X', 'X', 'X', 'X', '0', 'X', 'X'],
    ['0', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', '0', 'X', 'X'],
    ['0', '0', '0', '0', '0', '0', '0', '0', '0', '0', 'X', 'X']
 ]




"""result=A_Star(easy1,"admissible")               
print(result)
"""
def admissible(board):
    # Measure CPU time and memory consumption for admissible A* search
        
    admissible_start_time = time.process_time()
    total_travel,expanded_node,solution_distance = A_Star(board, "admissible")
    admissible_cpu_time = time.process_time() - admissible_start_time
    admissible_memory_usage = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    print("-------------------------------------------------")
    print("Admissible Result:")
    print("Total Travel distance:",total_travel)
    print("Total Solution path distance:",solution_distance)
    print("Number of expanded Node:", expanded_node)
    print("CPU Time (Admissible):", admissible_cpu_time, "seconds")
    print("Memory Usage (Admissible):", admissible_memory_usage, "bytes")



def inadmissible(board):
    # Measure CPU time and memory consumption for inadmissible A* search
    inadmissible_start_time = time.process_time()
    total_travel,expanded_node,solution_distance = A_Star(board, "inadmissible")
    inadmissible_cpu_time = time.process_time() - inadmissible_start_time
    inadmissible_memory_usage = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    print("-------------------------------------------------")
    print("Inadmissible Result:")
    print("Total Travel distance:",total_travel)
    print("Total Solution path distance:",solution_distance)
    print("Number of expanded Node:", expanded_node)
    print("CPU Time (Inadmissible):", inadmissible_cpu_time, "seconds")
    print("Memory Usage (Inadmissible):", inadmissible_memory_usage, "bytes")



#inadmissible(difficult5)
#admissible(difficult5)
inadmissible(easy3)
