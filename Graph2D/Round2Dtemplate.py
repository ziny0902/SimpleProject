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
        Label:
            text: glCanvas.text_top_left #"Top left"
            text_size: self.width-10, self.height - 10
            valign: 'top'
            font_size: '15sp'
        Label:
            text: glCanvas.text_top_right
            text_size: self.width-10, self.height - 10
            valign: 'top'
            halign: 'right'
            font_size: '15sp'
        Label:
            text: glCanvas.text_bottom_left
            text_size: self.width-10, self.height - 10
            valign: 'bottom'
            font_size: '15sp'
        Label:
            text: glCanvas.text_bottom_right
            text_size: self.width-10, self.height-10
            valign: 'bottom'
            halign: 'right'
            font_size: '15sp'
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
        self.kivy_instructions = InstructionGroup()

    def resize(self, *args):
        super().resize(*args)
        self.renderer3d.setup_projection(self.width, self.height)

    def frame(self, delta):
        super().frame(delta)
        pass

    def drawFlushRenderer(self):
        #test
        self.fbo.bind()
        self.fbo.clear()
        self.fbo.clear_buffer()
        self.textdraw.flush()
        self.round2d.flush()
        self.renderer3d.flush()
        instructions = InstructionGroup()
        instructions.add(self.textdraw.renderer)
        instructions.add(self.round2d.renderer)
        instructions.add(self.kivy_instructions)
        instructions.add(self.renderer3d.renderer)
        self.fbo.add(instructions)
        self.fbo.release()

class TemplateTest(Round2Dtemplate):
    def __init__(self, **kwargs):
        self.mouse_circle= Line(circle=(0, 0, 0), width = 1);
        super(TemplateTest, self).__init__(**kwargs)
        Window.bind(mouse_pos=self.mouse_pos)
    def frame(self, delta):
        delta = delta
        # self.renderer3d.rotate(delta,self.width, self.height)
        pass
    def mouse_pos(self, window, pos):
        x, y = pos
        if x > self.pos[0] and x < self.pos[0]+ self.size[0]\
            and y > self.pos[1] and y < self.pos[1] + self.size[1]:
            self.mouse_circle.circle=(x - self.pos[0], y - self.pos[1], 10);
            self.text_top_left = str((x - self.pos[0], y - self.pos[1]))
        else:
            self.mouse_circle= Line(circle=(0, 0, 0), width = 1);
    def update(self, instr ):
        super().update(instr)
        #print("[DEBUG] display")
        # pos, angle, r, out, fill
        # test data.
        #3d rendering test
        triangle = [  [ 0.0, -0.25, -0.50],
                [ 0.0,  0.25,  0.00],
                [ 0.5, -0.25,  0.25],
                [-0.5, -0.25,  0.25] ];
        self.renderer3d.drawTriangle(triangle[2], triangle[1], triangle[3], [0, 255, 0, 255], [255, 255, 255, 255])
        self.renderer3d.drawTriangle(triangle[3], triangle[1], triangle[0], [35, 55, 155, 255], [255, 255, 255, 255])
        self.renderer3d.drawTriangle(triangle[0], triangle[1], triangle[2], [155, 0, 0, 255], [255, 255, 155, 255])
        self.renderer3d.drawTriangle(triangle[0], triangle[2], triangle[3], [155, 155, 155, 255], [255, 255, 255, 255])


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
    pass
if __name__ == "__main__":
    Builder.load_file('File.kv')
    class Glview(GridLayout):
        pass
    from kivy.app import App
    class TestApp(App):
        def build(self):
            return Glview()
            #return Round2Dtemplate()
    TestApp().run()
