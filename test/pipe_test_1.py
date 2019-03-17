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
recv = []

while True:

    time.sleep(2)
    while parent_conn.poll():
        recv.append(parent_conn.recv())
    while recv:
        rcv = recv.pop()
        if rcv == "terminado":
            exit()
        else:
            print(rcv)

print("termina programa")