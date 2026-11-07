from threading import Thread
from time import sleep


class WorkerThread(Thread):
    def __init__(self, num, tab, val, dur):
        super().__init__()
        self.num = num
        self.tab = tab
        self.val = val
        self.dur = dur

    def run(self):
        print(f"Поток   {self.num} начал выполнение")
