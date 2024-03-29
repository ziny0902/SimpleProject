from kivy.uix.gridlayout import GridLayout
from glcanvas import Glcanvas
from BasicTextDraw import BasicTextDraw
from Round2DRender import Round2DRender
from Renderer3D import Renderer3D
from kivy.graphics import InstructionGroup, Rectangle
from kivy.graphics import *
from kivy.graphics.instructions import InstructionGroup
from kivy.core.window import Window
from kivy.properties import StringProperty
from kivy.lang import Builder
import math

class Round2Dtemplate(Glcanvas):
    Builder.load_string(
'''
<Round2Dtemplate>:
    id: glCanvas
    text_top_left: ''
    text_top_right: ''
    text_bottom_left: ''
    text_bottom_right: ''
    GridLayout:
        size_hint: .95, .95
        pos_hint: {'center_x': .5, 'center_y': .5}
        cols:2
        rows:2
        MDLabel:
            text: glCanvas.text_top_left #"Top left"
            text_size: self.width-10, self.height - 10
            valign: 'top'
            font_size: '20sp'
        MDLabel:
            text: glCanvas.text_top_right
            text_size: self.width-10, self.height - 10
            valign: 'top'
            halign: 'right'
            font_size: '20sp'
        MDLabel:
            text: glCanvas.text_bottom_left
            text_size: self.width-10, self.height - 10
            valign: 'bottom'
            font_size: '20sp'
        MDLabel:
            text: glCanvas.text_bottom_right
            text_size: self.width-10, self.height-10
            valign: 'bottom'
            halign: 'right'
            font_size: '20sp'
'''
    )
    text_top_left = StringProperty('')
    text_top_right = StringProperty('')
    text_bottom_left = StringProperty('')
    text_bottom_right = StringProperty('')
    def __init__(self, **kwargs):
        super(Round2Dtemplate, self).__init__(**kwargs)
        self.round2d = Round2DRender()
        self.textdraw=BasicTextDraw()
        self.renderer3d = Renderer3D()
        self.debug_renderer = Renderer3D()
        self.pov:float = 45.
        self.far = 100
        self.near = 0.1
        self.kivy_instructions = InstructionGroup()

    def resize(self, *args):
        super().resize(*args)
        self.renderer3d.setup_projection(self.pov, self.width, self.height, self.near, self.far)
        self.debug_renderer.setup_projection(self.pov, self.width, self.height, self.near, self.far)

    def frame(self, delta):
        super().frame(delta)
        pass

    def update(self, instr ):
        super().update(instr)


    def drawFlushRenderer(self):
        #test
        self.fbo.clear()
        self.textdraw.flush()
        self.round2d.flush()
        self.renderer3d.flush()
        self.debug_renderer.flush()
        instructions = InstructionGroup()
        instructions.add(self.textdraw.renderer)
        instructions.add(self.round2d.renderer)
        instructions.add(self.kivy_instructions)
        instructions.add(self.renderer3d.renderer)
        instructions.add(self.debug_renderer.renderer)
        #infinite plane
        instructions.add(self.renderer3d.plane_renderer)
        self.fbo.add(instructions)

