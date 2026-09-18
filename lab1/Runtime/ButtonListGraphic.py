from tkinter import *
from functools import partial


class BLGraphic:

    def button_push(self, txt):
        self.scheduler.add_to_queue(txt, None)

    def __init__(self, buttons, schd):
        self.scheduler = schd
        self.win = Tk()
        self.win.title("Button List")
        for b in buttons:
            self.button = Button(self.win, text=b, command=partial(self.button_push, b))
            self.button.pack()

    def open_window(self):
        self.win.mainloop()
        self.scheduler.add_to_queue("window_closed", None)
