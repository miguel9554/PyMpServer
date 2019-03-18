import time
import server
import multiprocessing as mp


def foo((station, intervals, date), control_conn, data_conn):

    arguments = range(1, 9)

    control_conn.send("REQ {count}".format(count=str(len(arguments))))

    running_processes = []
    results = []

    while arguments or running_processes:

        server.communicate_with_processes(running_processes, results, control_conn)

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
                running_processes.append(server.Process(p, parent_control_conn, parent_data_conn, 0, 0, argument))

    data_conn.send(results)
    control_conn.send("END")

    end = False

    while not end:
        if control_conn.poll():
            if control_conn.recv() == "OUT":
                end = True


def bar(seconds, control_conn, data_conn):

    #time.sleep(seconds/5)

    for data in [x for x in range(seconds*2)]:
        data_conn.send(data)

    control_conn.send("END")

    end = False

    while not end:
        if control_conn.poll():
            if control_conn.recv() == "OUT":
                end = True
