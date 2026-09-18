from Runtime import Scheduler
from Runtime import Timer

Execute_Transition = 0
Discard_Event = 1
Terminate_System = 2


class HumanHeartbeat:

    state = "idle"

    def __init__(self):
        self.scheduler = Scheduler.STMScheduler(self, "Human Heartbeat")
        self.t1 = Timer.StoppableTimer("t1", self.scheduler)
        self.scheduler.add_to_queue("start", None)
        self.scheduler.run_until_completion()
        self.N_threshold = 5
        self.n = 0

    def fire(self, event, data, scheduler):
        if self.state == "idle":
            if event == "start":
                self.N_threshold = 5
                self.n = 0
                print("Start!")
                self.t1.start_timer(1000)
                self.state = "active"
                return Execute_Transition
            elif event == "Exit":
                print("Exit from idle!")
                self.state = "final"
                return Execute_Transition
        elif self.state == "active":
            if event == "t1":
                print("Heartbeat!")
                self.n += 1
                if self.n >= self.N_threshold:
                    print("Terminate!")
                    self.state = "final"
                else:
                    self.t1.start_timer(1000)
                    self.state = "active"
                return Execute_Transition
            if event == "Stop":
                print("Stop!")
                self.t1.stop_timer()
                self.state = "idle"
                return Execute_Transition
            if event == "Exit":
                print("Exit from active!")
                self.state = "final"
                return Execute_Transition
        return Discard_Event


HumanHeartbeat()
