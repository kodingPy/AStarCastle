import sys, pygame
import math
from heapq import heappush, heappop

RED = (255, 0, 0)
BLUE = (0, 255, 0)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
GREY = (128, 128, 128)
PURPLE = (128, 0, 128)
ORANGE = (255, 165, 0)
TURQUOISE = (64, 224, 208)

class ClickableSprite(pygame.sprite.Sprite):
	def __init__(self, image, x, y, callback):
		super().__init__()
		self.image = pygame.image.load(image).convert_alpha()
		self.rect = self.image.get_rect()
		self.rect.x = x
		self.rect.y = y
		self.callback = callback

	def update(self, events):
		for event in events:
			if event.type == pygame.MOUSEBUTTONUP:
				if self.rect.collidepoint(event.pos):
					self.callback()


def on_click(sprite):
	color = (255, 0, 0) if sprite.image.get_at(
		(0, 0)) != (255, 0, 0) else (0, 255, 0)
	img_rect = (0, 0, sprite.rect.w, sprite.rect.h)
	pygame.draw.rect(sprite.image, color, img_rect, 2)



class Spot: 
	def __init__(self, row, col, size, total_rows) :
		
		self.total_rows = total_rows
		self.row = row
		self.col = col
		self.x = row * size
		self.y = col * size
		self.color = WHITE
		self.neighbours = []
		self.width = size
		self.total_rows = total_rows
		self.img = pygame.image.load("asset/hexagon.png")
		self.surface = pygame.Surface((size, size))
		self.surface.fill(WHITE)
		
	
		self.square_path = {}
		self.value = 0
		self.isCastle = False
		self.isLake = False
		self.isMason = False
		self.isEnemy = False
		self.isWall = False
		self.isTerritory =False
		self.id = 0

   
	def get_pos(self):
		return self.row, self.col
	
	def on_click(self):
		color = (255, 0, 0) if self.img.get_at(
        	(0, 0)) != (255, 0, 0) else (0, 255, 0)
		self.img.fill(GREY)
	
	def update(self, events):
		for event in events:
			if event.type == pygame.MOUSEBUTTONUP:
				if self.rect.collidepoint(event.pos):
					self.callback()

	def is_closed(self):
		return self.color == RED

	def is_open(self):
		return self.color == GREEN

	def is_barrier(self):
		return self.color == BLACK

	def is_start(self):
		return self.color == ORANGE

	def is_end(self):
		return self.color == TURQUOISE

	def reset(self):
		self.color = WHITE

	def make_start(self, win):
		self.surface.fill(GREEN)
		

	def make_closed(self):
		self.color = RED

	def make_open(self):
		self.color = GREEN

	def make_barrier(self, win):
		self.surface.fill(BLACK)
		

	def make_end(self, win):
		self.surface.fill(TURQUOISE)
		
	def make_path(self):
		self.surface.fill(PURPLE)

	def set_icon(self):
   
		if self.isLake:
			self.img = pygame.image.load('asset/lake.png')
		elif self.isCastle:
			self.img = pygame.image.load('asset/castle.png')
		
		
		elif self.isMason:
			self.img = pygame.image.load('asset/masons.png')
		elif self.isEnemy:
			self.img = pygame.image.load('asset/enemy.png')

		return self.img 

	def draw(self, win):
		
		size = self.width
		
		nodeIcon = self.set_icon()
		imageIcon = pygame.transform.scale(nodeIcon, (size, size))
		self.surface.blit(imageIcon, (self.row, self.col))
		win.blit(self.surface, (self.row * size, self.col * size)) 
		
		
		

	def update_neighbors(self, grid):
		self.neighbors = []
		if self.row < self.total_rows - 1 and not grid[self.row + 1][self.col].is_barrier(): # DOWN
			self.neighbors.append(grid[self.row + 1][self.col])

		if self.row > 0 and not grid[self.row - 1][self.col].is_barrier(): # UP
			self.neighbors.append(grid[self.row - 1][self.col])

		if self.col < self.total_rows - 1 and not grid[self.row][self.col + 1].is_barrier(): # RIGHT
			self.neighbors.append(grid[self.row][self.col + 1])

		if self.col > 0 and not grid[self.row][self.col - 1].is_barrier(): # LEFT
			self.neighbors.append(grid[self.row][self.col - 1])
	
	def __lt__(self, other):
		return False

	def icon(self):
		return self.img 

	def update(self, events):
		for event in events:
			if event.type == pygame.MOUSEBUTTONUP:
				if self.rect.collidepoint(event.pos):
					self.on_click()


	def on_click(sprite):
		color = (255, 0, 0) if sprite.image.get_at(
			(0, 0)) != (255, 0, 0) else (0, 255, 0)
		img_rect = (0, 0, sprite.rect.w, sprite.rect.h)
		pygame.draw.rect(sprite.image, color, img_rect, 2)

