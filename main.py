import pygame
import random
import sys

# Inisialisasi Pygame
pygame.init()

# Konstanta Warna
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (50, 50, 50)
DARK_GRAY = (30, 30, 30)

# Warna Blok (I, J, L, O, S, T, Z)
COLORS = [
    (0, 240, 240),  # Cyan (I)
    (0, 0, 240),    # Blue (J)
    (240, 160, 0),  # Orange (L)
    (240, 240, 0),  # Yellow (O)
    (0, 240, 0),    # Green (S)
    (160, 0, 240),  # Purple (T)
    (240, 0, 0)     # Red (Z)
]

# Bentuk Blok (Matriks)
SHAPES = [
    [[1, 1, 1, 1]],  # I
    [[1, 0, 0], [1, 1, 1]],  # J
    [[0, 0, 1], [1, 1, 1]],  # L
    [[1, 1], [1, 1]],  # O
    [[0, 1, 1], [1, 1, 0]],  # S
    [[0, 1, 0], [1, 1, 1]],  # T
    [[1, 1, 0], [0, 1, 1]]  # Z
]

# Ukuran Game
BLOCK_SIZE = 30
GRID_WIDTH = 10
GRID_HEIGHT = 20
SIDEBAR_WIDTH = 200
GRID_OFFSET_X = 30
GRID_OFFSET_Y = 30

