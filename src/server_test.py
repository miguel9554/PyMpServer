import datetime
import itertools
import multiprocessing as mp


def foo(arg):
    pass


def get_requested():
    return 0


stations = ["abra", "esqu", "jvgo"]
intervals = ["0-1", "0-2"]
start_date = datetime.datetime(2017, 01, 01)
end_date = datetime.datetime(2017, 01, 10)

dates = []
aux = start_date
while aux <= end_date:
    dates.append(aux)
    aux += datetime.timedelta(days=1)

arguments = list(itertools.product(stations, [intervals], dates))

num_running = 0
num_requested = 0
MAX_PROCESS = 10

processes = []

while arguments:
    num_requested = get_requested()
    if num_requested == 0:
        if num_running <= MAX_PROCESS:
            for count in range(0, MAX_PROCESS - num_running):
                parent_conn, child_conn = mp.Pipe()
                p = mp.Process(target=foo, args=(arguments.pop(), child_conn))
                processes.append((p, parent_conn))
        else:
            exit("Error: mas procesos que el maximo")
    elif num_requested > 0:
        if num_running <= MAX_PROCESS:
            # arrancar MAX_PROCESS - num_running procesos
            pass
        else:
            exit("Error: mas procesos que el maximo")
    else:
        exit("Error: cantidad de pedidos negativa")