class Game():

	def __init__(self, jsonData, node_size):
		self.value = 0

		if "matches" in jsonData :
			self.board =  jsonData["matches"][0]["board"]
			self.id = jsonData["matches"][0]["id"]
			self.turn = jsonData["matches"][0]["turns"]
			self.turnSecobds =jsonData["matches"][0]["turnSeconds"]
			
		else:
			self.board = jsonData["board"]
			self.id = jsonData["id"]
			self.walls = self.board["walls"]
			self.territories = self.board["territories"]
		
		self.width = self.board["width"]
		self.height = self.board["height"]
		
		self.structures = self.board["structures"]
		self.masons = self.board["masons"]   
		

		self.img = pygame.image.load("asset/hexagon.png")
		self.mason_list = []
		self.enemies = []
		self.castles = []
		self.lakes = []
		self.grid = [[Spot(x, y, node_size, self.width) for x in range(self.width)] for y in range(self.height)]
		self.mason_id = (0, 0, 0)
		self.node = Node(0,0)
		self.node_size = node_size
	
	
		

		
	def get_castles(self):
		for x in range(self.width):
		
			for y in range(self.height):
				if self.structures[x][y] == 2:
					self.node = Spot(x, y, self.node_size, self.width)
					self.node.isCastle = True
					self.castles.append(self.node)
					self.grid[x][y] = self.node
				   

	def get_lakes(self):
		for x in range(self.width):
			for y in range(self.height):
				if self.structures[x][y] == 1:
					self.node = Spot(x, y, self.node_size, self.width)
					self.node.isLake = True                 
					self.lakes.append(self.node)
					self.grid[x][y] = self.node
			   
	
	def get_masons(self):
		for x in range(self.width):
			for y in range(self.height):
				if self.masons[x][y] > 0:
					self.node = Spot(x, y, self.node_size, self.width)
					self.node.isMason = True
					self.mason_id = (x, y, self.masons[x][y] )
					self.mason_list.append(self.node)
					self.grid[x][y] = self.node

	def get_enemies(self):
		for x in range(self.width):
			for y in range(self.height):
				if self.masons[x][y] < 0:
					self.node = Spot(x, y, self.node_size, self.width)
					self.node.isEnemy = True
					self.enemies.append(self.node)
					self.grid[x][y] = self.node

	def get_walls(self):
		for x in range(self.width):
			for y in range(self.height):
				if self.walls[x][y] != 0:
					self.node = Spot(x, y, self.node_size, self.width)
					self.grid[x][y] = self.node

	def get_territories(self):
		for x in range(self.width):
			for y in range(self.height):
				if self.territories[x][y] != 0:
					self.node =Spot(x, y, self.node_size, self.width)
					self.grid[x][y] = self.node
			
	def searchPath(self):
	  
		for mason in self.mason_list:
			start = mason

			for castl in self.castles:
				
				goal = castl
				searchpath =" AStar(self, self.mason_list[0], self.castles[0])"
		return searchpath
	
	def icon(self, x, y):
		self.img = pygame.image.load('asset/hexagon.png')
		self.value = self.structures[x][y]
		if self.value == 1:
			self.img = pygame.image.load('asset/lake.png')
		elif self.value == 2:
			self.img = pygame.image.load('asset/castle.png')
		
		self.value = self.masons[x][y]
		if self.value > 0:
			self.img = pygame.image.load('asset/masons.png')
		elif self.value < 0:
			self.img = pygame.image.load('asset/enemy.png')

		return self.img
	
	def get_node(self, x, y):
		if x < 0 or x >= self.width or y < 0 or y >= self.height:
			return None
		return self.grid[y][x]

	def is_walkable(self, x, y):
		node = self.get_node(x, y)
		if (node is None) :
			return False
		return node.parent is None

	def get_neighbors(self, node):
		neighbors = []
		for x in range(node.x - 1, node.x + 2):
			for y in range(node.y - 1, node.y + 2):
				neighbor = self.get_node(x, y)
				if neighbor is not None and neighbor != node and self.is_walkable(x, y):
					neighbors.append(neighbor)
		return neighbors

	def draw_grid(self, screen):
		for y in range(self.height):
			for x in range(self.width):
				self.icon(x, y)
			   
				self.showIcon(x, y, self.node_size, screen)
				

	def showIcon(self, x, y, size, screen):
		surface = pygame.Surface((size, size))
		surface.fill(WHITE)
		nodeIcon = self.img
		imageIcon = pygame.transform.scale(nodeIcon, (size, size))
		surface.blit(imageIcon, (0,0))
		screen.blit(surface, (x * size,y * size))

	def draw_label(self, screen, text, position):
		font = pygame.font.SysFont(None, 20)
		text_surface = font.render(text, True, (0, 0, 0))
		screen.blit(text_surface, position)
		
	def draw_square_path(self,  start_x, start_y, distance):
		"""Draws a square path from a cell at (start_x, start_y) in an 11*11 grid with distance = distance.

		Args:
		start_x: The x-coordinate of the start cell.
		start_y: The y-coordinate of the start cell.
		distance: The distance of the square path.

		Returns:
		A list of (x, y) coordinates of the square path.
		"""
		distance = distance * 2

	   
			# Create a list to store the square path.
		square_path = []
		start_x = start_x - distance // 2
		start_y = start_y - distance // 2
		if 0 > start_x : start_x == 0
		if 11 < start_x: start_x == 10
		if 0 > start_y : start_y == 0
		if 11 < start_y : start_y == 10
		# Add the start top left cell to the square path.
	   

		# Move right by distance.
		for i in range(distance ):
			square_path.append((start_x + i + 1, start_y))


		# Move down by distance.
		for i in range(distance ):
			square_path.append((start_x + distance, start_y + i + 1))

		# Move left by distance.
		for i in range(distance):
			square_path.append((start_x + distance - i - 1, start_y + distance))

		# Move up by distance.
		for i in range(distance):
			square_path.append((start_x, start_y + distance - i - 1))

		# Close the square path by adding the start cell again.
		square_path.append((start_x, start_y))


		# Return the square path.
		return square_path

	def get_neighbor_cells_with_distance_2(self, dist, center_cell_x, center_cell_y, grid):
		"""Returns a list of all neighbor cells with distance = 2 from the center cell.

		Args:
			center_cell_x: The x-coordinate of the center cell.
			center_cell_y: The y-coordinate of the center cell.
			grid: A 2D list representing the grid.

		Returns:
			A list of all neighbor cells with distance = 2 from the center cell.
		"""

		neighbor_cells = []
		# Check all 8 cells around the center cell.
		for dx in [-2, -1, 0, 1, 2]:
			for dy in [-2, -1, 0, 1, 2]:
			# Make sure that the neighbor cell is within the bounds of the grid.
				if 0 <= center_cell_x + dx < grid.width and 0 <= center_cell_y + dy < grid.height:
				# Make sure that the neighbor cell is not the center cell itself.
					if dx != 0 or dy != 0:
						neighbor_cells.append((center_cell_x + dx, center_cell_y + dy))

		return neighbor_cells


