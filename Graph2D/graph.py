from kivy.lang import Builder
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.screen import MDScreen
from kivymd.uix.screenmanager import MDScreenManager
from kivy.properties import ObjectProperty
from graph3d import Graph3dline, Graph3dmesh
from graph2d import Graph2d

if __name__ == "__main__":

    kv_test = """
<ContentNavigationDrawer>

    MDList:

        OneLineListItem:
            text: "Plot 2D Line"
            on_press:
                root.nav_drawer.set_state("close")
                root.screen_manager.current = "2d"
                root.app_bar.title = "2D Line"

        OneLineListItem:
            text: "Plot 3D Line"
            on_press:
                root.nav_drawer.set_state("close")
                root.screen_manager.current = "3dline"
                root.app_bar.title = "3D Line"

        OneLineListItem:
            text: "Plot 3D Mesh"
            on_press:
                root.nav_drawer.set_state("close")
                root.screen_manager.current = "3dmesh"
                root.app_bar.title = "3D Mesh"

MDScreen:
    MDTopAppBar:
        id: app_bar
        pos_hint: {"top": 1}
        title: "2D Line"
        right_action_items: 
            [
            ["trash-can-outline", lambda x: manager.current_graph(root).on_new() ],
            ["file-document-plus-outline", lambda x: manager.current_graph(root).on_file_select()],
            ["calculator-variant-outline", lambda x: manager.current_graph(root).on_mathexpr_select()],
            ]
        left_action_items: [["menu", lambda x: nav_drawer.set_state("open")]]
    MDNavigationLayout:
        pos_hint: {"bottom": 1}
        size_hint: 1, None
        height: root.height - app_bar.height
        GraphManager:
            id: manager
            Gl2dGraph:
                name: "2d"
                Graph2d:
                    id:grah2d
            Gl3dGraphLine:
                name: "3dline"
                Graph3dline:
                    id:graph3dline
            Gl3dGraphmesh:
                name: "3dmesh"
                Graph3dmesh:
                    id:graph3dmesh

        MDNavigationDrawer:
            id: nav_drawer
            radius: (0, 16, 16, 0)
            ContentNavigationDrawer:
                screen_manager: manager
                nav_drawer: nav_drawer
                app_bar : app_bar

<MathEditDialog>:
    size_hint_y: None
    BoxLayout:
        orientation: "vertical"
        size_hint_y: None
        height: "300dp"
        MDTabs:
            id: tabs
            Function_x:
                id: function_x
            Parametric2d:
                id: parametric2d
<Parametric2d>:
    title: "parametric"
    orientation: "vertical"
    spacing: "10dp"
    FocusedTextField:
        id: fx
        font_size: "20sp"
        hint_text: "x(t)="
        text: "sin(3*t)"
    FocusedTextField:
        id: fy
        font_size: "20sp"
        hint_text: "y(t)="
        text: "cos(5*t)"
    MDBoxLayout:
        spacing: "5dp"
        MDLabel:
            text: "t:"
            size_hint_x: None
            width: 40
            valign: 'center'
            font_style: 'H5'
        FloatInput:
            id: ts 
            hint_text: "start"
            mode: "rectangle"
            text: "0"
        FloatInput:
            id: te
            hint_text: "end"
            mode: "rectangle"
            text: "6.3"
        FloatInput:
            id: step
            hint_text: "step"
            mode: "rectangle"
            text: "100"

    MDBoxLayout:
        spacing: "20dp"
        adaptive_size: True
        pos_hint: {"center_x": .5, "center_y": .5}
        MDFlatButton:
            text: "Cancel"
            on_press: root.cancel()
            font_size: '20sp'

        MDFlatButton:
            text: "Ok"
            on_press: root.eval(root)
            font_size: '20sp'
<Function_x>:
    title: "function(x)"
    orientation: "vertical"
    spacing: "5dp"
    FocusedTextField:
        id: math_expr 
        font_size: "20sp"
        hint_text: "expression"
    MDBoxLayout:
        spacing: "5dp"
        FloatInput:
            id: start
            hint_text: "start"
            mode: "rectangle"
        FloatInput:
            id: end
            hint_text: "end"
            mode: "rectangle"
        FloatInput:
            id: step
            hint_text: "num of step"
            mode: "rectangle"

    MDBoxLayout:
        spacing: "20dp"
        adaptive_size: True
        pos_hint: {"center_x": .5, "center_y": .5}
        MDFlatButton:
            text: "Cancel"
            on_press: root.cancel()
            font_size: '20sp'

        MDFlatButton:
            text: "Ok"
            on_press: root.eval(root)
            font_size: '20sp'
    """
    class GraphManager(MDScreenManager):
        def current_graph(self, root):
            if self.current == "2d":
                return root.ids.grah2d
            elif self.current == "3dline":
                return root.ids.graph3dline
            elif self.current == "3dmesh":
                return root.ids.graph3dmesh
    class ContentNavigationDrawer(MDScrollView):
        screen_manager = ObjectProperty()
        nav_drawer = ObjectProperty()
        app_bar = ObjectProperty()
        
    class Gl2dGraph(MDScreen):
        pass

    class Gl3dGraphLine(MDScreen):
        pass

    class Gl3dGraphmesh(MDScreen):
        pass

    # from kivy.app import App
    from kivymd.app import MDApp
    class graphApp(MDApp):
        def build(self):
            self.theme_cls.theme_style = "Dark"
            from kivymd.font_definitions import theme_font_styles
            from kivy.core.text import LabelBase
            # using korean font
            LabelBase.register(
                name="KoPubWorld",
                fn_regular="font/KoPubWorld Dotum Medium.ttf")
            LabelBase.register(
                name="Mono",
                fn_regular="font/Ubuntu Mono Nerd Font Complete Mono.ttf")

            theme_font_styles.append('KoPubWorld')
            theme_font_styles.append('Mono')
            self.theme_cls.font_styles["Subtitle1"] = [
                "KoPubWorld",
                18,
                False,
                0.15,
            ]
            self.theme_cls.font_styles["Body1"] = [
                "Mono",
                18,
                False,
                0.15,
            ]
            return Builder.load_string(kv_test)
    graphApp().run()
