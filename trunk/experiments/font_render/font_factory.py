from font_parser import FontParser
import re
import os

class FontFactory:
	def __init__(self, manifest_root, default="RPG"):
		manifests = [m for m in os.listdir(manifest_root) if re.search('Manifest$', m)]
		self.fonts = {}
		self.default = default
		self.base_path = manifest_root
		for manifest in manifests:
			actual_path = os.path.join(manifest_root, manifest)
			self.fonts[FontParser.parse_name(actual_path)] = actual_path

	def create_font_renderer(self, fontname):
		if not self.fonts.has_key(fontname):
			fontname = self.default

		parser = FontParser(self.base_path)
		return parser.parse(self.fonts[fontname])
		
