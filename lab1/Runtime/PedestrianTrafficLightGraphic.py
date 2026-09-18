from tkinter import *


class TLGraphic:

    car_red = False
    car_yellow = False
    car_green = True
    ped_red = True
    ped_green = False

    def __init__(self, schd):
        self.scheduler = schd
        self.win = Tk()
        self.win.title("Pedestrian Traffic Light")
        self.canvas = Canvas(width=200, height=300, bg="black")
        self.red_car_light = self.canvas.create_oval(10, 10, 90, 90, outline="gray", fill="black")
        self.yellow_car_light = self.canvas.create_oval(10, 110, 90, 190, outline="gray", fill="black")
        self.green_car_light = self.canvas.create_oval(10, 210, 90, 290, outline="gray", fill="black")
        self.red_ped_light = self.canvas.create_oval(110, 10, 190, 90, outline="gray", fill="black")
        self.green_ped_light = self.canvas.create_oval(110, 110, 190, 190, outline="gray", fill="black")
        self.canvas.pack()
        self.button = Button(self.win, text="Pedestrian", command=self.button_push)
        self.button.pack()

    def open_window(self):
        self.win.mainloop()
        self.set_off("ped")
        self.set_off("car")
        self.scheduler.add_to_queue("window_closed", None)

    def button_push(self):
        self.scheduler.add_to_queue("button_pushed", None)

    def set_colors(self):
        if self.car_red:
            self.canvas.itemconfig(self.red_car_light, fill='red')
        else:
            self.canvas.itemconfig(self.red_car_light, fill='black')
        if self.car_yellow:
            self.canvas.itemconfig(self.yellow_car_light, fill='yellow')
        else:
            self.canvas.itemconfig(self.yellow_car_light, fill='black')
        if self.car_green:
            self.canvas.itemconfig(self.green_car_light, fill='green')
        else:
            self.canvas.itemconfig(self.green_car_light, fill='black')
        if self.ped_red:
            self.canvas.itemconfig(self.red_ped_light, fill='red')
        else:
            self.canvas.itemconfig(self.red_ped_light, fill='black')
        if self.ped_green:
            self.canvas.itemconfig(self.green_ped_light, fill='green')
        else:
            self.canvas.itemconfig(self.green_ped_light, fill='black')

    def set_red(self, tlt):
        if tlt == "ped":
            self.ped_red = True
            self.ped_green = False
        else:
            self.car_red = True
            self.car_yellow = False
            self.car_green = False
        self.win.after(0, self.set_colors)

    def set_yellow(self):
        self.car_red = False
        self.car_yellow = True
        self.car_green = False
        self.win.after(0, self.set_colors)

    def set_red_yellow(self):
        self.car_red = True
        self.car_yellow = True
        self.car_green = False
        self.win.after(0, self.set_colors)

    def set_green(self, tlt):
        if tlt == "ped":
            self.ped_red = False
            self.ped_green = True
        else:
            self.car_red = False
            self.car_yellow = False
            self.car_green = True
        self.win.after(0, self.set_colors)

    def set_off(self, tlt):
        if tlt == "ped":
            self.ped_red = False
            self.ped_green = False
        else:
            self.car_red = False
            self.car_yellow = False
            self.car_green = False
        self.win.after(0, self.set_colors)
