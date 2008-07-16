import pygame
from pygame.locals import *
import os
import sys
from font_factory import FontFactory

# Check this out! So, if this program complains about the manifest files
# not being formatted correctly; I think there's three garbage characters at the 
# beginning of console-blocks and console-extras. I could be doing something completely wrong!
if __name__ == "__main__":

	if len(sys.argv) < 5:
		print("python test_bed manifest_root font_name render_speed text")
		sys.exit(1)

	base_path = sys.argv[1]
	if not os.path.isdir(base_path):
		print("manifest_root needs to be a directory >:(")
		sys.exit(1)

	render_speed = int(sys.argv[3])
	if render_speed < 0 or render_speed > 10:
		print("Please make the render speed (0-10)")
		sys.exit(2)

	pygame.init()

	# Ideally, there would be only one font factory that is instantiated when the
	# game is booted (methinks).  That said, the create font renderer method should be static
	# and adhere to singleton rules, or something like that
	factory = FontFactory(base_path)
	renderer = factory.create_font_renderer(sys.argv[2]);

	screen = pygame.display.set_mode((640, 480))
	pygame.display.set_caption("Font Render Test")
	clock = pygame.time.Clock()

	# The speed attribute can, and should be passed in the constructor of the Renderer
	# The factory would have access to all that config info though 
	renderer.speed = render_speed
	# This method prepares the text to be rendered
	renderer.start_render(sys.argv[4])
	while 1:
		clock.tick(60)
		for event in pygame.event.get():
			if event.type == QUIT:
				sys.exit(1)
			
		#needed for speed
		renderer.render(screen)
		pygame.display.flip()
