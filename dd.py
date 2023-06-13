from kivy.app import App
from kivy.lang import Builder
from kivy.uix.widget import Widget
from kivy.core.window import Window
from kivy.uix.actionbar import ActionButton
from kivy.uix.label import Label
from kivy.clock import Clock

Builder.load_string("""
<Tooltip>:
    size_hint: None, None
    size: self.texture_size[0]+5, self.texture_size[1]+5
    canvas.before:
        Color:
            rgb: 0.2, 0.2, 0.2
        Rectangle:
            size: self.size
            pos: self.pos

<MyWidget>
    ActionBar:
        ActionView:
            MyActionButton:
                icon: 'atlas://data/images/defaulttheme/audio-volume-high'
            MyActionButton:
                icon: 'atlas://data/images/defaulttheme/audio-volume-high'                
""")

class Tooltip(Label):
    pass

class MyActionButton(ActionButton):
    tooltip = Tooltip(text='Hello world')

    def __init__(self, **kwargs):
        Window.bind(mouse_pos=self.on_mouse_pos)
        super(ActionButton, self).__init__(**kwargs)

    def on_mouse_pos(self, *args):
        if not self.get_root_window():
            return
        pos = args[1]
        self.tooltip.pos = pos
        Clock.unschedule(self.display_tooltip) # cancel scheduled event since I moved the cursor
        self.close_tooltip() # close if it's opened
        if self.collide_point(*self.to_widget(*pos)):
            Clock.schedule_once(self.display_tooltip, 1)

    def close_tooltip(self, *args):
        Window.remove_widget(self.tooltip)

    def display_tooltip(self, *args):
        Window.add_widget(self.tooltip)


class MyWidget(Widget):
    pass

class ClientApp(App):
    def build(self):
        return MyWidget()

if __name__ == '__main__':
    ClientApp().run()