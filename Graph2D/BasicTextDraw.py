from kivy.graphics import BindTexture, RenderContext, Callback
import numpy as np
import freetype as ft
import os
import ctypes
from kivy.graphics import Mesh
from kivy.graphics.texture import texture_create 
from util import *
from kivy.graphics.opengl import glBlendFunc, GL_ONE, GL_ONE_MINUS_SRC_ALPHA,\
                                GL_SRC_ALPHA

def get_numpy_unit8_array_pointer(array):
    assert array.dtype == np.uint8
    return array.ctypes.data_as(ctypes.POINTER(ctypes.c_uint8))

class BasicTextDraw():
	vs_str = '''
    #version 330
	layout(location = 0) in vec2 IN_pos;
	layout(location = 1) in vec2 IN_uv;
	layout(location = 2) in float IN_color;
    uniform vec4       iResolution;
    uniform mat4 projection_mat;

	out struct {
		vec2 uv;
		vec4 color;
	} FRAG;

	void main(){
		gl_Position = projection_mat*vec4(IN_pos, 0.0, 1.0);
		FRAG.uv = IN_uv;
		FRAG.color = vec4(
			float((int(IN_color) >> 16)&255)/255.0,
			float((int(IN_color) >>  8)&255)/255.0,
			float((int(IN_color) >>  0)&255)/255.0,
			1.0
			);
	}
	'''
	fs_str = '''
    #version 330
	in struct {
		vec2 uv;
		vec4 color;
	} FRAG;

	uniform sampler2D U_texture;
	out vec4 OUT_color;

	void main(){
		float sdf = texture(U_texture, FRAG.uv).r;
		float fw = 0.5*fwidth(sdf);
		float mask = smoothstep(0.5 - fw, 0.5 + fw, sdf);
		
		OUT_color = FRAG.color*mask;
		//OUT_color.a = smoothstep(0.0, 0.5, sdf);
	}
	'''
	attr_layout = [
    	(b'IN_pos', 2, 'float'),
    	(b'IN_uv', 2, 'float'),
    	(b'IN_color', 1, 'float'),
	]
	def __init__(self, font='Ubuntu Mono Nerd Font Complete Mono.ttf', size=24):
		self.face = None
		self.bitmap = None
		self.cursor_x = 0.
		self.cursor_y = 0.
		self.vertices = []
		self.indices = []
		self.load_font_image(font, size)
		self.renderer = self.RenderContext();

	def RenderContext(self):
		assert self.face is not None
		assert self.bitmap is not None
		canvas = RenderContext(use_parent_projection=True)
		canvas.shader.vs = self.vs_str 
		canvas.shader.fs = self.fs_str 
		#texture = Texture.create(size=(self.bitmap.shape[1], self.bitmap.shape[0]), colorfmt='rgb')
		self.texture = texture_create(size=(self.bitmap.shape[1], self.bitmap.shape[0]), colorfmt='red')
		#debug
		#print('width :', self.bitmap.shape[1])
		#print('height:', self.bitmap.shape[0])
		self.texture.blit_buffer(self.bitmap.tobytes(), colorfmt='red', bufferfmt='ubyte')
		with canvas:
			BindTexture(texture=self.texture, index=1)
		canvas['U_texture'] = 1
		return canvas

	def load_font_image(self, filename, size=24):
		assert os.path.exists(filename)
    	# Load font  and check it is monotype
		self.face = ft.Face(filename)
		#print('font size:', size)
		self.face.set_char_size( size*64 )
		if not self.face.is_fixed_width:
			raise 'Font is not monotype'
    	# Determine largest glyph size
		width, height, ascender, descender = 0, 0, 0, 0
		for c in range(0, 128):
			self.face.load_char( chr(c), ft.FT_LOAD_RENDER | ft.FT_LOAD_FORCE_AUTOHINT )
			bitmap    = self.face.glyph.bitmap
			width     = max( width, bitmap.width )
			ascender  = max( ascender, self.face.glyph.bitmap_top )
			descender = max( descender, bitmap.rows - self.face.glyph.bitmap_top )
		height = ascender+descender
		#debug
		#print(width, height, ascender, descender)
		# Generate texture data
		self.bitmap = np.zeros((height*8, width*16), dtype=np.ubyte)
		for j in range(8):
			for i in range(16):
				self.face.load_char(chr(0+j*16+i), ft.FT_LOAD_RENDER | ft.FT_LOAD_FORCE_AUTOHINT )
				bitmap = self.face.glyph.bitmap
				x = i*width  + self.face.glyph.bitmap_left
				y = j*height + ascender - self.face.glyph.bitmap_top
				self.bitmap[y:y+bitmap.rows, x:x+bitmap.width].flat = bitmap.buffer
				#debug
				#print(chr(0+j*16+i), 'y:',y+bitmap.rows,'x:',x+bitmap.width)
		self.glyph_w, self.glyph_h = float(width), float(height)
		self.glyph_dx, self.glyph_dy = float(width/self.bitmap.shape[1]), float(height/self.bitmap.shape[0])

		#debug
		#self.bitmap.tofile('TextDraw.txt', sep=' ')
		#

	def _putc(self, c, color=[255, 255, 255]):
		i = ord(c)
		if (c == '\n'):
			self.cursor_y -= float(self.glyph_h)
		elif (c == '\t'):
			self.cursor_x += float(self.glyph_w) * 4.
		elif (i < 128):
			x = i%16
			y = i//16
			#debug
			#print(c, 'x, y, dx, dy', x, y, self.glyph_dx, self.glyph_dy)
			# pos, uv, color
			color = float(cpTorgb(color))
			self.vertices.extend([
				self.cursor_x, self.cursor_y - self.glyph_h,
				float(x)*self.glyph_dx, float(y+1)*self.glyph_dy,
				color
				])
			self.vertices.extend([
				self.cursor_x, self.cursor_y,
				float(x)*self.glyph_dx, float(y)*self.glyph_dy,
				color
				])
			self.vertices.extend([
				self.cursor_x + self.glyph_w, self.cursor_y,
				float(x+1)*self.glyph_dx, float(y)*self.glyph_dy,
				color
				])
			self.vertices.extend([
				self.cursor_x + self.glyph_w, self.cursor_y - self.glyph_h,
				float(x+1)*self.glyph_dx, float(y+1)*self.glyph_dy,
				color
				])
			base = 4*(len(self.indices)//6)
			self.indices.extend([0+base, 1+base, 2+base, 0+base, 2+base, 3+base])
			self.cursor_x += float(self.glyph_w)
			
	def puts(self, s, x, y, color=[255, 255, 255]):
		self.cursor_x = float(x)
		self.cursor_y = float(y)
		for c in s:
			self._putc(c, color)
		self.cursor_x, self.cursor_y = 0., 0.

	def setup_gl_context(self, *args):
        # need for proper rendering
		glBlendFunc(GL_ONE, GL_ONE_MINUS_SRC_ALPHA)

	def reset_gl_context(self, *args):
        # kivy default blend function value
		glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

	def flush(self):
		#print('[DEBUG] vertices:\n', self.vertices)
		#print('[DEBUG] indices:\n', self.indices)
		self.renderer.clear()
		with self.renderer:
			self.cb = Callback(self.setup_gl_context)
			BindTexture(texture=self.texture, index=1)
			Mesh(
                vertices = self.vertices,
                indices= self.indices,
                fmt=self.attr_layout,
                mode='triangles',
			)
			self.cb = Callback(self.reset_gl_context)
		self.vertices = []
		self.indices  = []
		self.cursor_x, self.cursor_y = 0., 0.
        	
if __name__ == "__main__":
	textdraw=BasicTextDraw() 
	textdraw.load_font_image('Ubuntu Mono Nerd Font Complete Mono.ttf')
	textdraw.puts("TEST", 100, 100)
	textdraw.puts("STRING", 300, 200)
	textdraw.flush()
