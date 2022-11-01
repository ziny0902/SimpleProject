from kivy.graphics import Color, Ellipse, Rectangle, Line
from kivy.uix.floatlayout import FloatLayout
from kivymd.uix.boxlayout import BoxLayout
from kivymd.uix.dialog import MDDialog
from kivymd.uix.label import MDIcon
from kivymd.uix.scrollview import MDScrollView
from sympy import lambdify
from Round2Dtemplate import Round2Dtemplate
from kivy.core.window import Window
from kivymd.uix.selectioncontrol import MDSwitch
from kivymd.uix.filemanager import MDFileManager
import numpy as np
import pandas as pd
import math
from util import *

class Camera():
    yaw:float = -90.
    pos:np.array= np.array([0., 0., 10.])
    front:np.array = np.array([0., 0., 0.])
    up:np.array = np.array([0., 1., 0.])
    pitch:float = 0.
    angle:list = [0., 0.]
    D:float = 10.
    def __init__(self, pos=[0., 0., 10.], front=[0., 0., 0], up=[0., 1., 0.]):
        self.pos = np.array(pos)
        self.front = np.array(front)
        self.up = np.array(up)
        self.angle=[0., 0.]
        self.pitch = 0.
        self.yaw = -90.
        self.D = math.sqrt(self.pos[0]*self.pos[0] + self.pos[1]*self.pos[1] + self.pos[2]*self.pos[2])

from kivy.graphics.transformation import Matrix
class Gizmo(FloatLayout):
    axis_x:list = [[], []]
    axis_y:list = [[], []]
    axis_z:list = [[], []]
    proj_mat:Matrix = Matrix()
    model_mat:Matrix = Matrix()
    def __init__(self, **kwargs):
        super(Gizmo, self).__init__(**kwargs)
        self.bind(pos=self.resize)
        self.bind(size=self.resize)
        # make Orthographic projection matrix
        self.proj_mat[10] = 0
        self.R = 6
        #
    def rotate(self, angle:list):
        m = Matrix()
        angle[1] = -angle[1]
        m.rotate(math.radians(angle[0]), math.cos(math.radians(angle[1])), 0, math.sin(math.radians(angle[1])))
        m.rotate(math.radians(angle[1]), 0, 1, 0)
        m.rotate(math.radians(angle[2]), 0, 0, 1)
        self.model_mat = m
        self.update_axis()
        pass
    def resize(self, *args):
        self.update_axis()
    def update_axis(self):
        x = self.axis_x
        y = self.axis_y
        z = self.axis_z
        model= self.model_mat
        proj = self.proj_mat
        pos = self.pos
        width = self.width
        height = self.height
        m=Matrix()
        x[0]=list(m.project(-0.7, 0,  0, model, proj, pos[0], pos[1], width, height))
        x[1]=list(m.project(0.7,  0,  0, model, proj, pos[0], pos[1], width, height))
        y[0]=list(m.project(0, -0.7,  0, model, proj, pos[0], pos[1], width, height))
        y[1]=list(m.project(0,  0.7,  0, model, proj, pos[0], pos[1], width, height))
        z[0]=list(m.project(0,  0, -0.7, model, proj, pos[0], pos[1], width, height))
        z[1]=list(m.project(0,  0,  0.7, model, proj, pos[0], pos[1], width, height))
        self.canvas.clear()
        with self.canvas:
            R = self.R
            ##
            # X --------
            ##
            Color(0., 0., 0., 0.)
            Rectangle(size=self.size, pos=self.pos)
            #4834d4
            c = rgbTocp(0x4834d4)
            Color(c[0], c[1], c[2], 0.5)
            Line(points=[x[0][0], x[0][1], x[1][0], x[1][1]], width=2)
            #686de0
            c = rgbTocp(0x686de0)
            Color(c[0], c[1], c[2])
            Ellipse(pos=(x[1][0]-R, x[1][1]-R), size=(14,14))
            #4834d4
            c = rgbTocp(0x4834d4)
            Color(c[0], c[1], c[2])
            Line(circle=(x[0][0], x[0][1], R), width = 2)
            ##
            # Y --------
            ##
            #6ab04c
            c = rgbTocp(0x6ab04c)
            Color(c[0], c[1], c[2], 0.5)
            Line(points=[y[0][0], y[0][1], y[1][0], y[1][1]], width=2)
            #badc58
            c = rgbTocp(0xbadc58)
            Color(c[0], c[1], c[2])
            Ellipse(pos=(y[1][0]-R, y[1][1]-R), size=(14,14))
            #6ab04c
            c = rgbTocp(0x6ab04c)
            Color(c[0], c[1], c[2])
            Line(circle=(y[0][0], y[0][1], R), width = 2)
            ##
            # Z --------
            ##
            #f0932b
            c = rgbTocp(0xf0932b)
            Color(c[0], c[1], c[2], 0.5)
            Line(points=[z[0][0], z[0][1], z[1][0], z[1][1]], width=2)
            #ffbe76
            c = rgbTocp(0xffbe76)
            Color(c[0], c[1], c[2])
            Ellipse(pos=(z[1][0]-R, z[1][1]-R), size=(14,14))
            #f0932b
            c = rgbTocp(0xf0932b)
            Color(c[0], c[1], c[2])
            Line(circle=(z[0][0], z[0][1], R), width = 2)

    def select_axis(self, touch) -> int:
        super().on_touch_down(touch)
        R = self.R
        x = self.axis_x
        y = self.axis_y
        z = self.axis_z
        pos = touch.pos
        R2 = R*R
        if( pos[0] < self.pos[0] or pos[1] < self.pos[1]) : return -1
        len0 = (x[0][0] - pos[0])*(x[0][0] - pos[0]) + (x[0][1] - pos[1])*(x[0][1] - pos[1])
        len1 = (x[1][0] - pos[0])*(x[1][0] - pos[0]) + (x[1][1] - pos[1])*(x[1][1] - pos[1])
        if len0 <= R2  or len1 <= R2:
            return 0  # X Axis
        len0 = (y[0][0] - pos[0])*(y[0][0] - pos[0]) + (y[0][1] - pos[1])*(y[0][1] - pos[1])
        len1 = (y[1][0] - pos[0])*(y[1][0] - pos[0]) + (y[1][1] - pos[1])*(y[1][1] - pos[1])
        if len0 <= R2  or len1 <= R2:
            return 1 # Y Axis
        len0 = (z[0][0] - pos[0])*(z[0][0] - pos[0]) + (z[0][1] - pos[1])*(z[0][1] - pos[1])
        len1 = (z[1][0] - pos[0])*(z[1][0] - pos[0]) + (z[1][1] - pos[1])*(z[1][1] - pos[1])
        if len0 <= R2  or len1 <= R2:
            return 2 # Z Axis
        return -1

