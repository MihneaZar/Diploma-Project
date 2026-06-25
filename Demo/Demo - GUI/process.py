from multiprocessing import Process
from threading import Thread

def first_phase(overall_var, var_vect, THREAD_NO, thread_run, data, CHUNK_SIZE):#, start):
    # start.config(state=DISABLED)

    threads = []
    for i in range(THREAD_NO):
        thread = Thread(target=lambda: thread_run(i, var_vect[i], data[CHUNK_SIZE * i:CHUNK_SIZE * (i + 1)]))
        thread.start()
        threads.append(thread)

    # t = Thread(target=lambda: first_phase(overall_var, var_vect))
    # t.start()
    # t.join()

    for thread in threads:
        thread.join()