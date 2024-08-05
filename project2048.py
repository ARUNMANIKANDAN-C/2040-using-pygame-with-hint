import random as r
import numpy as np
from tkinter import messagebox
import pygame
import sys

class Board:
    def __init__(self):
        self.size = 4
        self.matrix = np.zeros((self.size, self.size), dtype='int')
        self.square_size = 420 // self.size
        self.margin = 2
        self.width = (self.size * self.square_size) + (self.margin * (self.size + 1)) + 30
        self.height = (self.size * self.square_size) + (self.margin * (self.size + 1)) + 150
        self.generate_random_tiles(2)
        pygame.init()
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("2048")
        self.font = pygame.font.Font(None, 36)
        self.screen.fill((245, 222, 179))
        self.initialize_buttons()
        pygame_icon = pygame.image.load('icon.png')
        pygame.display.set_icon(pygame_icon)
        pygame.display.flip()

    def reset(self):
        self.matrix = np.zeros((self.size, self.size), dtype='int')
        self.generate_random_tiles(2)

    def generate_random_tiles(self, num_tiles=1):
        for _ in range(num_tiles):
            while True:
                i, j = r.randint(0, self.size - 1), r.randint(0, self.size - 1)
                if self.matrix[i][j] == 0:
                    self.matrix[i][j] = r.choices([2, 4], weights=[0.9, 0.1])[0]
                    break

    def draw_board(self):
        self.screen.fill((245, 222, 179))
        self.draw_buttons()
        pygame.draw.rect(self.screen,(160,82,45),(10,10 +60, (self.square_size + self.margin)*self.size+10 ,(self.square_size + self.margin)*self.size+10))
        for i in range(self.size):
            for j in range(self.size):
                x = self.margin + j * (self.square_size + self.margin)+15
                y = self.margin + i * (self.square_size + self.margin)+15+60
                value = self.matrix[i][j]
                color = self.get_color(value)
                pygame.draw.rect(self.screen, color, (x, y, self.square_size, self.square_size))
                pygame.draw.rect(self.screen, (0, 0, 0), (x, y, self.square_size, self.square_size), 2)

                if value != 0:
                    font = pygame.font.Font(None, self.square_size // 3)
                    text_surface = font.render(str(value), True, (255, 255, 255))
                    text_rect = text_surface.get_rect(center=(x + self.square_size // 2, y + self.square_size // 2))
                    self.screen.blit(text_surface, text_rect)

    def get_color(self, value):
        colors = {
            0: (250, 220, 210),
            2: (238, 148, 138),
            4: (237, 104, 100),
            8: (242, 177, 121),
            16: (245, 149, 99),
            32: (246, 124, 95),
            64: (246, 94, 59),
            128: (237, 207, 114),
            256: (237, 204, 97),
            512: (237, 200, 80),
            1024: (237, 197, 63),
            2048: (237, 194, 46)
        }
        return colors.get(value, (0, 0, 0))
    
    def initialize_buttons(self):
        self.new_game_button = Button(self.width -70, 10, 50, 50, r"Restart.png", r"Restart.png", (50, 50) )
        self.undo_button = Button(self.width -170,  10, 50, 50, r"Undo.png", r"Undo.png", (50, 50))
        self.redo_button = Button(self.width -120,  10, 50, 50, r"Redo.png", r"Redo.png", (50, 50))
        self.hint_button = Button(self.width -220,  10, 50, 50, r"Hint.jpg", r"Hint.jpg", (50, 50))
        self.Home_button = Button(10,  10, 50, 50, r"2048.png", r"2048.png", (117, 50))

    def draw_buttons(self):
        self.new_game_button.draw(self.screen)
        self.undo_button.draw(self.screen)
        self.redo_button.draw(self.screen)
        self.hint_button.draw(self.screen)
        self.Home_button.draw(self.screen)

    def draw_score(self,score,suggest):
        self.draw_board()

        score_text = self.font.render(f"Score: {score.get_score()}", True, (244, 164, 96))
        best_score_text = self.font.render(f"High Score: {score.get_high_score()}", True, (244, 164, 96))

        score_rect = score_text.get_rect(center=(self.width // 5, self.height -50))
        best_score_rect = best_score_text.get_rect(center=(3 * self.width // 4, self.height -50))

        self.screen.blit(score_text, score_rect)
        self.screen.blit(best_score_text, best_score_rect)

        if suggest is not None:
            
            suggest_text=self.font.render(f"Hint:{suggest}",True,(244, 164, 96))
            suggest_rect=suggest_text.get_rect(center=(int(self.width*0.42), self.height -25))
            self.screen.blit(suggest_text,suggest_rect)

class Score:
    def __init__(self):
        self.current_score = 0
        self.high_score_file = 'best_score.txt'
        self.high_score = self.load_high_score()

    def add(self, points):
        self.current_score += points
        self.update_high_score()

    def reset(self):
        self.current_score = 0

    def get_score(self):
        return self.current_score

    def update_high_score(self):
        if self.current_score > self.high_score:
            self.high_score = self.current_score
            self.save_high_score()

    def save_high_score(self):
        with open(self.high_score_file, 'w') as file:
            file.write(str(self.high_score))

    def load_high_score(self):
        try:
            with open(self.high_score_file, 'r') as file:
                return int(file.read())
        except FileNotFoundError:
            return 0

    def get_high_score(self):
        return self.high_score

class Movement:
    def __init__(self, board):
        self.board = board
        self.matrix = board.matrix
        self.moved = False  # Flag to track if any movement or merging occurred
        self.merged = [[False] * 4 for _ in range(4)]  # Grid to track merged cells

    def move(self, direction, test_matrix=None):
        if test_matrix is not None:
            self.matrix = test_matrix
        else:
            self.matrix = self.board.matrix

        self.moved = False
        self.merged = [[False] * 4 for _ in range(4)]
        points = 0
        if direction == 'w':
            points = self.move_up()
        elif direction == 's':
            points = self.move_down()
        elif direction == 'a':
            points = self.move_left()
        elif direction == 'd':
            points = self.move_right()
        return self.moved, points

    def move_up(self):
        points = 0
        for j in range(4):
            for i in range(1, 4):
                if self.matrix[i][j] != 0:
                    k = i
                    while k > 0 and (self.matrix[k-1][j] == 0 or (self.matrix[k-1][j] == self.matrix[k][j])):
                        if self.matrix[k-1][j] == 0:
                            self.matrix[k-1][j] = self.matrix[k][j]
                            self.matrix[k][j] = 0
                            self.moved = True
                        elif self.matrix[k-1][j] == self.matrix[k][j] and not self.merged[k-1][j]:
                            self.matrix[k-1][j] *= 2
                            points += self.matrix[k-1][j]
                            self.matrix[k][j] = 0
                            self.moved = True
                            self.merged[k-1][j] = True
                            break
                        k -= 1
        return points

    def move_down(self):
        points = 0
        for j in range(4):
            for i in range(2, -1, -1):
                if self.matrix[i][j] != 0:
                    k = i
                    while k < 3 and (self.matrix[k+1][j] == 0 or (self.matrix[k+1][j] == self.matrix[k][j])):
                        if self.matrix[k+1][j] == 0:
                            self.matrix[k+1][j] = self.matrix[k][j]
                            self.matrix[k][j] = 0
                            self.moved = True
                        elif self.matrix[k+1][j] == self.matrix[k][j] and not self.merged[k+1][j]:
                            self.matrix[k+1][j] *= 2
                            points += self.matrix[k+1][j]
                            self.matrix[k][j] = 0
                            self.moved = True
                            self.merged[k+1][j] = True
                            break
                        k += 1
        return points

    def move_left(self):
        points = 0
        for i in range(4):
            for j in range(1, 4):
                if self.matrix[i][j] != 0:
                    k = j
                    while k > 0 and (self.matrix[i][k-1] == 0 or (self.matrix[i][k-1] == self.matrix[i][k])):
                        if self.matrix[i][k-1] == 0:
                            self.matrix[i][k-1] = self.matrix[i][k]
                            self.matrix[i][k] = 0
                            self.moved = True
                        elif self.matrix[i][k-1] == self.matrix[i][k] and not self.merged[i][k-1]:
                            self.matrix[i][k-1] *= 2
                            points += self.matrix[i][k-1]
                            self.matrix[i][k] = 0
                            self.moved = True
                            self.merged[i][k-1] = True
                            break
                        k -= 1
        return points

    def move_right(self):
        points = 0
        for i in range(4):
            for j in range(2, -1, -1):
                if self.matrix[i][j] != 0:
                    k = j
                    while k < 3 and (self.matrix[i][k+1] == 0 or (self.matrix[i][k+1] == self.matrix[i][k])):
                        if self.matrix[i][k+1] == 0:
                            self.matrix[i][k+1] = self.matrix[i][k]
                            self.matrix[i][k] = 0
                            self.moved = True
                        elif self.matrix[i][k+1] == self.matrix[i][k] and not self.merged[i][k+1]:
                            self.matrix[i][k+1] *= 2
                            points += self.matrix[i][k+1]
                            self.matrix[i][k] = 0
                            self.moved = True
                            self.merged[i][k+1] = True
                            break
                        k += 1
        return points

class Stack:
    def __init__(self):
        self.undo_stack = []  # Stack to store game states for undo
        self.redo_stack = []  # Stack to store game states for redo

    def save_state(self, game_matrix, score):
        self.undo_stack.append((game_matrix.copy(), score))
        self.redo_stack.clear()  # Clear redo stack after a new move

    def undo(self, game, score):
        if self.undo_stack:
            self.redo_stack.append((game.matrix.copy(), score.current_score))
            game.matrix, score.current_score = self.undo_stack.pop()

    def redo(self, game, score):
        if self.redo_stack:
            self.undo_stack.append((game.matrix.copy(), score.current_score))
            game.matrix, score.current_score = self.redo_stack.pop()

class Game:
    def __init__(self):
        self.dic = {"up": "w", "down": "s", "left": "a", "right": "d"}
        self.board = Board()
        self.score = Score()
        self.stack = Stack()
        self.stack.save_state(self.board.matrix.copy(), self.score.get_score())
        self.suggest = None
        self.clock = pygame.time.Clock()

    def reset_game(self):
        self.board.reset()
        self.score.reset()
        self.stack = Stack()
        self.stack.save_state(self.board.matrix.copy(), self.score.get_score())

    def play(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    direction = None
                    self.suggest = None
                    if event.key == pygame.K_w:
                        direction = 'w'
                    elif event.key == pygame.K_s:
                        direction = 's'
                    elif event.key == pygame.K_a:
                        direction = 'a'
                    elif event.key == pygame.K_d:
                        direction = 'd'
                    elif event.key == pygame.K_u:
                        self.stack.undo(self.board, self.score)
                    elif event.key == pygame.K_r:
                        self.stack.redo(self.board, self.score)
                    if direction:
                        moved = self.move_and_merge(direction)
                        if moved:
                            self.stack.save_state(self.board.matrix.copy(), self.score.get_score())
                        if self.is_game_over():
                            if self.is_win():
                                self.show_win_message()
                                self.reset_game()
                            else:
                                self.show_game_over_message()
                                running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    self.suggest = None
                    mouse_pos = pygame.mouse.get_pos()
                    if self.board.new_game_button.clicked(event):
                        self.reset_game()
                    elif self.board.undo_button.clicked(event):
                        self.stack.undo(self.board, self.score)
                    elif self.board.redo_button.clicked(event):
                        self.stack.redo(self.board, self.score)
                    elif self.board.hint_button.clicked(event):
                        best_move = self.evaluate_best_move()
                        self.suggest = f"move: {best_move}"
                        
            mouse_pos = pygame.mouse.get_pos()
            self.board.new_game_button.update(mouse_pos)
            self.board.undo_button.update(mouse_pos)
            self.board.redo_button.update(mouse_pos)
            self.board.hint_button.update(mouse_pos)
            
            self.board.draw_score(self.score,self.suggest)
            pygame.display.flip()
            self.clock.tick(30)

    def move_and_merge(self, direction):
        movement = Movement(self.board)
        moved, points = movement.move(direction)
        if moved:
            self.score.add(points)
            self.board.generate_random_tiles(1)
        return moved

    def evaluate_best_move(self):
        best_move = None
        best_score = -1
        original_matrix = self.board.matrix.copy()
        for move, direction in self.dic.items():
            test_matrix = original_matrix.copy()
            movement = Movement(self.board)
            moved, score = movement.move(direction, test_matrix)
            if moved and score > best_score:
                best_move = move
                best_score = score
        return best_move
    
    def is_game_over(self):
        if np.any(self.board.matrix == 0):
            return False
        for i in range(self.board.size):
            for j in range(self.board.size):
                if i < self.board.size - 1 and self.board.matrix[i][j] == self.board.matrix[i + 1][j]:
                    return False
                if j < self.board.size - 1 and self.board.matrix[i][j] == self.board.matrix[i][j + 1]:
                    return False
        return True
    
    def is_win(self):
        for i in range(self.board.size):
            for j in range(self.board.size):
                if self.board.matrix[i][j] == 2048:
                    return True
        return False
    
    def show_win_message(self):
        messagebox.showinfo("You Win", "Congratulations! You reached 2048!")

    def show_game_over_message(self):
        k = messagebox.askyesno("Game Over", "You Lose! Do you want to play again?")
        if k:
            self.reset_game()
            self.play()

class Button:
    def __init__(self, x, y, width, height, image_path, hover_image_path, image_scale=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.image = pygame.image.load(image_path)
        self.hover_image = pygame.image.load(hover_image_path)
        if image_scale:
            self.image = pygame.transform.scale(self.image, image_scale)
            self.hover_image = pygame.transform.scale(self.hover_image, image_scale)
        self.hovered = False

    def draw(self, surface):
        image = self.hover_image if self.hovered else self.image
        surface.blit(image, self.rect)

    def update(self, mouse_pos):
        self.hovered = self.rect.collidepoint(mouse_pos)

    def clicked(self, event):
        return self.hovered and event.type == pygame.MOUSEBUTTONDOWN

if __name__ == "__main__":
    game = Game()
    game.play()
    pygame.quit()
    sys.exit()