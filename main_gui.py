from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
import threading
import a9_script

class A9App(App):
    def build(self):
        layout = BoxLayout(orientation='vertical')
        self.status_label = Label(text='A9自动化脚本')
        layout.add_widget(self.status_label)

        start_btn = Button(text='开始运行')
        start_btn.bind(on_press=self.start_script)
        layout.add_widget(start_btn)

        stop_btn = Button(text='停止运行')
        stop_btn.bind(on_press=self.stop_script)
        layout.add_widget(stop_btn)

        return layout

    def start_script(self, instance):
        self.status_label.text = '脚本运行中...'
        threading.Thread(target=self.run_script).start()

    def stop_script(self, instance):
        self.status_label.text = '脚本已停止'

    def run_script(self):
        a9_script.main()

if __name__ == '__main__':
    A9App().run()