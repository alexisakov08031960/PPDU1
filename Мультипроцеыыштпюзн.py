import multiprocessing
import time
import random

def producer(queue, n_items):
    """Производитель, генерирует числа"""
    for i in range(n_items):
        item = random.randrange(1, 100)
        queue.put(item)
        print(f"Производитель {multiprocessing.current_process().name} создал {item}")
        time.sleep(random.uniform(0.5, 1.0))

def consumer(queue, n_producers):
    """Потребитель"""
    while True:
        item = queue.get()
        if item is None:
            n_producers -= 1
            if n_producers == 0:
                break
            continue
        result = item ** 2
        print(f"Получен -> {item}, изготовлен -> {result}")
        time.sleep(random.uniform(0.6, 2.0))
    print("Потребитель работу закончил")

if __name__ == "__main__":
    queue = multiprocessing.Queue()
    N = 10

    p_producer1 = multiprocessing.Process(target=producer, args=(queue, N), name="P1")
    p_producer2 = multiprocessing.Process(target=producer, args=(queue, N), name="P2")
    p_consumer = multiprocessing.Process(target=consumer, args=(queue, 2), name="C1")

    p_producer1.start()
    p_producer2.start()
    p_consumer.start()

    p_producer1.join()
    p_producer2.join()
    print("Все производители завершены")

    # сигналим потребителю, что данных больше не будет
    queue.put(None)
    queue.put(None)

    p_consumer.join()
    print("Главный процесс завершен")