import os
import pyglet
import ConfigParser
from itertools import cycle

class Sprite(object):
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.dx, self.dy = 0, 0
        self.parse_manifest()

    def parse_manifest(self):
        # Name of the subclass of Sprite we are instantiating
        sub_name = self.__class__.__name__
        
        if sub_name == 'Sprite':
            raise NotImplementedError, 'Called from Sprite base class'

        manifest_path = os.sep.join(['data', sub_name, sub_name + '.Manifest'])

        parser = ConfigParser.SafeConfigParser()
        parser.read(manifest_path)

        # Read metadata
        w, h = parser.get('metadata', 'SpriteSize').split('x')
        self.w, self.h = int(w), int(h)

        self.images = {}

        # Read actions
        actions = [s for s in parser.sections() if s != 'metadata']
        sheets = [parser.get(s, 'SpriteSheet') for s in actions]

        # Hardcoded base dir
        base_dir = os.sep.join(['data', sub_name, 'images']) + os.sep

        for action, sheet in dict(zip(actions, sheets)).iteritems():
            sheet_img = pyglet.image.load(base_dir + sheet)

            # TODO: Hardcoded tile width value (16)
            cols = sheet_img.width / 16
            frames_grid = pyglet.image.ImageGrid(sheet_img, 1, cols)

            # Flip frames horizontally if needed
            try:
                parser.get(action, 'FlipX')

                flipped_frames = []
                
                for frame in frames_grid:
                    flipped = frame.get_texture().get_transform(flip_x=True)
                    flipped.anchor_x = 0
                    flipped_frames.append(flipped)

                frames_grid = flipped_frames
            except ConfigParser.NoOptionError:
                pass

            # Flip frames vertically if needed
            try:
                parser.get(action, 'FlipY')

                flipped_frames = []
                
                for frame in frames_grid:
                    flipped = frame.get_texture().get_transform(flip_y=True)
                    flipped.anchor_y = 0
                    flipped_frames.append(flipped)

                frames_grid = flipped_frames
            except ConfigParser.NoOptionError:
                pass

            # If this frame sequence should loop, maker it a cycle
            # Otherwise, make it a normal iterator
            try:
                parser.get(action, 'Loop')
                frames_iter = cycle(frames_grid)
            except ConfigParser.NoOptionError:
                frames_iter = iter(frames_grid)

            self.images[action] = frames_iter

            # Set this frame sequence as the sprite's initial image if needed
            try:
                parser.get(action, 'Initial')
                self.image = self.images[action]
            except ConfigParser.NoOptionError:
                pass

    def draw(self):
        self.image.next().blit(self.x, self.y)

    def update(self):
        self.x, self.y = self.x + self.dx, self.y + self.dy
        self.draw()


class Arrow(Sprite):
    pass
