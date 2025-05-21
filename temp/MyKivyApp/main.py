# main.py
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label

class MainLayout(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'

        self.label = Label(text="Welcome to Kivy!")
        self.add_widget(self.label)

        button = Button(text="Click me")
        button.bind(on_press=self.on_button_click)
        self.add_widget(button)

    def on_button_click(self, instance):
        self.label.text = "Button clicked!"

class MyApp(App):
    def build(self):
        return MainLayout()

if __name__ == "__main__":
    MyApp().run()