class Node(pygame.sprite.Sprite):
	
	def __init__(self, x, y, parent=None, callback=None):
		self.x = x
		self.y = y
		self.parent = parent
		self.f_score = 0
		self.g_score = 0
		self.h_score = 0
		self.color = WHITE
		self.img = pygame.image.load("asset/hexagon.png")
		self.square_path = {}
		self.value = 0
		self.isCastle = False
		self.isLake = False
		self.isMason = False
		self.isEnemy = False
		self.isWall = False
		self.isTerritory =False
		self.id = 0
		
		self.rect = self.img.get_rect()
		self.rect.x = x
		self.rect.y = y
		self.callback = callback

	def update(self, events):
		for event in events:
			if event.type == pygame.MOUSEBUTTONUP:
				if self.rect.collidepoint(event.pos):
					self.callback()


	def __lt__(self, other):
		return self.f_score < other.f_score
	
	def get_value(self, data):
		return data[self.x][self.y]
	
	def set_structure(self,  data):
		
		if data[self.x][self.y] == 2:
			self.isCastle = True
			self.value = 2
		if data[self.x][self.y] == 1:
			self.isLake = True
			self.value = 1
		  
	def set_mason(self,data):
		if data[self.x][self.y] > 0:
			self.isMason = True
			self.id = data[self.x][self.y]
		elif data[self.x][self.y] < 0:
			self.isEnemy = True
	
	def set_color(self, value):
		if value == 0: return  WHITE 
		if value == 2: return  BLUE
		if value == 1: return RED
		if value < 0: return  GREEN
		else:
			return WHITE
		
	def set_icon(self):
   
		if self.isLake:
			self.img = pygame.image.load('asset/lake.png')
		elif self.isCastle:
			self.img = pygame.image.load('asset/castle.png')
		
		
		elif self.isMason:
			self.img = pygame.image.load('asset/masons.png')
		elif self.isEnemy:
			self.img = pygame.image.load('asset/enemy.png')

		return self.img 
	
	def drawIcon(self, size, screen, x, y):
		surface = pygame.Surface((size, size))
		surface.fill(WHITE)

		
		nodeIcon = self.set_icon()
		imageIcon = pygame.transform.scale(nodeIcon, (size, size))
		surface.blit(imageIcon, (0,0))
		screen.blit(surface, (x * size,y * size))
			   
	def get_square_path(self,  distance):
		"""Draws a square path from a cell at (start_x, start_y) in an 11*11 grid with distance = distance.

		Args:
		start_x: The x-coordinate of the start cell.
		start_y: The y-coordinate of the start cell.
		distance: The distance of the square path.

		Returns:
		A list of (x, y) coordinates of the square path.
		"""
		start_x = self.x
		start_y  = self.y
		distance = distance * 2

	   
			# Create a list to store the square path.
		square_path = []
		if self.isCastle :
			start_x = start_x - distance // 2
			start_y = start_y - distance // 2
			if 0 > start_x : start_x == 0
			if 11 < start_x: start_x == 10
			if 0 > start_y : start_y == 0
			if 11 < start_y : start_y == 10
			# Add the start top left cell to the square path.
		

			# Move right by distance.
			for i in range(distance ):
				square_path.append((start_x + i + 1, start_y))


			# Move down by distance.
			for i in range(distance ):
				square_path.append((start_x + distance, start_y + i + 1))

			# Move left by distance.
			for i in range(distance):
				square_path.append((start_x + distance - i - 1, start_y + distance))

			# Move up by distance.
			for i in range(distance):
				square_path.append((start_x, start_y + distance - i - 1))

			# Close the square path by adding the start cell again.
			square_path.append((start_x, start_y))


		# Return the square path.
		return square_path
	
