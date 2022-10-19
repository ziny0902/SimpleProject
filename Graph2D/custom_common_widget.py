
from kivymd.uix.textfield.textfield import MDTextField
class FocusedTextField(MDTextField):
    def keyboard_on_key_down(self, window, keycode, text, modifiers):
        modifier = ''
        if len(modifiers) > 0 :
            modifier = modifiers[0]
        if keycode[0] == 9 and not (modifier == 'shift'):
            next = self.get_focus_next()
            next.focus = True
            return True
        if keycode[0] == 9 and (modifier == 'shift'):
            prev = self.get_focus_previous()
            prev.focus = True
            return True
        super().keyboard_on_key_down(window, keycode, text, modifiers)
        return False
class FloatInput(MDTextField):
    input_filter = "float"

    def keyboard_on_key_down(self, window, keycode, text, modifiers):
        modifier = ''
        if len(modifiers) > 0 :
            modifier = modifiers[0]
        if keycode[0] == 9 and not (modifier == 'shift'):
            next = self.get_focus_next()
            next.focus = True
            return True
        if keycode[0] == 9 and (modifier == 'shift'):
            prev = self.get_focus_previous()
            prev.focus = True
            return True
        super().keyboard_on_key_down(window, keycode, text, modifiers)
        return False

def show_info_message(message:str):
    from kivymd.uix.snackbar import Snackbar
    from kivymd.uix.button import MDFlatButton
    from kivy.core.window import Window
    snackbar = Snackbar(
        text=message,
        snackbar_x="10dp",
        snackbar_y="10dp",
    )
    snackbar.size_hint_x = (
        Window.width - (snackbar.snackbar_x * 2)
    ) / Window.width
    snackbar.buttons = [
        MDFlatButton(
            text="OK",
            text_color=(1, 1, 1, 1),
            on_release=snackbar.dismiss,
        )
    ]
    snackbar.open()
