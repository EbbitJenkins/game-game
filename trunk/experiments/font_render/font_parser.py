from pygame import image, Surface, Color
import ConfigParser
import os
from font_renderer import FontRenderer

#prepares the config parser
def prepare_parser(manifest):
	parser = ConfigParser.ConfigParser()
	try:
		#debug line
		print manifest
		parser.readfp(open(manifest))
	except ConfigParser.MissingSectionHeaderError:
		print "Weird errors, I wasn't able to remove until I erased the comments"
	
	return parser

class FontParser:
	def __init__(self, base_path):
		self.base_path = base_path

	def parse(self, manifest):
		parser = prepare_parser(manifest)

		image_path = os.path.join(self.base_path, parser.get('metadata', 'file'))
		font_table = image.load(image_path)
		font_table.set_colorkey(font_table.get_at((1,0)))

		images = self.__generate_characters(font_table, parser)

		renderer = FontRenderer(parser.get('metadata', 'name'))
		renderer.space_width = parser.getint('control', 'space_width')
		renderer.images = images
		return renderer

	def __generate_characters(self, font_table, content):
		images = {}
		font_height = font_table.get_height() - 1

		cur_pix = self.__starting_pix(font_table)
		for i in range(0, len(content.options('stripmap'))):
			if not content.has_option('stripmap', str(i)):
				break
			font_width = self.__determine_font_width(font_table, cur_pix)
			for letter in content.get('stripmap', str(i)).split(" "):
				images[letter] = font_table.subsurface(cur_pix, 1, font_width, font_height)
			cur_pix += font_width + 1

		images['unknown'] = images[content.get('control','unknown_glyph')]
		return images

	def __starting_pix(self, image, cord=(0,0)):
		return 0 if Color('red') != image.get_at(cord) else 1

	def __determine_font_width(self, image, cur_pix):
		# Our separator color
		color = Color('red')
		width = self.__starting_pix(image, (cur_pix, 0))

		try:
			while color != image.get_at((cur_pix + width, 0)):
				width += 1
				#This is added here because the last characters in some font would be huge
				#just break out for now, until we handle it better
				if width > 10:
					break
		except:
			print "Out of range"

		return width

	# Is this even the correct way to do "static" methods in python? I'll check this at a later date
	@classmethod
	def parse_name(self, manifest):
		parser = prepare_parser(manifest)
		return parser.get('metadata', 'name')


