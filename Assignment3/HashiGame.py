class HashiGame:
    def __init__(self, grid):
        self.grid = grid
        self.grid_size = len(grid)
        self.player_turn = 1
        self.player_scores = {1: 0, 2: 0}
    

    def display_grid(self):
        for row in self.grid:
            print(" ".join(str(cell).ljust(5) if cell is not None else ' ' * 5 for cell in row))


    def make_move(self, move):
            if move[0] == 'bridge':
                bridge_type, start, end = move[1], move[2], move[3]
                # Update the grid with the bridge
                if bridge_type == 'horizontal':
                    for col in range(min(start[1]+1, end[1]+1), max(start[1]-1, end[1]-1) + 1):
                        if(self.grid[start[0]][col] == '-'):
                            self.grid[start[0]][col] = '='
                        else:
                            self.grid[start[0]][col] = '-'
                elif bridge_type == 'vertical':
                    for row in range(min(start[0]+1, end[0]+1), max(start[0]-1, end[0]-1) + 1):
                        if(self.grid[row][start[1]] == '|'):
                            self.grid[row][start[1]] = 'X'
                        else:    
                            self.grid[row][start[1]] = '|'
                #Update scores
                if self.grid[start[0]][start[1]] == self.count_bridges((start[0],start[1])):
                    self.player_scores[self.player_turn] += self.grid[start[0]][start[1]]
                    self.player_scores[3 - self.player_turn] -= self.grid[start[0]][start[1]]
                if self.grid[end[0]][end[1]] == self.count_bridges((end[0],end[1])):
                    self.player_scores[self.player_turn] += self.grid[end[0]][end[1]]
                    self.player_scores[3-self.player_turn] -= self.grid[end[0]][end[1]]
            elif move[0] == 'label':
                label, position= move[1], move[2]
                # Update the grid with the label
                self.grid[position[0]][position[1]] = label
           
            # Switch to the next player's turn
            self.player_turn = 3 - self.player_turn
            return True
    

    def count_bridges(self, position):
        row, col = position
        count = 0
        # Count horizontal bridges
        if col+1 < self.grid_size and self.grid[row][col+1] == '-': 
            count += 1
        if col-1 >= 0 and self.grid[row][col-1] == '-':
            count +=1
        if col+1 < self.grid_size and self.grid[row][col+1] == '=': 
            count += 2
        if col-1 >= 0 and self.grid[row][col-1] == '=':
            count +=2
        
        # Count vertical bridges
        if row+1 < self.grid_size and self.grid[row+1][col] == '|':
            count +=1
        if row-1 >= 0 and self.grid[row-1][col] == '|':
            count +=1    
        if row+1 < self.grid_size and self.grid[row+1][col] == 'X':
            count +=2
        if row-1 >= 0 and self.grid[row-1][col] == 'X':
            count +=2 
        return count

    def is_game_over(self):
    # Check if the grid is fully filled
        if all(all(cell != "." for cell in row) for row in self.grid):
            return True
        # Check if no legal moves are available for both players
        if not self.get_legal_moves():
            return True
        return False

    
    def evaluate_state(self):
        #Payoff function
    # Calculate the score difference between players
        score_difference = self.player_scores[1] - self.player_scores[2]
        # Return the score difference as the payoff
        return score_difference

    
    def alpha_beta_search(self, depth, alpha, beta):
        if depth == 0 or self.is_game_over():
            return self.evaluate_state()
        
        if self.player_turn == 1:
            #Maximizing player (human)
            max_eval = float('-inf')
            for move in self.get_legal_moves():
                self.make_move(move)
                eval = self.alpha_beta_search(depth - 1, alpha, beta)
                self.undo_move(move)
                max_eval = max(max_eval, eval)
                alpha = max(alpha, eval)
                if beta <= alpha:
                    break
            return max_eval
        else:
            #Minimizing player (computer)
            min_eval = float('inf')
            for move in self.get_legal_moves():
                self.make_move(move)
                eval = self.alpha_beta_search(depth - 1, alpha, beta)
                self.undo_move(move)
                min_eval = min(min_eval, eval)
                beta = min(beta, eval)
                if beta <= alpha:
                    break
            return min_eval

    
    def undo_move(self, move):
        if move[0] == 'bridge':
            bridge_type, start, end = move[1], move[2], move[3]
            #Revert the scores
            if self.grid[start[0]][start[1]] == self.count_bridges((start[0],start[1])):
                self.player_scores[self.player_turn] += self.grid[start[0]][start[1]]
                self.player_scores[3 - self.player_turn] -= self.grid[start[0]][start[1]]
            if self.grid[end[0]][end[1]] == self.count_bridges((end[0],end[1])):
                self.player_scores[self.player_turn] += self.grid[end[0]][end[1]]
                self.player_scores[3-self.player_turn] -= self.grid[end[0]][end[1]]          
            # Revert the grid changes made by the bridge
            if bridge_type == 'horizontal':
                for col in range(min(start[1]+1, end[1]+1), max(start[1]-1, end[1]-1) + 1):
                    if  isinstance(self.grid[start[0]][col] ,int):
                        break
                    else:
                        if(self.grid[start[0]][col] == '='):
                            self.grid[start[0]][col] = '-'
                        else:
                            self.grid[start[0]][col] = '.'
            elif bridge_type == 'vertical':
                for row in range(min(start[0]+1, end[0]+1), max(start[0]-1, end[0]-1) + 1):
                    if isinstance(self.grid[row][start[1]],int):
                        break
                    else:
                        if(self.grid[row][start[1]] == 'X'):
                            self.grid[row][start[1]] = '|'
                        else:
                            self.grid[row][start[1]] = '.'
        elif move[0] == 'label':
            position = move[2]
            # Revert the grid changes made by the label
            self.grid[position[0]][position[1]] = 0
        self.player_turn = 3 - self.player_turn
        

    
    def get_legal_moves(self):
        legal_moves = []
        for row in range(self.grid_size):
            for col in range(self.grid_size):
                if self.grid[row][col] == 0:
                    # Add label moves for empty cells
                    legal_moves.extend([('label', label, (row, col)) for label in [3, 4]])
                elif isinstance(self.grid[row][col], int):
                    label = self.grid[row][col]
                    #Check if label satisfied
                    if (label != self.count_bridges((row,col)) and label > self.count_bridges((row,col))):
                        # Check if bridges can be placed horizontally
                        for c in range(col + 1, self.grid_size):
                            #Check there is no crossing bridge
                            if self.grid[row][c] in ['=', '|','X']:
                                break
                            if isinstance(self.grid[row][c], int):
                                neighbour_label=self.grid[row][c]
                                if(neighbour_label  > self.count_bridges((row,c))):
                                    legal_moves.append(('bridge', 'horizontal', (row, col), (row, c)))
                                break
                        for c in range(col - 1, -1, -1):
                            if self.grid[row][c] in ['=', '|', 'X']:
                                break
                            if isinstance(self.grid[row][c], int):
                                neighbour_label = self.grid[row][c]
                                if (neighbour_label > self.count_bridges((row, c))):
                                    legal_moves.append(('bridge', 'horizontal', (row, col), (row, c)))
                                break
                        
                        # Check if bridges can be placed vertically
                        for r in range(row + 1, self.grid_size):
                            if self.grid[r][col] in ['-', '=','X']:
                                break
                            if isinstance(self.grid[r][col], int):
                                neighbour_label=self.grid[r][col]
                                if( neighbour_label > self.count_bridges((r,col))):
                                    legal_moves.append(('bridge', 'vertical', (row, col), (r, col)))
                                break
                        for r in range(row - 1, -1, -1):
                            if self.grid[r][col] in ['-', '=', 'X']:
                                break
                            if isinstance(self.grid[r][col], int):
                                neighbour_label = self.grid[r][col]
                                if( neighbour_label > self.count_bridges((r,col))):
                                    legal_moves.append(('bridge', 'vertical', (row, col), (r, col)))
                                break
        return legal_moves
    
    def play_human_vs_computer(self):
        print("Initial Grid:")
        self.display_grid()
        print("Player 1: 0")
        print("Player 2: 0")
        print("-------------------------------")



        while not self.is_game_over():
                print(f"Player {self.player_turn} turn.", end=' ')
                if self.player_turn == 1:
                    print("Please make move:")
                    move = self.get_human_move()
                else:
                    print("Computer makes move.")
                    move = self.get_computer_move()
                
                self.make_move(move)
                print("-------------------------------")
                print("Current Grid:")
                self.display_grid()
                print(f"Player 1: {self.player_scores[1]}")
                print(f"Player 2: {self.player_scores[2]}")
                print("-------------------------------")

        print("END OF THE GAME")
        print("There is no possible move. ", end='')
        if self.player_scores[1] > self.player_scores[2]:
                print("Player 1 won.")
        elif self.player_scores[1] < self.player_scores[2]:
                print("Player 2 won.")
        else:
                print("It's a tie.")

    def get_human_move(self):
        while True:
            move_input = input("Enter your move (format: 'label <3 or 4> <row> <column>' or 'bridge <horizontal/vertical> <start_row> <start_column> <end_row> <end_column>'): ")
            move = tuple(move_input.split())
            if move[0] == 'label':
                label = int(move[1])
                if label not in [3, 4]:
                    print("Invalid label value. Please enter 3 or 4.")
                    continue
                row, col = int(move[2]), int(move[3])
                legal_moves= self.get_legal_moves()
                move =('label', label, (row, col))
                if move not in legal_moves:
                    print("Invalid move. Please try again.")
                    continue
            elif move[0] == 'bridge':
                bridge_type = move[1]
                start_row, start_col = int(move[2]), int(move[3])
                end_row, end_col = int(move[4]), int(move[5])
                legal_moves= self.get_legal_moves()
                move= ('bridge', bridge_type, (start_row, start_col), (end_row, end_col))
                if move not in legal_moves:
                    print("Invalid move. Please try again.")
                    continue
            else:
                print("Invalid move format. Please try again.")
                continue
            return move

    def get_computer_move(self):
        best_move = None
        best_score = float('inf')
        legal_moves = self.get_legal_moves()
        for move in legal_moves:
            self.make_move(move)
            score = self.alpha_beta_search(depth=3, alpha=float('-inf'), beta=float('inf'))
            self.undo_move(move)
            if score < best_score:
                best_score = score
                best_move = move
        return best_move



grid = [
    [ '.', 3 ,'.', 2 , '.', '.', 0],
    [ 1 ,'.', 1, '.', '.', 3, '.' ],
    ['.', 3, '.', 2, '.', '.', '.' ],
    ['.', '.', '.', '.', '.', '.', '.' ],
    [4, '.', 2, '.', '.', '.', '.' ],
    ['.', '.', '.', '.', '.', '.', '.' ],
    [0, '.', '.', 3, '.', 3, '.' ],
]


game = HashiGame(grid)
game.play_human_vs_computer()



# Display the final state of the game
print("Final Grid:")
game.display_grid()

# Print the scores of both players
print("Player 1 Score:", game.player_scores[1])
print("Player 2 Score:", game.player_scores[2])