import threading
import queue

Execute_Transition = 0
Discard_Event = 1
Terminate_System = 2


def log(message):
    print(message)


class STMScheduler:

    inputQueue = queue.Queue()

    def __init__(self, p_stm, p_name):
        self.stm = p_stm
        self.name = p_name
        self.thr = threading.Thread(target=self.schd_thread, daemon=False)
        self.thr.start()

    def schd_thread(self):
        running = True
        while running:
            e = self.inputQueue.get()
            event = e.get("event")
            data = e.get("data")
            if data is None:
                log(self.name + ' firing event with name ' + event)
            else:
                log(self.name + ' firing event with name ' + event + ' and data ' + str(data))
            result = self.stm.fire(event, data, self)
            if result == Discard_Event:
                if data is None:
                    log(self.name + ': Discarded Event ' + event)
                else:
                    log(self.name + ': Discarded Event ' + event + ' and data ' + str(data))
            elif result == Terminate_System:
                log(self.name + ': Terminating System ... Bye, bye')
                running = False

    def add_to_queue(self, event, data):
        e = {"event": event, "data": data}
        self.inputQueue.put(e)

    def run_until_completion(self):
        self.thr.join()
