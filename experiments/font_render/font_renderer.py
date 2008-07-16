MAX_LENGTH=320
RENDER_TICKS = 10

class FontRenderer:
	def __init__(self, name, cord=(10, 10), speed=10):
		self.name = name
		self.images = {}
		self.speed = speed
		self.cord = cord
		self.rendering = False

	def start_render(self, text):
		self.rendering = True
		self.char_iter = iter(text)
		self.counter = self.speed
		self.x = self.cord[0]
		self.y = self.cord[1]

	def render(self, surface):
		if not self.rendering:
			return

		if self.counter < RENDER_TICKS:
			self.counter += 1
		else:
			self.counter = self.speed
			try:
				char = self.char_iter.next()
				if char == " ":
					char = self.char_iter.next()
					self.x += self.space_width
				char_img = self.images[char] if self.images.has_key(char) else self.images['unknown']
				surface.blit(char_img, (self.x, self.y), char_img.get_rect())
				self.x += char_img.get_width() + 1
				if self.x > MAX_LENGTH:
					self.x = self.cord[0]
					self.y += char_img.get_height() + 2
			except StopIteration:
					self.rendering = False