from kivymd.uix.tab import MDTabsBase
from custom_common_widget import FloatInput, FocusedTextField
from kivy.properties import ObjectProperty
class Graph3dmeshMathEditor(MDScrollView):
    eval = ObjectProperty(None)
    dismiss = ObjectProperty(None)
    focus_group: list = []
    next_focus: int = 0
    def __init__(self, **kwargs):
        super(Graph3dmeshMathEditor, self).__init__(**kwargs)
        self.ids.function_xy.eval = self.eval
        self.ids.function_xy.dismiss = self.dismiss
        self.ids.parametric.eval = self.eval
        self.ids.parametric.dismiss = self.dismiss
class Graph3dlineMathEditor(MDScrollView):
    eval = ObjectProperty(None)
    dismiss = ObjectProperty(None)
    def __init__(self, **kwargs):
        super(Graph3dlineMathEditor, self).__init__(**kwargs)
        self.ids.parametric.eval = self.eval
        self.ids.parametric.dismiss = self.dismiss

class Function_xy(BoxLayout, MDTabsBase):
    eval = ObjectProperty(None)
    dismiss = ObjectProperty(None)
    def expr(self):
        return self.ids.f_xy_expr.text
    def xrange(self):
        return (self.ids.xstart.text, self.ids.xend.text)
    def yrange(self):
        return (self.ids.ystart.text, self.ids.yend.text)
    def step(self):
        return (self.ids.xstep.text, self.ids.ystep.text)
    def validate(self):
        if len(self.ids.f_xy_expr.text) == 0: return False
        elif len(self.ids.xstart.text) == 0: return False
        elif len(self.ids.ystart.text) == 0: return False
        elif len(self.ids.xend.text) == 0: return False
        elif len(self.ids.yend.text) == 0: return False
        elif len(self.ids.xstep.text) == 0: return False
        elif len(self.ids.ystep.text) == 0: return False
        return True
    def print_expr(self):
        if self.validate() is not True: return False
        print("f=", self.expr())
        xs, xe = self.xrange()
        print("x=[", xs, xe, "]")
        ys, ye = self.yrange()
        print("y=[", ys, ye, "]")
        xstep, ystep = self.step()
        print("step=[", xstep, ystep, "]")
        return True

