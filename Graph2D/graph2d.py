from Round2Dtemplate import Round2Dtemplate
from kivy.core.window import Window
import pandas as pd
from kivy.graphics import *
from kivy.properties import ObjectProperty
from kivymd.uix.filemanager import MDFileManager
from kivymd.uix.scrollview import MDScrollView


##
# generate test data
##
def gen_test_data1() ->tuple[list, list]:
    import numpy as np
    x = np.linspace(0, 2*np.pi, int(2*np.pi/0.1))
    y = np.cos(x)
    return x, y
def gen_test_data2() ->tuple[list, list]:
    import numpy as np
    x = np.linspace(0, 2*np.pi, int(2*np.pi/0.1))
    y = np.sin(x)
    return x, y
###

def float2str(v:float) -> str:
    if( abs(v) >= 1 and abs(v) < 1000) :
        return f'{v:3.1f}'
    elif(abs(v) < 1 and abs(v) > 0.001) :
        return f'{v:.3f}'
    else:
        return f'{v:.0e}'

from kivymd.uix.tab import MDTabsBase
from custom_common_widget import FloatInput, FocusedTextField
from kivymd.uix.boxlayout import BoxLayout
class MathEditDialog(MDScrollView):
    eval = ObjectProperty(None)
    cancel = ObjectProperty(None)
    focus_group: list = []
    next_focus: int = 0
    def __init__(self, **kwargs):
        super(MathEditDialog, self).__init__(**kwargs)
        self.ids.function_x.eval = self.eval
        self.ids.function_x.cancel = self.cancel
        self.ids.parametric2d.eval = self.eval
        self.ids.parametric2d.cancel = self.cancel

class Function_x(BoxLayout, MDTabsBase):
    eval = ObjectProperty(None)
    cancel = ObjectProperty(None)
    def fy(self):
        return self.ids.math_expr.text
    def xrange(self):
        return (self.ids.start.text, self.ids.end.text)
    def step(self):
        return self.ids.step.text
    def validate(self) :
        xs, xe = self.xrange()
        if(len(self.fy()) == 0 or len(self.step()) == 0
            or len(xs) == 0 or len(xe) == 0
            or len(self.step()) == 0
            ): return False
        return True

class Parametric2d(BoxLayout, MDTabsBase):
    eval = ObjectProperty(None)
    cancel = ObjectProperty(None)
    def fx(self):
        return self.ids.fx.text
    def fy(self):
        return self.ids.fy.text
    def trange(self):
        return(float(self.ids.ts.text), float(self.ids.te.text))
    def step(self):
        return float(self.ids.step.text)
    def validate(self):
        if (
        len(self.fx()) == 0 or len(self.fy()) == 0
        or len(self.ids.ts.text) == 0 or len(self.ids.te.text) == 0
        or len(self.ids.step.text) == 0
        ): return False
        return True

