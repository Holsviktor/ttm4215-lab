from Runtime import Scheduler, ButtonListGraphic
from SenseHat import ButtonSenseHat, SenseHatSetOff
from Runtime import Timer
from Runtime import PedestrianTrafficLightGraphic
import threading

from time import sleep
Execute_Transition = 0
Discard_Event = 1
Terminate_System = 2

yellow_light_time = 3_000 #ms
pedestrian_light_time = 10_000 # ms
car_time = 20_000 #ms

def is_raspberry_pi():
    return 1

class TrafficLight:

    state = "start"

    def __init__(self):
        self.scheduler = Scheduler.STMScheduler(self, "TrafficLight")



        self.TLGraphic = None
        if is_raspberry_pi():
            print("Hello! I am a berry happy raspberry pi. asdasdsa")
            self.TLGraphic = SenseHatSetOff.SenseHatSetOff()
            self.TLGraphic.switch_off()
            self.button_manager = ButtonSenseHat.ButtonSH(self.scheduler)
        else:
            self.TLGraphic = PedestrianTrafficLightGraphic.TLGraphic(self.scheduler)
            self.TLGraphic.open_window()
        print("main thread is not blocked")

        sleep(1)
        self.t1 = Timer.StoppableTimer("t1", self.scheduler)
        self.scheduler.add_to_queue("start", None)

        self.scheduler.run_until_completion()

    def fire(self, event, data, scheduler):
        if self.state == "start":
            if event == "start":
                print("Start!")
                self.t1.start_timer(car_time)
                self.TLGraphic.set_green("cars")
                self.TLGraphic.set_red("ped")

                self.state = "cars_green"
                return Execute_Transition


        elif self.state == ("cars_green"):
            if event == "t1":
                print("Heartbeat!")
                self.t1.start_timer(car_time)

                self.state = "cars_green"
                return Execute_Transition
            elif event == "button_pushed":
                print("Button pressed while green!")

                self.state = "green_light_pedestrian_waiting"
                return Execute_Transition


        elif self.state == ("green_light_pedestrian_waiting"):
            if event == "t1":
                print("Pedestriantimer in pedestrian waiting!")
                self.t1.start_timer(yellow_light_time)
                self.TLGraphic.set_yellow()

                self.state = "yellow_to_red"
                return Execute_Transition


        elif self.state == ("yellow_to_red"):
            if event == "t1":
                print("Pedestriantimer in pedestrian waiting!")
                self.TLGraphic.set_green("ped")
                self.TLGraphic.set_red("cars")
                self.t1.start_timer(pedestrian_light_time)

                self.state = "pedestrian_green"
                return Execute_Transition


        elif self.state == ("pedestrian_green"):
            if event == "t1":
                print("Pedestrians finished!")
                self.TLGraphic.set_red("ped")
                self.TLGraphic.set_red_yellow()
                self.t1.start_timer(yellow_light_time)

                self.state = "yellow_to_green"
                return Execute_Transition


        elif self.state == ("yellow_to_green"):
            if event == "t1":
                print("Light turning green without pedestrians!")
                self.TLGraphic.set_green("cars")
                self.t1.start_timer(car_time)

                self.state = "cars_green"
                return Execute_Transition
            if event == "button_pushed":
                print("Pedestrians waiting before cars have green!")

                self.state = "yellow_light_pedestrian_waiting"
                return Execute_Transition


        elif self.state == ("yellow_light_pedestrian_waiting"):
            if event == "t1":
                print("Pedestrians finished!")
                self.TLGraphic.set_green("cars")
                self.t1.start_timer(car_time)

                self.state = "green_light_pedestrian_waiting"
                return Execute_Transition

        return Discard_Event


TrafficLight()