class Parametric3dmesh(BoxLayout, MDTabsBase):
    eval = ObjectProperty(None)
    dismiss = ObjectProperty(None)
    def fx(self):
        return self.ids.f_x_expr.text
    def fy(self):
        return self.ids.f_y_expr.text
    def fz(self):
        return self.ids.f_z_expr.text
    def urange(self):
        return (self.ids.ustart.text, self.ids.uend.text)
    def ustep(self):
        return self.ids.ustep.text
    def vrange(self):
        return (self.ids.vstart.text, self.ids.vend.text)
    def vstep(self):
        return self.ids.vstep.text
    def validate(self):
        us, ue = self.urange()
        vs, ve = self.vrange()
        if ( len(self.fx()) == 0 or len(self.fy()) == 0 or  len(self.fz()) == 0
            or len(us) ==0 or len(ue) == 0 or len(vs) == 0 or len(ve) == 0 or len(self.ustep()) == 0
            or len(self.vstep()) == 0 ) : return False
        return True
    def print_expr(self):
        if self.validate() is not True: return False
        us, ue = self.urange()
        vs, ve = self.vrange()
        print("fx(u,v)) = ", self.fx())
        print("fy(u,v)) = ", self.fy())
        print("fz(u,v)) = ", self.fz())
        print("u=[", us, ue, self.ustep(), "]")
        print("v=[", vs, ve, self.vstep(), "]")
        return True

class Parametric3dline(BoxLayout, MDTabsBase):
    eval = ObjectProperty(None)
    dismiss = ObjectProperty(None)
    def x_expr(self):
        return self.ids.f_xt_expr.text
    def y_expr(self):
        return self.ids.f_yt_expr.text
    def z_expr(self):
        return self.ids.f_zt_expr.text 
    def t(self):
        return (self.ids.t_start.text, self.ids.t_end.text)
    def step(self):
        return self.ids.t_step.text
    def validate(self):
        if len(self.x_expr()) == 0: return False
        elif len(self.y_expr()) == 0: return False
        elif len(self.z_expr()) == 0: return False
        elif len(self.step()) == 0: return False
        ts, te = self.t()
        if len(ts) == 0 or len(te) == 0: return False
        return True
    def print_expr(self):
        if self.validate() is not True: return False
        ts, te = self.t()
        print("x=", self.x_expr())
        print("y=", self.y_expr())
        print("z=", self.z_expr())
        print("t=[", ts, te, "]")
        print("step=", self.step())
        return True

