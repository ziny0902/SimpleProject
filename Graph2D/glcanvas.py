from kivy.base import EventLoop
from kivy.graphics import Callback
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.uix.relativelayout import FloatLayout
from kivy.graphics import Rectangle
from kivy.graphics.fbo import Fbo

# test
# from kivy.lang import Builder
# Builder.load_file('File.kv')

#class Glcanvas(RelativeLayout):
from kivymd.uix.relativelayout import MDRelativeLayout 
class Glcanvas(MDRelativeLayout):
    Resolution = (0.0, 0.0, 0.0, 0.0)
    Screen = (0.0,0.0)
    def __init__(self, **kwargs):
        EventLoop.ensure_window()
        super(Glcanvas, self).__init__(**kwargs)
        with self.canvas:
            self.cb = Callback(self.update, reset_context=False)
            self.fbo = Fbo (size=self.size, clear_color=(0., 0., 0., 0.))
            self.viewport = Rectangle(size=self.size, pos=self.pos)
        self.bind(pos=self.resize)
        self.bind(size=self.resize)
        Clock.schedule_interval(self.frame, 1 / 60.)

    def resize(self, *args):
        args = args
        self.fbo.size = self.size
        self.viewport.texture = self.fbo.texture
        self.viewport.size = self.size

    def update(self, instr):
        pass
    def frame(self, delta):
        pass
    def normalize(self, vertices):
        new_vertices=[]
        sz = self.size
        rw = sz[0] 
        rh = sz[1] 
        #print("[DEBUG] (w, h) =", sz)
        vlen = len(vertices)
        for i in range(0, vlen, 2):
            new_vertices.append(2*vertices[i]/rw - 1)
            new_vertices.append(2*vertices[i+1]/rh - 1)
        return self.screenTowidget(new_vertices)
    # vertices: normalize value
    def screenTowidget(self, vertices):
        sz = self.size
        pz = self.pos
        rw = sz[0] 
        rh = sz[1] 
        rx = pz[0] 
        ry = pz[1] 
        sw, sh = Window.size 
        rtx = rw/sw
        rty = rh/sh
        offx = rx * rtx
        offy = 1 - 2*(sh - (rh/2+ry))/sh 
        vlen = len(vertices)
        new_vertices=[]
        for i in range(0, vlen, 2):
            new_vertices.append(vertices[i]*rtx+ offx)
            new_vertices.append(vertices[i+1]*rty+ offy) 
        return new_vertices

# test block
if __name__ == "__main__":
    from kivy.uix.gridlayout import GridLayout
    class GridWidget(GridLayout):
        pass
    from kivy.app import App
    class TestApp(App):
        def build(self):
            return GridWidget()
    TestApp().run()