class TemplateTest(Round2Dtemplate):
    def __init__(self, **kwargs):
        self.mouse_circle= Line(circle=(0, 0, 0), width = 1);
        super(TemplateTest, self).__init__(**kwargs)
        Window.bind(mouse_pos=self.on_mouse_move)
        self.setup_scene()
        self.angle=0
        self.mouse_pos = (0, 0)
        self.renderer3d.setup_camera([0, 0, 10], [0, 0, 0], [0, 1, 0])

    def frame(self, delta):
        delta = delta
        super().frame(delta)
        self.angle += 0.3
        # self.renderer3d.rotate(self.angle, [1, 0, 0])
        cam_x = 10*math.sin( math.radians(self.angle) )
        cam_y = 10*math.cos( math.radians(self.angle) )
        self.renderer3d.setup_camera([cam_x, 0, cam_y], [0, 0, 1], [0, 1, 0])
        x, y = self.mouse_pos
        if x > self.pos[0] and x < self.pos[0]+ self.size[0]\
            and y > self.pos[1] and y < self.pos[1] + self.size[1]:
            self.text_top_left = str((x - self.pos[0], y - self.pos[1]))
            self.mouse_circle.circle=(x - self.pos[0], y - self.pos[1], 10)
        else:
            self.mouse_circle.circle=(0, 0, 1);
        pass

    def on_mouse_move(self, window, pos):
        diffx, diffy = self.mouse_pos 
        diffx -= pos[0]
        diffy -= pos[1]
        self.mouse_pos = pos
        cam_x = 1*math.sin(math.radians(pos[0]))
        cam_y = 1*math.cos(math.radians(pos[1]))
        # self.renderer3d.setup_camera([cam_x, 0, 2+cam_y], [0, 0, 0], [0, 1, 0])

    def setup_scene(self):
        #print("[DEBUG] display")
        # pos, angle, r, out, fill
        # test data.
        #3d rendering test
        # triangle = [  [ 0.0, -0.25, -0.50],
        #         [ 0.0,  0.25,  0.00],
        #         [ 0.5, -0.25,  0.25],
        #         [-0.5, -0.25,  0.25] ];
        # self.renderer3d.drawTriangle(triangle[2], triangle[1], triangle[3], [0, 255, 0, 255], [255, 255, 255, 255], [1,1,1], [0,0,0])
        # self.renderer3d.drawTriangle(triangle[3], triangle[1], triangle[0], [35, 55, 155, 255], [255, 255, 255, 255], [1,1,1], [0,0,0])
        # self.renderer3d.drawTriangle(triangle[0], triangle[1], triangle[2], [155, 0, 0, 255], [255, 255, 155, 255], [1,1,1], [0,0,0])
        # self.renderer3d.drawTriangle(triangle[3], triangle[0], triangle[2], [155, 155, 155, 255], [255, 255, 255, 255], [1,1,1], [0,0,0])
        # self.renderer3d.drawTriangle(triangle[2], triangle[1], triangle[3], [0, 255, 0, 255], [0, 0, 0, 255])
        # self.renderer3d.drawTriangle(triangle[3], triangle[1], triangle[0], [35, 55, 155, 255], [0, 0, 0, 255])
        # self.renderer3d.drawTriangle(triangle[0], triangle[1], triangle[2], [155, 0, 0, 255], [0, 0, 0, 255])
        # self.renderer3d.drawTriangle(triangle[3], triangle[0], triangle[2], [155, 155, 155, 255], [0, 0, 0, 255])
        ##
        # drawCube( center, size, fill, line )
        ##
        import numpy as np
        ptlist = []
        for t in np.arange(0, math.pi*2, math.pi*2/60.) :
            ptlist.append([math.cos(t), math.sin(t), t/(math.pi*2)])
        self.renderer3d.drawLinestrip(ptlist, [255, 255, 255, 255])
        self.renderer3d.drawCube( [2, 0, 2], [0.5, 0.5, 0.3], [0, 155, 0, 255], [255, 255, 255, 255] )
        self.renderer3d.drawPyramid( [0, 3, 0], [1, 0.5, 0.5], [155, 0, 0, 255], [255, 255, 255, 255])
        self.renderer3d.drawPyramid( [-1, 0, 0], [1, 0.5, 0.5], [155, 0, 0, 255], [255, 255, 255, 255], [0, -1, -1])
        self.renderer3d.drawCone( [-2, 3, 0], [0.5, 1], [155, 0, 0, 255], [255, 255, 255, 255], [1, -1, 1])
        self.renderer3d.drawCone( [2, 2, 0], [0.5, 1.5], [155, 0, 0, 255], [255, 255, 255, 255])
        self.renderer3d.drawCylinder( [2, -3, 0], [0.5, 1], [179, 127, 255, 255], [255, 255, 255, 255])
        self.renderer3d.drawCylinder( [-2, -3, 0], [0.5, 2], [179, 127, 255, 255], [255, 255, 255, 255], [1, 1, 0])
        self.renderer3d.drawSphere( [0, 2, 1], [1, 1], [155, 155, 155, 0], [255, 255, 255, 255])

        self.renderer3d.drawArrow( [3, 0, 0], [0.05, 0.5], [0, 0, 255, 255], [0, 0, 255, 255], [1, 0, 0], 10)
        self.renderer3d.drawArrow( [3, 0, 0], [0.05, 0.5], [0, 255, 0, 255], [0, 255, 0, 255], [0, 1, 0], 10)
        self.renderer3d.drawArrow( [3, 0, 0], [0.05, 0.5], [255, 0, 0, 255], [255, 0, 0, 255], [0, 0, 1], 10)
        ##


        ##
        # 2D Graphics example
        ##
        self.round2d.drawCircle([300, 300], 0, 50, [255, 255, 255, 255], [179, 127, 255, 255])
        self.round2d.drawPolygon(
                4,
                [[1000, 100], [1000,150], [400, 150], [400, 100]],
                10.,
                [255, 255, 255, 255],
                [179, 127, 255, 255]
                )
        self.round2d.drawPolygon(
                5,
                [[500, 300], [500, 400],  [450, 450], [400,400], [400, 300] ],
                5.,
                [255, 255, 255, 255],
                [179, 127, 255, 255]
                )
        self.textdraw.puts("TEST", 330, 400, [230, 226, 114, 255])
        self.kivy_instructions.clear()
        self.kivy_instructions.add(Color(1,0,0))
        self.kivy_instructions.add(Rectangle(pos=(100, 480), size=(100, 100)))
        self.kivy_instructions.add(Line(points=[100, 200, 200, 200, 100, 300], width=1))
        self.kivy_instructions.add(Color(1,1,1))
        self.kivy_instructions.add(self.mouse_circle)
        self.drawFlushRenderer()

    def update(self, instr ):
        super().update(instr)
    pass
if __name__ == "__main__":
    # from kivy.app import App
    from kivymd.app import MDApp
    class TestApp(MDApp):
        def build(self):
            self.theme_cls.theme_style = "Dark"
            return TemplateTest()
    TestApp().run()