from kivy.lang import Builder
class Graph3d(Round2Dtemplate):
    Builder.load_string(
     '''
<Graph3dlineMathEditor>:
    size_hint_y: None
    BoxLayout:
        orientation: "vertical"
        size_hint_y: None
        height: "400dp"
        MDTabs:
            id: tabs
            Parametric3dline:
                id: parametric 
                
<Graph3dmeshMathEditor>:
    size_hint_y: None
    BoxLayout:
        orientation: "vertical"
        size_hint_y: None
        height: "440dp"
        MDTabs:
            id: tabs
            Function_xy:
                id: function_xy
            Parametric3dmesh:
                id: parametric
<Parametric3dline>:
    title: 'parametric'
    orientation: "vertical"
    spacing: "10dp"
    FocusedTextField:
        id: f_xt_expr 
        hint_text: "x(t) = "
        font_size: "20sp"
        text: "2*cos(t)"
    FocusedTextField:
        id: f_yt_expr 
        hint_text: "y(t) = "
        font_size: "20sp"
        text: "2*sin(t)"
    FocusedTextField:
        id: f_zt_expr 
        hint_text: "z(t) = "
        font_size: "20sp"
        text: "t/8"
    MDBoxLayout:
        spacing: "5dp"
        MDLabel:
            text: "t:"
            size_hint_x: None
            width: 40
            valign: 'center'
            font_style: 'H5'
        FloatInput:
            id: t_start
            hint_text: "from"
            mode: "rectangle"
            text: "0"
        FloatInput:
            id: t_end
            hint_text: "to"
            mode: "rectangle"
            text: "9.42477796076938"
        FloatInput:
            id: t_step
            hint_text: "step"
            mode: "rectangle"
            text: "100"
    MDBoxLayout:
        spacing: "20dp"
        adaptive_size: True
        pos_hint: {"center_x": .5, "center_y": .5}
        MDFlatButton:
            text: "Cancel"
            on_press: root.dismiss()
            font_size: '20sp'

        MDFlatButton:
            text: "Ok"
            on_press: root.eval(root)
            font_size: '20sp'
<Parametric3dmesh>:
    title: 'parametric'
    orientation: "vertical"
    spacing: "10dp"
    FocusedTextField:
        id: f_x_expr 
        hint_text: "x(u, v) = "
        font_size: "20sp"
        text: "(sqrt(2) * (cos(v) * cos(v)) * cos(2*u) + cos(u) * sin(2*v)) / (2 - sqrt(2) * sin(3*u) * sin(2*v))"
    FocusedTextField:
        id: f_y_expr 
        hint_text: "y(u, v) = "
        font_size: "20sp"
        text: "(sqrt(2) * ( cos(v) * cos(v)) * sin(2*u) - sin(u) * sin(2*v)) / (2 - sqrt(2) * sin(3*u) * sin(2*v))"
    FocusedTextField:
        id: f_z_expr 
        hint_text: "z(u, v) = "
        font_size: "20sp"
        text: "(3 * (cos(v) * cos(v))) / (2 - sqrt(2) * sin(3*u) * sin(2*v))"
    MDBoxLayout:
        spacing: "5dp"
        MDLabel:
            text: "u:"
            size_hint_x: None
            width: 40
            valign: 'center'
            font_style: 'H5'
        FloatInput:
            id: ustart
            hint_text: "from"
            mode: "rectangle"
            text: "-1.5707963267948966"
        FloatInput:
            id: uend
            hint_text: "to"
            mode: "rectangle"
            text: "1.5707963267948966"
        FloatInput:
            id: ustep
            hint_text: "step"
            mode: "rectangle"
            text: "50"
    MDBoxLayout:
        spacing: "5dp"
        MDLabel:
            text: "v:"
            size_hint_x: None
            width: 40
            valign: 'center'
            font_style: 'H5'
        FloatInput:
            id: vstart
            hint_text: "from"
            mode: "rectangle"
            text: "0"
        FloatInput:
            id: vend
            hint_text: "to"
            mode: "rectangle"
            text: "3.141592653589793"
        FloatInput:
            id: vstep
            hint_text: "step"
            mode: "rectangle"
            text: "50"

    MDBoxLayout:
        spacing: "20dp"
        adaptive_size: True
        pos_hint: {"center_x": .5, "center_y": .5}
        MDFlatButton:
            text: "Cancel"
            on_press: root.dismiss()
            font_size: '20sp'

        MDFlatButton:
            text: "Ok"
            on_press: root.eval(root)
            font_size: '20sp'

<Function_xy>:
    title: 'function(x,y)'
    orientation: "vertical"
    size_hint_y: None
    height: "280dp"
    spacing: "10dp"
    FocusedTextField:
        id: f_xy_expr 
        hint_text: "expression"
        font_size: "20sp"
        text: "x**2 - y**2"
    MDBoxLayout:
        spacing: "5dp"
        MDLabel:
            text: "x:"
            size_hint_x: None
            width: 40
            valign: 'center'
            font_style: 'H5'
        FloatInput:
            id: xstart
            hint_text: "from"
            mode: "rectangle"
            text: "-2"
        FloatInput:
            id: xend
            hint_text: "to"
            mode: "rectangle"
            text: "2"
        FloatInput:
            id: xstep
            hint_text: "step"
            mode: "rectangle"
            text: "50"
    MDBoxLayout:
        spacing: "5dp"
        MDLabel:
            text: "y:"
            size_hint_x: None
            width: 40
            valign: 'center'
            font_style: 'H5'
        FloatInput:
            id: ystart
            hint_text: "from"
            mode: "rectangle"
            text: "-2"
        FloatInput:
            id: yend
            hint_text: "to"
            mode: "rectangle"
            text: "2"
        FloatInput:
            id: ystep
            hint_text: "step"
            mode: "rectangle"
            text: "50"

    MDBoxLayout:
        spacing: "20dp"
        adaptive_size: True
        pos_hint: {"center_x": .5, "center_y": .5}
        MDFlatButton:
            text: "Cancel"
            on_press: root.dismiss()
            font_size: '20sp'

        MDFlatButton:
            text: "Ok"
            on_press: root.eval(root)
            font_size: '20sp'
    '''
    )
    class LineColors():
        #ff0096
        #189cff
        #8300ff
        #b6ff11
        #ff0303
        color_list=[ 0xff0096, 0x189cff, 0x8300ff, 0xb6ff11, 0xff0303 ]
        cur_idx = 0
        def getColor(self):
            ret = self.color_list[ self.cur_idx ]
            self.cur_idx += 1
            if self.cur_idx >= len( self.color_list ):
                self.cur_idx = 0
            return ret
    class Mouse():
        firstcall:bool = True
        last_x:int = 0
        last_y:int = 0
        def __init__(self):
            self.firstcall = True 
        def diff(self, pos:list) -> list:
            if self.firstcall :
                self.firstcall = False
                self.last_x = pos[0]
                self.last_y = pos[1]
            diff = [pos[0] - self.last_x, self.last_y - pos[1]]
            self.last_x = pos[0]
            self.last_y = pos[1]
            return diff

    angle: float = 0
    center: list = [0, 0, 0]
    scale: float = 1
    data = None
    def __init__(self, **kwargs):
        super(Graph3d, self).__init__(**kwargs)
        self._keyboard_open()
        self.set_default()
        self.gizmo = Gizmo(size_hint=(None, None), size=(100, 100))
        self.add_widget(self.gizmo)
        self.initialize_grid_onoff_switch()
        import os
        self.file_manager = MDFileManager(
            exit_manager=self.exit_manager, select_path=self.select_path,
            current_path = os.path.expanduser("~"),
            ext=['.csv']
        )

        # self.setup_scene()

    def set_default(self):
        self.angle = 0.
        self.center: list = [0., 0., 0.]
        self.scale: float = 1.
        self.max_distance = 10.
        self.mouse = Graph3d.Mouse()
        self.camera = Camera([0., 0., self.max_distance + 1.])
        camera = self.camera
        self.renderer3d.setup_camera(camera.pos, camera.front, camera.up)
        self.debug_renderer.setup_camera(camera.pos, camera.front, camera.up)
        self.renderer3d.reset_modelview()
        self.debug_renderer.reset_modelview()
        self.data = None
        
    ##
    # setup on/off switch
    ##
    def initialize_grid_onoff_switch(self):
        onoff_box = BoxLayout(orientation="horizontal", size_hint=(None, None),pos_hint={'top': 1., 'center_x': .5})
        self.grid_switch = MDSwitch(pos_hint={'center_y': .5} , active=True)
        self.grid_switch.bind(active = self.grid_on_off)
        grid_switch_label = MDIcon(icon="grid", pos_hint={'center_y': .5})
        onoff_box.add_widget(grid_switch_label)
        onoff_box.add_widget(self.grid_switch)
        self.add_widget(onoff_box)

    def grid_on_off(self, instance_switch, active_value: bool) :
        self.renderer3d.option["grid"] = active_value
        self.setup_scene()

    def on_new(self):
        self.set_default()
        self.setup_scene()

    def select_path(self, path: str):
        self.exit_manager()
        self.set_default()
        self.data = pd.read_csv(path, sep=" ", index_col=0)
        self.adjust_coordinate(self.data)
        self.setup_scene()

    def exit_manager(self, *args):
        self.file_manager.close()

    def on_file_select(self):
        self.file_manager.show(self.file_manager.current_path)  # output manager to the screen

    def resize(self, *args):
        super().resize(*args)
        self.gizmo.pos = (self.width - 100, self.height - 100)

    def _keyboard_open(self):
        self._keyboard = Window.request_keyboard(self._keyboard_closed, self)
        self._keyboard.bind(on_key_down=self._on_keyboard_down)

    def _keyboard_closed(self):
        self._keyboard.unbind(on_key_down=self._on_keyboard_down)
        self._keyboard = None

    def _on_keyboard_down(self, keyboard, keycode, text, modifiers):
        camera = self.camera
        if keycode[1] == 'w':
            camera.angle[0] += 3. 
        elif keycode[1] == 's':
            camera.angle[0] += -3.
        elif keycode[1] == 'a':
            camera.angle[1] += 3.
        elif keycode[1] == 'd':
            camera.angle[1] += -3.
        else: return
        if camera.angle[0] > 90. : camera.angle[0] = 89.
        elif camera.angle[0] < -90.: camera.angle[0] = -89.
        camera.pos[0] = camera.D*math.sin(math.radians(camera.angle[1])) * math.cos(math.radians(camera.angle[0]))
        camera.pos[1] = camera.D*math.sin(math.radians(camera.angle[0]))
        camera.pos[2] = camera.D*math.cos(math.radians(camera.angle[1])) * math.cos(math.radians(camera.angle[0]))
        self.renderer3d.setup_camera(camera.pos, camera.front, camera.up)
        self.debug_renderer.setup_camera(camera.pos, camera.front, camera.up)
        self.gizmo.rotate([camera.angle[0], camera.angle[1], 0])

    from  kivy.input.motionevent import MotionEvent
    def on_touch_down(self, touch:MotionEvent) -> bool:
        super(Graph3d, self).on_touch_down(touch)
        if (touch.is_touch) and (touch.button == 'left'):
            axis = self.gizmo.select_axis(touch)
            if axis >= 0 :
                self.reset_projection(axis)
                return False
            self.mouse.last_x = touch.pos[0] 
            self.mouse.last_y = touch.pos[1] 
        if touch.is_mouse_scrolling:
            if touch.button == 'scrolldown':
                self.pov += 1.
                if self.pov > 90. : self.pov = 90.
            elif touch.button == 'scrollup':
                self.pov -= 1.
                if self.pov < 1. : self.pov = 1.
            else: return False
            self.renderer3d.setup_projection(self.pov, self.width, self.height, self.near, self.far)
            self.debug_renderer.setup_projection(self.pov, self.width, self.height, self.near, self.far)
            return False
        return False 

    def reset_projection(self, axis:int):
        camera = self.camera
        if axis == 0 : # x axis y: 90 degree
            camera.angle[1] = 90.
            camera.angle[0] = 0.
        elif axis == 1 : #y axis x: 90 degree
            camera.angle[0] = 90.
            camera.angle[1] = 0.
        elif axis == 2 : #z axis 
            camera.angle[0] = 0.
            camera.angle[1] = 0.
        self.update_camera_pos()

    def update_camera_pos(self):
        camera = self.camera
        camera.pos[0] = camera.D*math.sin(math.radians(camera.angle[1])) * math.cos(math.radians(camera.angle[0]))
        camera.pos[1] = camera.D*math.sin(math.radians(camera.angle[0]))
        camera.pos[2] = camera.D*math.cos(math.radians(camera.angle[1])) * math.cos(math.radians(camera.angle[0]))
        self.renderer3d.setup_camera(camera.pos, camera.front, camera.up)
        self.debug_renderer.setup_camera(camera.pos, camera.front, camera.up)
        self.gizmo.rotate([camera.angle[0], camera.angle[1], 0])

    def on_touch_move(self, touch:MotionEvent):
        if (not touch.is_touch) or (not touch.button == 'left'):
            return False
        pos = touch.pos
        camera = self.camera
        if pos[0] < self.pos[0] or pos[0] > (self.pos[0]+self.width):
            return False
        sensitivity = 1
        diff = np.array(self.mouse.diff(pos)) * sensitivity
        camera.angle[1] += -1*diff[0]
        camera.angle[0] += 1*diff[1]
        if camera.angle[0] > 90 : camera.angle[0] = 90
        elif camera.angle[0] < -90 : camera.angle[0] = -90
        self.update_camera_pos()
        return True

    def adjust_coordinate(self, df):
        max_list = [df.index.max(), df.max(axis=0)['z'], df.max(axis=0)['y'] ]
        min_list = [df.index.min(), df.min(axis=0)['z'], df.min(axis=0)['y'] ]
        max = -1
        min = 1 
        for min_val, max_val in zip(min_list, max_list):
            if min > min_val : min = min_val
            if max < max_val : max = max_val
        # 4 x 4 world
        ratio = 8/(max - min) if not(min == max) else 1.
        center = self.center
        center[0] = (max_list[0] + min_list[0])/2
        center[1] = (max_list[1] + min_list[1])/2
        center[2] = (max_list[2] + min_list[2])/2
        self.scale = ratio
        self.renderer3d.reset_modelview()
        self.debug_renderer.reset_modelview()
        self.renderer3d.translate(-ratio*center[0], -ratio*center[1], -ratio*center[2])
        self.debug_renderer.translate(-ratio*center[0], -ratio*center[1], -ratio*center[2])
        self.renderer3d.scale(ratio, ratio, ratio)
        self.debug_renderer.scale(ratio, ratio, ratio)
        self.text_top_left = ( 
                f'max: [{max_list[0]:.1f}, {max_list[2]:.1f}, {max_list[1]:.1f}]\n' 
                + f'min: [{min_list[0]:.1f}, {min_list[2]:.1f}, {min_list[1]:.1f}]')