from custom_common_widget import show_info_message
from custom_common_widget import FloatInput
class Graph2d(Round2Dtemplate):
    data: list = []
    x_range: list=[0,0]
    y_range: list=[0, 0]
    r_x: float = 0;
    r_y: float = 0;
    x_axis: list=[0, 0, 0, 0]
    y_axis: list=[0, 0, 0, 0]
    view_port: list = [0,0,0,0]
    # left, right, top, bottom
    pad: list = [20, 20, 20, 20]
    xtick_str: list = []
    ytick_str: list = []
    color_list: list =[
            [229/255, 54/255, 228/255],
            [4/255, 251/255, 239/255],
            [1, 0, 0]
            ]
    ##
    # mouse x position
    ##
    mpos: int=0

    def __init__(self, **kwargs):
        super(Graph2d, self).__init__(**kwargs)
        Window.bind(mouse_pos=self.mouse_pos)
        self.tracker_line = None
        self.tracker_points:list = None
        import os
        self.file_manager = MDFileManager(
            exit_manager=self.exit_manager, select_path=self.select_path,
            current_path = os.path.expanduser("~"),
            ext=['.csv']
        )
        from kivymd.uix.dialog import MDDialog
        content = MathEditDialog(eval=self.eval, cancel=self.dismiss_popup)
        self._popup = MDDialog(title="Edit Math Expression", type="custom", content_cls=content)

    def select_path(self, path: str):
        self.add_plot_from_file(path)
        self.exit_manager()

    def exit_manager(self, *args):
        self.file_manager.close()

    def dismiss_popup(self):
        self._popup.dismiss()

    def on_new(self):
        self.data.clear()
        self.x_axis = [0, 0, 0, 0]
        self.y_axis = [0, 0, 0, 0]
        self.view_port = [0,0,0,0]
        self.pad = [20, 20, 20, 20]
        self.xtick_str = []
        self.ytick_str = []
        self.x_range = [0,0]
        self.y_range = [0, 0]
        self.r_x = 0;
        self.r_y = 0;
        self.fbo.clear()
        self.fbo.clear_buffer()
        self.text_top_right = ""

    def eval(self, instance):
        if instance.validate() is not True:
            show_info_message("you have to fill fields!")
            return
        if instance.title == 'function(x)':
            self.eval_function_x(instance)
        if instance.title == 'parametric':
            self.eval_parameteric(instance)

    def eval_parameteric(self, instance):
        from sympy import sympify
        import numpy as np
        from sympy.abc import t 
        try:
            fx = sympify(instance.fx())
            fy = sympify(instance.fy())
            ts, te = instance.trange()
            step = int(instance.step())
            input = np.linspace(ts, te, step)
            x:list = []
            y:list = []
            for tval in input :
                x.append(fx.subs(t, tval))
                y.append(fy.subs(t, tval))
        except:
            show_info_message("can't handle expression")
            return
        self.dismiss_popup()
        self.add_plot(x, y)

    def eval_function_x(self, instance):
        from sympy import sympify
        import numpy as np
        from sympy.abc import x
        try:
            f = sympify(instance.fy())
            xs, xe = instance.xrange()
            start:float = float(xs)
            end:float = float(xe)
            step = int(instance.step())
            input = np.linspace(start, end, step)
            y:list = []
            for t in input :
                y.append(f.subs(x, t))
        except:
            show_info_message("can't handle expression")
            return
        self.dismiss_popup()
        self.add_plot(list(input), y)
    def on_file_select(self):
        self.file_manager.show(self.file_manager.current_path)  # output manager to the screen

    def on_mathexpr_select(self):
        self._popup.open()

    def get_disp_format_string(self, x, y, num:int) -> str:
        fmt_str = ""
        ux = (self.x_range[1] - self.x_range[0])/num
        if(ux < 0.0001):
            format_str += str(f'({x:.5f}, ')
        elif(ux < 0.001):
            fmt_str += str(f'({x:.4f}, ')
        elif(ux < 0.01):
            fmt_str += str(f'({x:.3f}, ')
        elif(ux < 0.1):
            fmt_str += str(f'({x:.2f}, ')
        else :
            fmt_str += str(f'({x:.1f}, ')
        uy = (self.y_range[1] - self.y_range[0])/num
        if(uy < 0.1):
            fmt_str += str(f'{y:.4f})')
        else :
            fmt_str += str(f'{y:.1f})')
        return fmt_str

    def mouse_pos(self, window, pos):
        x, y = pos
        if(len(self.data) == 0) : return
        if x > self.pos[0] and x < self.pos[0]+ self.size[0]\
            and y > self.pos[1] and y < self.pos[1] + self.size[1]:
            self.mpos = x - self.pos[0]
        viewport = self.view_port
        x_range = self.x_range
        x = x_range[0] + (x_range[1] - x_range[0]) \
                * (self.mpos - viewport[0])/(viewport[2] - viewport[0])

        if (self.mpos >= viewport[0] and self.mpos <= viewport[2]):
            self.update_mouse_tracker(self.mpos)
        dx = x
        data_str = ""
        i = 0
        for _data in self.data :
            step = (x_range[1] - x_range[0])/_data.index.size
            df = _data[(_data.index >= dx) & (_data.index < (dx+step))]
            y=0
            if(df.index.size >= 1):
                x = df.index[0]
                y = df.values[0][0]
                if(len(data_str) > 0) : data_str += "\n"
                self.update_marker(i, x, y)
                data_str += self.get_disp_format_string(x, y, len(_data.index))
            i += 1
        self.text_top_right = data_str

    def calAxis(self, x: list, y: list):
        for val in x:
            if (val > self.x_range[1]):
                self.x_range[1] = val;
            if (val < self.x_range[0]):
                self.x_range[0] = val
        for val in y:
            if (val > self.y_range[1]):
                self.y_range[1] = val;
            if (val < self.y_range[0]):
                self.y_range[0] = val
    def set_pad(self, pad=list) :
        self.pad = pad

    def create_axis(self):
        size = self.size
        pad = self.pad
        if(self.x_range[0] == self.x_range[1]):
            self.x_range[0] = self.x_range[0]+1
        if(self.y_range[0] == self.y_range[1]):
            self.y_range[0] = self.y_range[0]+1
        self.view_port = [ pad[0], pad[3], size[0] - pad[1], size[1] - pad[2] ]
        viewport = self.view_port
        self.r_x = (viewport[2] - viewport[0])/( self.x_range[1]-self.x_range[0] )
        self.r_y = (viewport[3] - viewport[1])/( self.y_range[1]-self.y_range[0] )
        ##
        # x axis
        ##
        # start (x, y)
        self.x_axis[0] = viewport[0] # left pad
        self.x_axis[1] = viewport[1] # bottom pad
        # end (x, y)
        self.x_axis[2] = viewport[2]
        self.x_axis[3] = viewport[1] 
        ##
        # y axis
        ##
        # start (x, y)
        self.y_axis[0] = viewport[0] # left pad
        self.y_axis[1] = viewport[1] # bottom pad
        # endy(x, y)
        self.y_axis[2] = viewport[0] # left pad
        self.y_axis[3] = viewport[3] #widget height - top pad
        pass

    def draw_axis(self):
        self.kivy_instructions.add(Color(0,1,0)) # axis color
        self.kivy_instructions.add(Line(points=self.x_axis, width=1))
        self.kivy_instructions.add(Line(points=self.y_axis, width=1))

    def draw_data(self, x:list, y:list, color_idx: int):
        pt:list =[]
        i = 0;
        for v in x:
            v = (v - self.x_range[0])*self.r_x + self.view_port[0] 
            pt.append(v)
            v = (y[i] - self.y_range[0])*self.r_y + self.view_port[1] 
            pt.append(v)
            i += 1

        r, g, b = tuple(self.color_list[color_idx])
        self.kivy_instructions.add(Color(r, g, b)) # axis color
        self.kivy_instructions.add(Line(points=pt, width=1))

    def create_tick(self, num: int):
        ##
        # create tick label
        ##
        self.xtick_str.clear()
        self.ytick_str.clear()
        xtick_str = self.xtick_str 
        ytick_str = self.ytick_str 
        max_len: int = 0
        unit_tick_x : float = (self.x_range[1] - self.x_range[0])/(num + 1)
        unit_tick_y : float = (self.y_range[1] - self.y_range[0])/(num + 1)
        for i in range(1, num + 1):
            v = unit_tick_x * i + self.x_range[0]
            xtick_str.append(float2str(v))
            v = unit_tick_y * i + self.y_range[0]
            vstr:str = float2str(v)
            if(len(vstr) > max_len):
                max_len = len(vstr)
            ytick_str.append(vstr)
        self.pad[0] = max_len * self.textdraw.glyph_w
        self.pad[3] = self.textdraw.glyph_h + 10

    def draw_grid(self, num: int) :
        viewport = self.view_port
        unit_step_x : float = (viewport[2] - viewport[0])* 1/(num + 1)
        unit_step_y : float = (viewport[3] - viewport[1]) * 1/(num + 1)
        ##
        # horizontal grid
        ##
        pt:list=[]
        self.kivy_instructions.add(Color(1, 1, 1, 0.7)) # axis color
        for i in range(1, num+1):
            x = unit_step_x * i + viewport[0]
            pt.append(x)
            pt.append(viewport[1])
            pt.append(x)
            pt.append(viewport[3])
            self.kivy_instructions.add(Line(points=pt, width=1))
            offset = len(self.xtick_str[i-1])*self.textdraw.glyph_w/2
            self.textdraw.puts(self.xtick_str[i-1], x - offset, self.textdraw.glyph_h, [255, 255, 255])
            pt.clear()
            y = unit_step_y * i + viewport[1]
            pt.append(viewport[0])
            pt.append(y)
            pt.append(viewport[2])
            pt.append(y)
            self.kivy_instructions.add(Line(points=pt, width=1))
            self.textdraw.puts(self.ytick_str[i-1], viewport[0] - self.pad[0], y+self.textdraw.glyph_h/2, [255, 255, 255])
            pt.clear()
        self.kivy_instructions.add(Color(1, 1, 1, 0.5)) # axis color
        for i in range(0, num+1):
            pt.clear()
            x = unit_step_x * i + viewport[0] + unit_step_x/2
            pt.append(x)
            pt.append(viewport[1])
            pt.append(x)
            pt.append(viewport[3])
            self.kivy_instructions.add(Line(points=pt, dashes=[10, 5], width=1))
            pt.clear()
            y = unit_step_y * i + viewport[1] + unit_step_y/2
            pt.append(viewport[0])
            pt.append(y)
            pt.append(viewport[2])
            pt.append(y)
            self.kivy_instructions.add(Line(points=pt, dashes=[10, 5], width=1))
        pass

    #delimiter : " "
    def add_plot_from_file(self, filename: str):
        df = pd.read_csv(filename, sep=" ", index_col=0)
        x_values = df.index.values
        y_values = df.values
        y = [item for sublist in y_values for item in sublist]
        self.data.append(df)
        self.calAxis(x_values, y)
        self.plot()

    def draw_mouse_tracker(self):
        if(self.mpos <= self.view_port[0] 
                or self.mpos >= self.view_port[2]):
            self.tracker_points = None
            self.tracker_line = None
            return
        pt:list = []
        x = self.mpos
        pt.append(x)
        pt.append(self.view_port[1])
        pt.append(x)
        pt.append(self.view_port[3])
        self.kivy_instructions.add(Color(1, 0, 0, 0.7)) # axis color
        self.tracker_line = Line(points=pt, width=1)
        self.kivy_instructions.add(self.tracker_line)
        viewport = self.view_port
        x_range = self.x_range
        dx = x_range[0] + (x_range[1] - x_range[0]) \
                * (self.mpos - viewport[0])/(viewport[2] - viewport[0])
        self.kivy_instructions.add(Color(249/255, 253/255, 127/255, 1)) # marker color
        # display a marker at real data point.
        self.tracker_points = []
        for df in self.data :
            step = (x_range[1] - x_range[0])/df.index.size
            data = df.query('index >='+f'{dx:.5f} and index < '+f'{dx+step:.5f}').iloc[:1]
            if(len(data) == 1):
                x = viewport[0] + (data.index[0] - self.x_range[0])*self.r_x
                y = viewport[1] + (data.values[0][0]- self.y_range[0])*self.r_y
                tracker = Line(circle=(x, y, 5), width = 1)
                self.tracker_points.append(tracker)
                self.kivy_instructions.add(tracker)
    def update_mouse_tracker(self, x):
        if self.tracker_line == None : self.draw_mouse_tracker()
        if self.tracker_line == None : return
        pt:list = []
        pt.append(x)
        pt.append(self.view_port[1])
        pt.append(x)
        pt.append(self.view_port[3])
        self.tracker_line.points=pt

    def update_marker(self, i, dx, dy):
        if self.tracker_points == None : return
        viewport = self.view_port
        x = viewport[0] + (dx - self.x_range[0])*self.r_x
        y = viewport[1] + (dy - self.y_range[0])*self.r_y
        self.tracker_points[i].circle=(x, y, 5)

    def plot(self):
        self.create_tick(3)
        self.create_axis()
        self.kivy_instructions.clear()
        self.draw_axis()
        self.draw_grid(3)
        i = 0
        for _data in self.data :
            x:list = _data.index.values
            y:list = _data.values
            self.draw_data(x, y, i)
            i +=1
            if(i >= len(self.color_list)): i = 0
        self.draw_mouse_tracker()
        self.drawFlushRenderer()

    def add_plot(self, x: list, y: list):
        _data = pd.DataFrame(y, index=x, columns=['y'])
        self.data.append(_data)
        self.calAxis(x, y)
        self.plot()

    def update(self, instr):
        super().update(instr)

    def resize(self, *args):
        super().resize(*args)
        self._popup.content_cls.height=self.height
        self._popup.size = self.size
        self._popup.update_height()
        if( len(self.data) > 0 ):
            self.plot()

