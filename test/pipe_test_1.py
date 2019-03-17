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


if __name__ == "__main__":

    parent_conn, child_conn = mp.Pipe()
    p = mp.Process(target=foo, args=("hola", child_conn))
    p.start()
    recv = []

    data = True
    parent_conn.send("test")
    while True:

        if parent_conn.poll():
            if not data:
                print("hay datos")
            data = True
            while parent_conn.poll():
                recv.append(parent_conn.recv())
            for data in recv:
                print("\tDato: {data}".format(data=data))
        else:
            if data:
                print("no hay datos")
            data = False
        while recv:
            rcv = recv.pop()
            if rcv == "terminado":
                exit()
            else:
                print(rcv)
