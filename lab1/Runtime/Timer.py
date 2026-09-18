import threading


class StoppableTimer:

    def __init__(self, p_name, p_schd):
        self.name = p_name
        self.schd = p_schd
        self.delay = None
        self.timer = None

    def timeout(self):
        self.schd.add_to_queue(self.name, None)

    def start_timer(self, p_delay):
        self.delay = p_delay
        self.timer = threading.Timer(self.delay / 1000, self.timeout)
        self.timer.start()

    def stop_timer(self):
        self.timer.cancel()

    def reset_timer(self):
        self.stop_timer()
        self.timer = threading.Timer(self.delay / 1000, self.timeout)
        self.timer.start()
