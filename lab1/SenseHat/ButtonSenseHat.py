import threading
from sense_hat import SenseHat


class ButtonSH:

    def __init__(self, schd):
        self.scheduler = schd
        self.active = True
        self.sense = SenseHat()
        self.button_control = threading.Thread(target=self.button_ctr, daemon=False)
        self.button_control.start()

    def button_ctr(self):
        while self.active:
            for event in self.sense.stick.get_events():
                if event.action == "pressed" and event.direction == "middle":
                    self.scheduler.add_to_queue("button_pushed", None)

    def button_stop(self):
        self.active = False
