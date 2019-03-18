import datetime
import itertools
import server
import target
import multiprocessing as mp
import os


def generate_arguments():

    stations = ["abra", "jvgo"]
    intervals = ["0-1", "0-2"]
    start_date = datetime.datetime(2017, 01, 01)
    end_date = datetime.datetime(2017, 01, 2)

    dates = []
    aux = start_date
    while aux <= end_date:
        dates.append(aux)
        aux += datetime.timedelta(days=1)

    return list(itertools.product(stations, [intervals], dates))


if __name__ == "__main__":

    arguments = generate_arguments()

    requested_processes = 0
    MAX_PROCESSES = 10

    running_processes = []
    old_processes = []
    results = []

    while arguments or running_processes:

        server.communicate_with_processes(running_processes, results)
        total_processes, requested_processes = server.get_requested(running_processes)

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
                        p = mp.Process(target=target.foo, args=(argument, child_control_conn, child_data_conn))
                        p.start()
                        running_processes.append(server.Process(p, parent_control_conn, parent_data_conn, 0, 0, argument))

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

    for result in results:
        print("PID: {id}".format(id=result.id))
        for data in result.results:
            for element in data:
                print("\tArgumento: {arg}".format(arg=element.id))
                print("\t\t{val}".format(val=element.results))
