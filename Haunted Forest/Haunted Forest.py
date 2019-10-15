from cocos import *
from cocos.layer import *
from cocos.director import *
from cocos.actions import *
from cocos.sprite import *
from pyglet.window import key
import pyglet
import random
import cocos

window = director.init(1024, 864, caption="Haunted Forest")

small_image = pyglet.resource.image('explosion.png')
small_grid = pyglet.image.ImageGrid(small_image, 11, 1)
small_textures = pyglet.image.TextureGrid(small_grid)
small_textures_list = small_textures[:]
frame_period = 0.05
small_animation = pyglet.image.Animation.from_image_sequence(small_textures_list, frame_period, loop=False)

duration = len(small_textures_list) * frame_period
default_opacity = 128
ghost_spritesheet_image = pyglet.resource.image('Ghost_spritesheet.png')
grid = pyglet.image.ImageGrid(ghost_spritesheet_image, 1, 28)
textures = pyglet.image.TextureGrid(grid)
textures_list = textures[:]
textures_list.append(textures_list[0])
ghost_animation = pyglet.image.Animation.from_image_sequence(textures_list, 0.085, loop=True)

img = pyglet.image.load('Man.png')
img_grid = pyglet.image.ImageGrid(img, 1, 4)
man = pyglet.image.Animation.from_image_sequence(img_grid[0:], 0.25, loop=True)


class Background (ScrollableLayer):
	def __init__(self):
		super().__init__()
		animation = pyglet.image.load_animation('Woods.gif')
		bg = cocos.sprite.Sprite(animation, scale=1.5)
		bg.position = bg.width // 2, bg.height // 2
		self.px_width = bg.width
		self.px_height = bg.height
		self.add(bg)


class Mover (cocos.actions.Move):
	def step(self, dt):
		super().step(dt)
		vel_x = (keyboard[key.RIGHT] - keyboard[key.LEFT]) * 500
		vel_y = 0
		self.target.velocity = (vel_x, vel_y)
		scroller.set_focus(self.target.x, self.target.y)


class Man (ScrollableLayer):
	def __init__( self ):
		super().__init__()
		spr = cocos.sprite.Sprite(man)
		spr.position = (80, 100)
		spr.velocity = (0, 0)
		spr.do(Mover())
		self.add(spr)


class TouchSprite(Sprite):

	def __init__(self, image):
		super(TouchSprite, self).__init__(image)

		window.push_handlers(self.on_mouse_press)

	def does_contain_point(self, pos):
		return (
				(abs(pos[0] - self.position[0]) < self.image.width / 2) and
				(abs(pos[1] - self.position[1]) < self.image.width / 2))

	def on_processed_touch(self, x, y, buttons, modifiers):
		pass

	def on_mouse_press(self, x, y, buttons, modifiers):
		px, py = director.get_virtual_coordinates(x, y)
		if self.does_contain_point((px, py)):
			self.on_processed_touch(px, py, buttons, modifiers)


class GhostSprite(TouchSprite):

	def does_contain_point(self, pos):
		return (
				(abs(pos[0] - self.position[0]) < 35) and
				(abs(pos[1] - self.position[1]) < 50))

	def on_processed_touch(self, x, y, buttons, modifiers):
		self.image = small_animation
		self.do(Delay(duration) + CallFuncS(GhostSprite.kill))


class GhostLayerAction(Action):
	def step(self, dt):
		ghosts = self.target.get_children()
		if 1 == len(ghosts):
			self.target.addghosts()


class GhostLayer(ScrollableLayer):
	def __init__(self):
		super().__init__()
		self.addghosts()
		self.do(GhostLayerAction())

	def addghosts(self):
		for i in range(0, 10):
			posX = 80 + random.random() * 1376
			posY = 100 + random.random() * 750
			new_ghost = GhostSprite(ghost_animation)
			new_ghost.position = (posX, posY)
			self.add(new_ghost)


class MainMenu (cocos.menu.Menu):
	def __init__(self):
		super().__init__('Haunted Forest')
		items = []
		items.append(cocos.menu.MenuItem("New Game", self.on_new_game))
		items.append(cocos.menu.MenuItem("Quit", self.on_quit))
		self.create_menu(items, cocos.menu.shake(), cocos.menu.shake_back())

	def on_new_game(self):
		scene.remove(self)
		scene.add(scroller)

	def on_quit(self):
		director.window.close()


director.window.pop_handlers()
keyboard = key.KeyStateHandler()
director.window.push_handlers(keyboard)
man_layer = Man()
bg_layer = Background()
ghost_layer = GhostLayer()
scroller = cocos.layer.ScrollingManager()
scroller.add(bg_layer)
scroller.add(man_layer)
scroller.add(ghost_layer)
menu = MainMenu()
scene = cocos.scene.Scene()
scene.add(menu)
director.run(scene)