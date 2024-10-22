from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import StringProperty
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.lang import Builder

from gui import MainScreen
from gui import ReorderableTableScreen


class ScreenTwo(Screen):
    pass


# Load the KV file
Builder.load_file('main.kv')

class MyApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(MainScreen(name='main'))
        sm.add_widget(ReorderableTableScreen(name='edit_replay'))
        sm.add_widget(ScreenTwo(name='screen_two'))
        return sm

if __name__ == '__main__':
    MyApp().run()
