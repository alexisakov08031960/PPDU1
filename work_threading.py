from threading import Thread
from time import sleep

class WorkThreading(Thread):
    def __init__(self, thread_id, prefix, count, delay):
        super().__init__()
        self.thread_id = thread_id
        self.prefix = prefix
        self.count = count
        self.delay = delay

    def run(self):
        for k in range(self.count):
            print(f'{self.prefix}Поток {self.thread_id}: Действие {k + 1}', flush=True)
            sleep(self.delay)
        print(f'{self.prefix}Поток {self.thread_id} завершил выполнение', flush=True)