from custom_common_widget import show_info_message
from kivy.clock import Clock
from kivymd.uix.progressbar import MDProgressBar
import threading
class Graph3dline(Graph3d):
    def __init__(self, **kwargs):
        super(Graph3dline, self).__init__(**kwargs)
        content = Graph3dlineMathEditor(eval=self.on_eval, dismiss=self.on_dismiss)
        self.math_editor = MDDialog(title="Expression Dialog", 
                type="custom",
                content_cls=content,
                size_hint=(None, None)
                )
        progressbar = MDProgressBar(type="determinate", size_hint_y=None, height=100)
        self.progressbar = MDDialog(title="Calculating", 
                type="custom",
                content_cls=progressbar,
                )
    def eval_parametric(self, instance):
        from sympy import sympify
        from sympy.abc import t
        try:
            fx = sympify(instance.x_expr())
            fy = sympify(instance.y_expr())
            fz = sympify(instance.z_expr())
            ts, te = instance.t()
            numofstep = instance.step()

            ts = float(ts)
            te = float(te)
        except:
            show_info_message("can't handle expression")
            return
        self.on_dismiss()
        step = (te - ts)/float(numofstep)
        xval = []
        yval = []
        zval = []
        for tval in np.arange(ts, te, step):
            xval.append(fx.subs(t, tval))
            yval.append(fy.subs(t, tval))
            zval.append(fz.subs(t, tval))
        dict = {
                "x": list(xval),
                "y": list(yval),
                "z": list(zval)
                }
        self.data = pd.DataFrame(dict)
        self.data = self.data.set_index("x")
        Clock.schedule_once(self.update_graph)
    def update_graph(self, dt):
        self.adjust_coordinate(self.data)
        self.setup_scene()
        self.progressbar.dismiss()
    def on_eval(self, instance):
        if instance.validate() is not True : 
            show_info_message("you have to fill fields!")
            return
        self.on_new()
        if instance.title == 'parametric':
            self.loading = threading.Thread(target=self.eval_parametric, args=(instance,))
            self.loading.start()
            self.progressbar.open()
            self.progressbar.content_cls.start()
            self.eval_parametric(instance)
    def on_dismiss(self):
        self.math_editor.dismiss()
    def on_mathexpr_select(self):
        self.math_editor.open()

    def resize(self, *args):
        super().resize(*args)
        self.math_editor.content_cls.height=self.height
        self.math_editor.size = self.size
        self.math_editor.update_height()

    def setup_scene(self):
        if self.data is None : 
            self.set_default()
            self.drawFlushRenderer()
            return
        df = self.data
        line_colors = Graph3dline.LineColors()
        ptlist = []
        # parametric curve
        for i, x in zip(range(0, df.index.size), df.index) :
            ptlist.append([ x, df.iat[i, 1], df.iat[i, 0] ])
        color = np.array(rgbTocp(line_colors.getColor()))*255
        self.renderer3d.drawLinestrip(ptlist, color)

        ##
        #x-Axis
        #686de0
        c = np.array(rgbTocp(0x686de0))*255
        center = self.center
        scale = self.scale
        self.renderer3d.drawArrow( center, [0.03/scale, 0.7/scale], [c[0], c[1], c[2], 255], [c[0], c[1], c[2], 255], [1, 0, 0], 10)
        #y - Axis
        #badc58
        c = np.array(rgbTocp(0xbadc58))*255
        self.renderer3d.drawArrow( center, [0.03/scale, 0.7/scale], [c[0], c[1], c[2], 255], [c[0], c[1], c[2], 255], [0, 1, 0], 10)
        #z - Axis
        #f0932b
        c = np.array(rgbTocp(0xf0932b))*255
        self.renderer3d.drawArrow( center, [0.03/scale, 0.7/scale], [c[0], c[1], c[2], 255], [c[0], c[1], c[2], 255], [0, 0, 1], 10)
        self.drawFlushRenderer()

