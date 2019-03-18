class Process:

    def __init__(self, process, control_conn, data_conn, requested, children, id):

        self.process = process
        self.control_conn = control_conn
        self.data_conn = data_conn
        self.requested = requested
        self.children = children
        self.id = id


class Result:

    def __init__(self, id, results=[]):

        self.id = id
        self.results = results


def get_requested(running_processes):

    requested_processes = 0
    child_processes = 0

    for process in running_processes:

        requested_processes += process.requested
        child_processes += process.children

    return len(running_processes) + child_processes, requested_processes


def communicate_with_processes(running_processes, results, conn=None):

    current_processes = len(running_processes)

    for process in running_processes:

        while process.control_conn.poll():

            recv = process.control_conn.recv()

            if recv == "END":

                result = Result(process.id)
                while process.data_conn.poll():
                    result.results.append(process.data_conn.recv())
                results.append(result)

                process.data_conn.close()
                process.control_conn.send("OUT")
                process.process.join()
                process.control_conn.close()
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