class Tetris:
    def __init__(self):
        # Setup Layar
        self.width = GRID_OFFSET_X * 2 + GRID_WIDTH * BLOCK_SIZE + SIDEBAR_WIDTH
        self.height = GRID_OFFSET_Y * 2 + GRID_HEIGHT * BLOCK_SIZE
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Tetris")
        
        # Game State
        self.grid = [[0 for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        self.current_piece = self.new_piece()
        self.next_piece = self.new_piece()
        self.game_over = False
        self.score = 0
        self.level = 1
        self.fall_speed = 0.5  # Kecepatan jatuh blok (detik)
        self.fall_time = 0
        
        # Font
        self.font_large = pygame.font.SysFont('Arial', 36, bold=True)
        self.font_medium = pygame.font.SysFont('Arial', 24)
        self.font_small = pygame.font.SysFont('Arial', 18)
        
        # Background Gradient
        self.bg_color1 = (10, 20, 30)
        self.bg_color2 = (30, 40, 50)
    
    def new_piece(self):
        """Membuat blok baru secara acak."""
        shape_idx = random.randint(0, len(SHAPES) - 1)
        shape = SHAPES[shape_idx]
        color = COLORS[shape_idx]
        
        x = GRID_WIDTH // 2 - len(shape[0]) // 2  # Posisi tengah
        y = 0  # Mulai dari atas
        
        return {"shape": shape, "color": color, "x": x, "y": y}
    
    def valid_move(self, piece, x_offset=0, y_offset=0):
        """Cek apakah pergerakan blok valid."""
        for y, row in enumerate(piece["shape"]):
            for x, cell in enumerate(row):
                if cell:
                    new_x = piece["x"] + x + x_offset
                    new_y = piece["y"] + y + y_offset
                    
                    if (new_x < 0 or new_x >= GRID_WIDTH or 
                        new_y >= GRID_HEIGHT or 
                        (new_y >= 0 and self.grid[new_y][new_x])):
                        return False
        return True
    
    def rotate_piece(self):
        """Rotasi blok 90 derajat."""
        # Create a new rotated shape
        rotated_shape = []
        for x in range(len(self.current_piece["shape"][0])):
            new_row = []
            for y in range(len(self.current_piece["shape"])-1, -1, -1):
                new_row.append(self.current_piece["shape"][y][x])
            rotated_shape.append(new_row)
        
        # Create a new piece with rotated shape
        piece = {
            "shape": rotated_shape,
            "color": self.current_piece["color"],
            "x": self.current_piece["x"],
            "y": self.current_piece["y"]
        }
        
        if self.valid_move(piece):
            self.current_piece = piece
    
    def lock_piece(self):
        """Mengunci blok ke grid."""
        for y, row in enumerate(self.current_piece["shape"]):
            for x, cell in enumerate(row):
                if cell:
                    grid_y = self.current_piece["y"] + y
                    grid_x = self.current_piece["x"] + x
                    if grid_y >= 0:
                        self.grid[grid_y][grid_x] = self.current_piece["color"]
        
        self.clear_lines()
        self.current_piece = self.next_piece
        self.next_piece = self.new_piece()
        
        if not self.valid_move(self.current_piece):
            self.game_over = True
    
    def clear_lines(self):
        """Hapus garis yang penuh dan update skor."""
        lines_cleared = 0
        for y in range(GRID_HEIGHT):
            if all(self.grid[y]):
                lines_cleared += 1
                for y2 in range(y, 0, -1):
                    self.grid[y2] = self.grid[y2 - 1].copy()
                self.grid[0] = [0] * GRID_WIDTH
        
        # Update Skor
        if lines_cleared == 1:
            self.score += 100 * self.level
        elif lines_cleared == 2:
            self.score += 300 * self.level
        elif lines_cleared == 3:
            self.score += 500 * self.level
        elif lines_cleared >= 4:
            self.score += 800 * self.level
        
        # Update Level
        self.level = 1 + self.score // 10000
        self.fall_speed = max(0.05, 0.5 - (self.level - 1) * 0.05)
    
    def draw_background(self):
        """Gambar background gradient."""
        for y in range(self.height):
            ratio = y / self.height
            r = int(self.bg_color1[0] + (self.bg_color2[0] - self.bg_color1[0]) * ratio)
            g = int(self.bg_color1[1] + (self.bg_color2[1] - self.bg_color1[1]) * ratio)
            b = int(self.bg_color1[2] + (self.bg_color2[2] - self.bg_color1[2]) * ratio)
            pygame.draw.line(self.screen, (r, g, b), (0, y), (self.width, y))
    
    def draw_grid(self):
        """Gambar grid dan blok yang sudah terkunci."""
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                pygame.draw.rect(
                    self.screen, GRAY,
                    (GRID_OFFSET_X + x * BLOCK_SIZE, 
                     GRID_OFFSET_Y + y * BLOCK_SIZE, 
                     BLOCK_SIZE, BLOCK_SIZE), 1
                )
                if self.grid[y][x]:
                    pygame.draw.rect(
                        self.screen, self.grid[y][x],
                        (GRID_OFFSET_X + x * BLOCK_SIZE + 1, 
                         GRID_OFFSET_Y + y * BLOCK_SIZE + 1, 
                         BLOCK_SIZE - 2, BLOCK_SIZE - 2)
                    )
    
    def draw_current_piece(self):
        """Gambar blok yang sedang jatuh."""
        for y, row in enumerate(self.current_piece["shape"]):
            for x, cell in enumerate(row):
                if cell:
                    pygame.draw.rect(
                        self.screen, self.current_piece["color"],
                        (GRID_OFFSET_X + (self.current_piece["x"] + x) * BLOCK_SIZE + 1,
                         GRID_OFFSET_Y + (self.current_piece["y"] + y) * BLOCK_SIZE + 1,
                         BLOCK_SIZE - 2, BLOCK_SIZE - 2)
                    )
    
    def draw_next_piece(self):
        """Gambar preview blok berikutnya."""
        sidebar_x = GRID_OFFSET_X + GRID_WIDTH * BLOCK_SIZE + 10
        sidebar_y = GRID_OFFSET_Y
        
        # Panel Sidebar
        pygame.draw.rect(
            self.screen, DARK_GRAY,
            (sidebar_x, sidebar_y, SIDEBAR_WIDTH, self.height - GRID_OFFSET_Y * 2)
        )
        
        # Teks "Next"
        next_text = self.font_medium.render("NEXT", True, WHITE)
        self.screen.blit(next_text, (sidebar_x + SIDEBAR_WIDTH // 2 - next_text.get_width() // 2, sidebar_y + 20))
        
        # Gambar Blok Berikutnya
        shape = self.next_piece["shape"]
        start_x = sidebar_x + (SIDEBAR_WIDTH - len(shape[0]) * BLOCK_SIZE) // 2
        start_y = sidebar_y + 70
        
        for y, row in enumerate(shape):
            for x, cell in enumerate(row):
                if cell:
                    pygame.draw.rect(
                        self.screen, self.next_piece["color"],
                        (start_x + x * BLOCK_SIZE + 1, 
                         start_y + y * BLOCK_SIZE + 1, 
                         BLOCK_SIZE - 2, BLOCK_SIZE - 2)
                    )
        
        # Skor & Level
        score_text = self.font_medium.render(f"SCORE: {self.score}", True, WHITE)
        level_text = self.font_medium.render(f"LEVEL: {self.level}", True, WHITE)
        
        self.screen.blit(score_text, (sidebar_x + 20, sidebar_y + 150))
        self.screen.blit(level_text, (sidebar_x + 20, sidebar_y + 180))
    
    def draw_game_over(self):
        """Tampilkan layar Game Over."""
        if self.game_over:
            overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            self.screen.blit(overlay, (0, 0))
            
            game_over_text = self.font_large.render("GAME OVER", True, (240, 50, 50))
            restart_text = self.font_medium.render("Press R to Restart", True, WHITE)
            
            self.screen.blit(
                game_over_text,
                (self.width // 2 - game_over_text.get_width() // 2, 
                 self.height // 2 - 40)
            )
            self.screen.blit(
                restart_text,
                (self.width // 2 - restart_text.get_width() // 2, 
                 self.height // 2 + 20)
            )
    
    def run(self):
        """Main Game Loop."""
        clock = pygame.time.Clock()
        
        while True:
            # Handle Input
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                
                if not self.game_over:
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_LEFT:
                            if self.valid_move(self.current_piece, x_offset=-1):
                                self.current_piece["x"] -= 1
                        elif event.key == pygame.K_RIGHT:
                            if self.valid_move(self.current_piece, x_offset=1):
                                self.current_piece["x"] += 1
                        elif event.key == pygame.K_DOWN:
                            if self.valid_move(self.current_piece, y_offset=1):
                                self.current_piece["y"] += 1
                        elif event.key == pygame.K_UP:
                            self.rotate_piece()
                        elif event.key == pygame.K_SPACE:
                            while self.valid_move(self.current_piece, y_offset=1):
                                self.current_piece["y"] += 1
                            self.lock_piece()
                
                if event.type == pygame.KEYDOWN and event.key == pygame.K_r and self.game_over:
                    self.__init__()  # Restart Game
            
            # Update Game
            if not self.game_over:
                self.fall_time += clock.get_rawtime() / 1000  # Delta time
                clock.tick()
                
                if self.fall_time >= self.fall_speed:
                    self.fall_time = 0
                    if self.valid_move(self.current_piece, y_offset=1):
                        self.current_piece["y"] += 1
                    else:
                        self.lock_piece()
            
            # Draw Everything
            self.draw_background()
            self.draw_grid()
            self.draw_current_piece()
            self.draw_next_piece()
            self.draw_game_over()
            
            pygame.display.flip()

if __name__ == "__main__":
    game = Tetris()
    game.run()