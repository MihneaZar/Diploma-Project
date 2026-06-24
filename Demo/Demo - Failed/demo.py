from tkinter import Tk, Frame, Button, Label, DoubleVar, TOP, BOTTOM, HORIZONTAL, BOTH, DISABLED
from tkinter.ttk import Style, Progressbar 
from PIL import Image, ImageTk
from threading import Thread
from time import sleep
import os

from python_pipeline.process_concepts import * # pyright: ignore[reportMissingImports]

HOMEPATH = os.path.dirname(os.path.realpath(__file__))

MAIN_FONT = ("Arial", 20)
APP_SIZE  = (1450, 800)
BAR_WIDTH = 15

THREAD_NO = 10
THREADS_PER_LINE = 5
CHUNK_SIZE = DF_ROWS // THREAD_NO


# def thread_func(var):
#     val = 0
#     while val <= 100:
#         var.set(val)
#         val += 20
#         sleep(1)


def first_phase(overall_var, var_vect, start):
    start.config(state=DISABLED)

    threads = []
    for i in range(THREAD_NO):
        thread = Thread(target=lambda: thread_run(i, var_vect[i], data[CHUNK_SIZE * i:CHUNK_SIZE * (i + 1)]))
        thread.start()
        threads.append(thread)

    overall = sum([var.get() for var in var_vect]) // THREAD_NO
    while overall <= 100:
        new_val = sum([var.get() for var in var_vect]) // THREAD_NO
        # print([var.get() for var in var_vect])
        if  overall < new_val:
            overall = new_val
            overall_var.set(overall)

    for thread in threads:
        thread.join()


def main():
    root = Tk()
    root.geometry(f"{APP_SIZE[0]}x{APP_SIZE[1]}")
    root.resizable(False, False)

    root.title("Concepts Tracking in Research Papers")

    ico = Image.open(f"{HOMEPATH}/research.png")
    photo = ImageTk.PhotoImage(ico)
    root.wm_iconphoto(False, photo)

    style = Style()
    style.theme_use('default')
    style.configure("blue.Horizontal.TProgressbar", foreground='blue', background='blue')

    top = Frame(root)
    top.pack(side=TOP)

    overall_var = DoubleVar(value=0)

    Label(top, text="First Phase Progress", font=MAIN_FONT).pack()
    Progressbar(top, orient=HORIZONTAL, length=400, mode='determinate', style="blue.Horizontal.TProgressbar", variable=overall_var).pack(pady=10, ipady=BAR_WIDTH)

    bottom = Frame(root)
    bottom.pack(side=BOTTOM, pady=20, fill=BOTH, expand=True)

    var_vect = []
    for i in range(THREAD_NO // THREADS_PER_LINE + 1):
        for j in range(min(THREADS_PER_LINE, THREAD_NO - i * THREADS_PER_LINE)):
            new_var = DoubleVar(value=0)
            var_vect.append(new_var)
            Label(bottom, width=15, text=f"Thread #{i * THREADS_PER_LINE + j + 1}", font=MAIN_FONT).grid(row=i * 2, padx=20, column=j, ipady=BAR_WIDTH)
            Progressbar(bottom, orient=HORIZONTAL, length=200, mode='determinate', style="blue.Horizontal.TProgressbar", variable=new_var).grid(row=i * 2 + 1, padx=20, column=j, ipady=BAR_WIDTH / 2)

    start = Button(bottom, text="Start First Phase", font=MAIN_FONT)
    start.config(command=lambda: Thread(target=lambda: first_phase(overall_var, var_vect, start)).start())
    start.grid(row=9, column=2, pady=100)    

    root.mainloop()


if __name__ == "__main__":
    main()