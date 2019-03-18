import datetime
import itertools
import multiprocessing as mp
import time
import os


class Process:
    
    def __init__(self, process, control_conn, data_conn, requested, children, id):
        
        self.process = process
        self.control_conn = control_conn
        self.data_conn = data_conn
        self.requested = requested
        self.children = children
        self.id = id


def foo((station, intervals, date), control_conn, data_conn):

    arguments = range(1, 9)

    control_conn.send("REQ {count}".format(count=str(len(arguments))))

    running_processes = []

    while arguments or running_processes:
        
        communicate_with_processes(running_processes, control_conn)

        if not control_conn.poll():
    
            continue
    
        else:

            approved_to_run = control_conn.recv()

            for i in range(approved_to_run):

                parent_control_conn, child_control_conn = mp.Pipe()
                parent_data_conn, child_data_conn = mp.Pipe()
                argument = arguments.pop()
                p = mp.Process(target=bar, args=(argument, child_control_conn, child_data_conn))
                p.start()
                running_processes.append(Process(p, parent_control_conn, parent_data_conn, 0, 0, argument))

    control_conn.send("END")


def bar(seconds, conn):
    time.sleep(seconds*3)
    conn.send("END")


def get_requested(running_processes):

    # look for data in active processes' pipes, if the end message is received stop tracking process

    requested_processes = 0
    child_processes = 0

    for process in running_processes:

        requested_processes += process.requested
        child_processes += process.children

    return len(running_processes) + child_processes, requested_processes


def communicate_with_processes(running_processes, conn=None):

    current_processes = len(running_processes)

    for process in running_processes:

        while process.conn.poll():

            recv = process.conn.recv()

            if recv == "END":

                process.conn.close()
                if process.process.is_alive():
                    process.process.terminate()
                running_processes.remove(process)
                break
            elif recv[:3] == "REQ":

                process.requested = int(recv[4:])

            elif recv[:4] == "DONE":

                process.children -= int(recv[5:])

            else:

                print(recv)

    if conn:
        finnished_processes = current_processes - len(running_processes)
        if finnished_processes:
            conn.send("DONE {count}".format(count=finnished_processes))


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

    while arguments or running_processes:

        communicate_with_processes(running_processes)
        total_processes, requested_processes = get_requested(running_processes)

        os.system('cls')
        for process in running_processes:
            print("Process: {process}".format(process=process.process))
            print("\tRequested: {req}".format(req=process.requested))
            print("\tChildren: {child}".format(child=process.children))
            print("")

        print("Procesos totales: {tot}".format(tot=total_processes))

        # if no subprocesses are requested, start new process

        if requested_processes == 0:

            if total_processes <= MAX_PROCESSES:

                if arguments:
                    # start MAX_PROCESSES - total_processes processes

                    for _ in range(MAX_PROCESSES - total_processes):

                        parent_control_conn, child_control_conn = mp.Pipe()
                        parent_data_conn, child_data_conn = mp.Pipe()
                        argument = arguments.pop()
                        p = mp.Process(target=foo, args=(argument, child_control_conn, child_data_conn))
                        p.start()
                        running_processes.append(Process(p, parent_control_conn, parent_data_conn, 0, 0, argument))

                        if not arguments:

                            break

            else:

                for process in running_processes:
                    process.control_conn.close()
                    if process.process.is_alive():
                        process.process.terminate()
                    running_processes.remove(process)
                exit("Error: mas procesos que el maximo")

        elif requested_processes >= 0:

            if total_processes <= MAX_PROCESSES:

                for process in running_processes:

                    children_processes_to_run = min(process.requested, MAX_PROCESSES - total_processes)

                    if children_processes_to_run:
                        process.control_conn.send(children_processes_to_run)
                        total_processes += children_processes_to_run
                        process.requested -= children_processes_to_run
                        process.children += children_processes_to_run
            else:

                for process in running_processes:
                    process.control_conn.close()
                    if process.process.is_alive():
                        process.process.terminate()
                    running_processes.remove(process)
                exit("Error: mas procesos que el maximo")

        else:

            for process in running_processes:
                process.control_conn.close()
                if process.process.is_alive():
                    process.process.terminate()
                running_processes.remove(process)
            exit("Error: cantidad de pedidos negativa")

    print("ya se procesaron todos los argumentos, cerrando")
