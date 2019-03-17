import multiprocessing as mp
import time


def foo(arg, conn):
    conn.send("hola")
    conn.send("che, el argumento que reicibi es {arg}".format(arg=arg))
    conn.send("ahora voy a dormir por 5 segundos")
    time.sleep(5)
    conn.send("mandando que termine")
    conn.send("terminado")
    conn.close()


parent_conn, child_conn = mp.Pipe()
p = mp.Process(target=foo, args=("hola", child_conn))
p.start()
time.sleep(2)
while True:
    recv = parent_conn.recv()
    if recv == "terminado":
        break
    else:
        print(recv)
print("termina programa")