class Graph3dmesh(Graph3d):
    def __init__(self, **kwargs):
        super(Graph3dmesh, self).__init__(**kwargs)
        content = Graph3dmeshMathEditor(eval=self.on_eval, dismiss=self.on_dismiss)
        self.math_editor = MDDialog(title="Expression Dialog", 
                type="custom",
                content_cls=content,
                size_hint=(None, None)
                )
        progressbar = MDProgressBar(type="determinate", size_hint_y=None, height=100)
        self.progressbar = MDDialog(title="Calculating", 
                type="custom",
                content_cls=progressbar,
                )

    def on_mathexpr_select(self):
        self.math_editor.open()

    def on_eval(self, instance):
        if instance.validate() is not True : 
            show_info_message("you have to fill fields!")
            return
        self.on_new()
        if instance.title == "function(x,y)":
            self.loading = threading.Thread(target=self.eval_func_xy, args=(instance,))
            self.loading.start()
            self.progressbar.open()
            self.progressbar.content_cls.start()
            return
        if instance.title == "parametric":
            self.loading = threading.Thread(target=self.eval_parametric, args=(instance,))
            self.loading.start()
            self.progressbar.open()
            self.progressbar.content_cls.start()
            return

    def eval_parametric(self, instance):
        from sympy import sympify
        try:
            fx = sympify(instance.fx())
            fy = sympify(instance.fy())
            fz = sympify(instance.fz())
            us, ue = instance.urange()
            vs, ve = instance.vrange()
            numofustep = instance.ustep()
            numofvstep = instance.vstep()

            us = float(us)
            ue = float(ue)
            vs = float(vs)
            ve = float(ve)
            ustep = (ue - us)/float(numofustep)
            vstep = (ve - vs)/float(numofvstep)
        except:
            show_info_message("can't handle expression")
            return False
        self.on_dismiss()
        from sympy.abc import u, v
        from mesh import mesh_from_function
        fx = lambdify([u, v],fx)
        fy = lambdify([u, v],fy)
        fz = lambdify([u, v],fz)
        xval, yval, zval = mesh_from_function(lambda u, v: (
            fx(u, v),
            fy(u, v),
            fz(u, v)
            ),
            [us, ue, ustep], [vs, ve, vstep])

        dict = {
                "x": list(xval),
                "y": list(yval),
                "z": list(zval)
                }
        self.data = pd.DataFrame(dict)
        self.data = self.data.set_index("x")
        Clock.schedule_once(self.update_graph)
    def update_graph(self, dt):
        self.adjust_coordinate(self.data)
        self.setup_scene()
        self.progressbar.dismiss()

    def eval_func_xy(self, instance):
        from sympy import sympify
        from sympy.abc import x, y
        from mesh import mesh_from_function
        xval = None
        yval = None
        fval = None
        try:
            f = sympify(instance.expr())
            xs, xe = instance.xrange()
            ys, ye = instance.yrange()

            numofx, numofy= instance.step()
            xs = float(xs)
            xe = float(xe)
            ys = float(ys)
            ye = float(ye)
            xstep = (xe - xs)/float(numofx)
            ystep = (ye - ys)/float(numofy)
        except:
            show_info_message("can't handle expression")
            return False
        self.on_dismiss()
        fval = []
        xval = []
        yval = []
        fx = lambdify([x, y],x)
        fy = lambdify([x, y],y)
        fz = lambdify([x, y],f)
        xval, yval, fval = mesh_from_function(lambda x, y: (
            fx(x, y),
            fy(x, y),
            fz(x, y)
            ),
            [xs, xe, xstep], [ys, ye, ystep])
        dict = {
                "x": list(xval),
                "y": list(yval),
                "z": fval
                }
        self.data = pd.DataFrame(dict)
        self.data = self.data.set_index("x")
        Clock.schedule_once(self.update_graph)
        return True

    def on_dismiss(self):
        self.math_editor.dismiss()

    def resize(self, *args):
        super().resize(*args)
        self.math_editor.content_cls.height=self.height
        self.math_editor.size = self.size
        self.math_editor.update_height()

    def setup_scene(self):
        if self.data is None : 
            self.set_default()
            self.drawFlushRenderer()
            return
        df = self.data
        colors = Graph3dline.LineColors()
        fill_color = np.array(rgbTocp(colors.getColor()))*255

        ptlist = []
        for i in range(0, df.index.size, 3) :
            ptlist.clear()
            a = [ df.index[i], df.iat[i, 1], df.iat[i, 0] ]
            b = [ df.index[i+1], df.iat[i+1, 1], df.iat[i+1, 0] ]
            c = [ df.index[i+2], df.iat[i+2, 1], df.iat[i+2, 0] ]
            self.renderer3d.drawTriangle(a, c, b, fill_color, [0, 0, 0, 255], None, None)
        self.drawFlushRenderer()

if __name__ == "__main__":
    from kivymd.app import MDApp
    class graphApp(MDApp):
        def build(self):
            return Graph3dline()
    graphApp().run()
