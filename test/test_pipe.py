import multiprocessing as mp
import time


def foo(arg, conn):
    conn.send("hola")
    conn.send("che")
    print(foo)
    time.sleep(5)
    conn.send("mandando que termine")
    conn.close()


mp.freeze_support()
parent_conn, child_conn = mp.Pipe()
p = mp.Process(target=foo, args=("hola", child_conn))
p.start()
while True:
    try:
        recv = parent_conn.recv()
        print(recv)
    except EOFError:
        print("terminado")
        break
print("termina programa")
p.join()