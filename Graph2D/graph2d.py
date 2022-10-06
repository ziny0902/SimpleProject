from kivy.uix.boxlayout import BoxLayout
from Round2Dtemplate import Round2Dtemplate
from kivy.core.window import Window
import pandas as pd
from kivy.graphics import *
from kivy.uix.popup import Popup
from kivy.properties import ObjectProperty
from kivy.uix.floatlayout import FloatLayout
from  kivy.uix.textinput import TextInput


kv_test = """
<Gl2dGraph>:
    orientation: 'vertical'
    ActionBar:
        pos_hint: {'top': 1}
        ActionView:
            ActionPrevious:
                title: ''
                app_icon: ''
                with_previous: False
            ActionButton:
                icon: r'icon/file-document-plus.png'
                on_release: grah.on_file_select()
            ActionButton:
                icon: r'icon/calculator-variant-outline.png'
                on_release: grah.on_mathexpr_select()
    Graph2d:
        id:grah

<LoadDialog>:
    BoxLayout:
        size: root.size
        pos: root.pos
        orientation: "vertical"
        FileChooserListView:
            id: filechooser
            path: u'./'
            filters: ['*.csv']

        BoxLayout:
            size_hint_y: None
            height: 30
            Button:
                text: "Cancel"
                on_release: root.cancel()

            Button:
                text: "Load"
                on_release: root.load(filechooser.path, filechooser.selection)

<MathEditDialog>:
    BoxLayout:
        size: root.size
        pos: root.pos
        orientation: "vertical"
        TextInput:
            id: math_expr 
            on_text: root.on_text(self, self.text)
            on_focus: root.on_focus(self, 0)
        BoxLayout:
            size_hint_y: None
            height: 30
            Label:
                size_hint_x: None
                width: 50
                text: 'start'
            FloatInput:
                id: start
                on_focus: root.on_focus(self, 1)
                on_text: root.on_text(self, self.text)
            Label:
                size_hint_x: None
                width: 50
                text: 'end'
            FloatInput:
                id: end
                on_focus: root.on_focus(self, 2)
                on_text: root.on_text(self, self.text)
            Label:
                size_hint_x: None
                width: 110
                text: 'number of step'
            FloatInput:
                id: step
                on_focus: root.on_focus(self, 3)
                on_text: root.on_text(self, self.text)

        BoxLayout:
            size_hint_y: None
            height: 30
            Button:
                text: "Cancel"
                on_release: root.cancel()

            Button:
                text: "Evaluate"
                on_release: root.eval(math_expr.text, start.text, end.text, step.text)
"""

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

class LoadDialog(FloatLayout):
    load = ObjectProperty(None)
    cancel = ObjectProperty(None)

class MathEditDialog(FloatLayout):
    eval = ObjectProperty(None)
    cancel = ObjectProperty(None)
    focus_group: list = []
    next_focus: int = 0
    def __init__(self, **kwargs):
        from kivy.clock import Clock
        super(MathEditDialog, self).__init__(**kwargs)
        Clock.schedule_once(self.set_mathexpr_focus, 0.5)
    def set_mathexpr_focus(self, *args):
        self.ids.math_expr.focus = True
        self.next_focus = 1
        self.focus_group=[self.ids.math_expr, self.ids.start, self.ids.end, self.ids.step]
    def on_focus(self, instance, value):
        self.next_focus = (value+1)%4
        print("on_focus")
        pass
    def on_text(self, instance, value:str) :
        c = ' '
        print("on_text")
        if len(value) > 0:
            c = value[len(value) -1]
        if c == '\t':
            print("receive tab: ", self.next_focus)
            # instance.focus = False
            self.focus_group[self.next_focus].focus = True
            instance.text = value.split("\t")[0]

import re
class FloatInput(TextInput):
    pat:str = re.compile('[^0-9]')

    def insert_text(self, substring, from_undo=False):
        if substring == "\t":
            return super().insert_text(substring, from_undo=from_undo)

        pat = self.pat
        if '.' in self.text:
            s = re.sub(pat, '', substring)
        else:
            s = '.'.join(
                re.sub(pat, '', s)
                for s in substring.split('.', 1)
            )
        return super().insert_text(s, from_undo=from_undo)

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

    def dismiss_popup(self):
        self._popup.dismiss()

    def file_load(self, path:str, filenames:list):
        self.add_plot_from_file(filenames[0])
        self.dismiss_popup()

    def eval(self, expr: str, s:str, e:str, step:str):
        from sympy import sympify
        import numpy as np
        from sympy.abc import x
        f = sympify(expr)
        start:float = float(s)
        end:float = float(e)
        input = np.linspace(start, end, int(step))
        y:list = []
        for t in input :
            y.append(f.subs(x, t))
        self.add_plot(list(input), y)
        self.dismiss_popup()

    def on_file_select(self):
        content = LoadDialog(load=self.file_load, cancel=self.dismiss_popup)
        self._popup = Popup(title="Load csv file", content=content,
                            size_hint=(0.5, 0.7))
        self._popup.open()

    def on_mathexpr_select(self):
        content = MathEditDialog(eval=self.eval, cancel=self.dismiss_popup)
        self._popup = Popup(title="Edit Math Expression", content=content,
                            size_hint=(0.5, 0.5))
        self._popup.open()
        print("on_maxexpr_select")

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
        dx = x
        data_str = ""
        for _data in self.data :
            df = _data.query('index >='+f'{dx:.5f}').iloc[:1]
            y=0
            if(len(df) == 1):
                x = df.index[0]
                y = df.values[0][0]
                if(len(data_str) > 0) : data_str += "\n"
                data_str += self.get_disp_format_string(x, y, len(_data.index))
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
            self.textdraw.puts(self.ytick_str[i-1], 0, y+self.textdraw.glyph_h/2, [255, 255, 255])
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

    def draw_mouse_tracker(self):
        if(self.mpos <= self.view_port[0] 
                or self.mpos >= self.view_port[2]):
            return
        pt:list = []
        x = self.mpos
        pt.append(x)
        pt.append(self.view_port[1])
        pt.append(x)
        pt.append(self.view_port[3])
        self.kivy_instructions.add(Color(1, 0, 0, 0.7)) # axis color
        self.kivy_instructions.add(Line(points=pt, width=1))
        pt.clear()
        viewport = self.view_port
        x_range = self.x_range
        dx = x_range[0] + (x_range[1] - x_range[0]) \
                * (self.mpos - viewport[0])/(viewport[2] - viewport[0])
        self.kivy_instructions.add(Color(249/255, 253/255, 127/255, 1)) # marker color
        # display a marker at real data point.
        for df in self.data :
            data = df.query('index >='+f'{dx:.5f}').iloc[:1]
            if(len(data) == 1):
                x = viewport[0] + (data.index[0] - self.x_range[0])*self.r_x
                y = viewport[1] + (data.values[0][0]- self.y_range[0])*self.r_y
                self.kivy_instructions.add(Line(circle=(x, y, 5), width = 1))

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

    def update(self, instr):
        super().resize(instr)
        if( len(self.data) > 0 ):
            self.plot()

    def resize(self, *args):
        super().resize(*args)
        if( len(self.data) > 0 ):
            self.plot()

from kivy.lang import Builder
if __name__ == "__main__":
    Builder.load_string(kv_test)
    
    class Gl2dGraph(BoxLayout):
        pass
    from kivy.app import App
    class graph2dApp(App):
        def build(self):
            return Gl2dGraph()
    graph2dApp().run()