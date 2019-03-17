import datetime
import itertools
import random
import multiprocessing as mp


class Process:
    
    def __init__(self, process, conn, requested, children):
        
        self.process = process
        self.conn = conn
        self.requested = requested
        self.children = children

    def run_children(self, count):
        
        if count:
            print(count)


def foo((station, intervals, date), conn):

    conn.send("Estacion {station}, intervalos {interval_0} y {interval_1} para el dia {date}".format(
        station=station,
        interval_0=intervals[0],
        interval_1=intervals[1],
        date=date))

    conn.send("REQ {count}".format(count=str(50)))
    
    while True:
        
        if not conn.poll():
    
            continue
    
        else:
    
            print("Puedo correr {count}".format(count=conn.recv()))
            break

    conn.send("END")


def get_requested():
    return 0


if __name__ == "__main__":

    stations = ["abra", "jvgo"]
    intervals = ["0-1", "0-2"]
    start_date = datetime.datetime(2017, 01, 01)
    end_date = datetime.datetime(2017, 01, 02)

    dates = []
    aux = start_date
    while aux <= end_date:
        dates.append(aux)
        aux += datetime.timedelta(days=1)

    arguments = list(itertools.product(stations, [intervals], dates))

    requested_processes = 0
    MAX_PROCESSES = 10

    running_processes = []

    while arguments:

        requested_processes = 0
        child_processes = 0

        for process in running_processes:

            requested_processes += process.requested
            child_processes += process.children

        # look for data in active processes' pipes, if the end message is received stop tracking process
        for process in running_processes:

            while process.conn.poll():

                recv = process.conn.recv()

                if recv == "END":

                    process.conn.close()
                    if process.process.is_alive():
                        process.process.terminate()
                    running_processes.remove(process)

                elif recv[:3] == "REQ":

                    process.requested = int(recv[4:])

                else:

                    print(recv)

        # check running, requested and max processes, decide which to start

        total_processes = len(running_processes) + child_processes

        # if no subprocesses are requested, start new process

        if requested_processes == 0:

            if total_processes <= MAX_PROCESSES:

                # start MAX_PROCESSES - total_processes processes

                for count in range(0, MAX_PROCESSES - total_processes):

                    parent_conn, child_conn = mp.Pipe()
                    p = mp.Process(target=foo, args=(arguments.pop(), child_conn))
                    p.start()
                    running_processes.append(Process(p, parent_conn, 0, 0))

                    if not arguments:

                        break

            else:

                exit("Error: mas procesos que el maximo")

        elif requested_processes > 0:

            if total_processes <= MAX_PROCESSES:

                for process in running_processes:

                    children_processes_to_run = min(process.requested, MAX_PROCESSES - total_processes)
                    process.run_children(children_processes_to_run)
                    total_processes += children_processes_to_run
                    process.requested -= children_processes_to_run
            else:

                exit("Error: mas procesos que el maximo")

        else:

            exit("Error: cantidad de pedidos negativa")

    while running_processes:

        requested_processes = 0
        child_processes = 0

        for process in running_processes:

            requested_processes += process.requested
            child_processes += process.children

        total_processes = len(running_processes) + child_processes

        for process in running_processes:

            while process.conn.poll():

                recv = process.conn.recv()

                if recv == "END":

                    process.conn.close()
                    if process.process.is_alive():
                        process.process.terminate()
                    running_processes.remove(process)

                elif recv[:3] == "REQ":

                    process.requested = int(recv[4:])

                else:

                    print(recv)

        if requested_processes >= 0:

            if total_processes <= MAX_PROCESSES:

                for process in running_processes:

                    children_processes_to_run = min(process.requested, MAX_PROCESSES - total_processes)
                    process.run_children(children_processes_to_run)
                    total_processes += children_processes_to_run
                    process.requested -= children_processes_to_run

            else:

                exit("Error: mas procesos que el maximo")

        else:

            exit("Error: cantidad de pedidos negativa")

    print("ya se procesaron todos los argumentos, cerrando")
