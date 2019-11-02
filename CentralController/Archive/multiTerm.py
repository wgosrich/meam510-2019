import sys
import subprocess
from threading import Thread

try:
    from Queue import Queue, Empty
except ImportError:
    from queue import Queue, Empty # for Python 3.x

ON_POSIX = 'posix' in sys.builtin_module_names

def enqueue_output(out, queue):
    for line in iter(out.readline, b''):
        queue.put(line)
    out.close()

if __name__ == '__main__':
    logfile = open('logfile.txt', 'w')
    processes = [
                subprocess.Popen('python subproc_1.py', stdout=subprocess.PIPE, bufsize=1),
                subprocess.Popen('python subproc_2.py', stdout=subprocess.PIPE, bufsize=1),
                subprocess.Popen('python subproc_3.py', stdout=subprocess.PIPE, bufsize=1),
            ]
    q = Queue()
    threads = []
    for p in processes:
        threads.append(Thread(target=enqueue_output, args=(p.stdout, q)))

    for t in threads:
        t.daemon = True
        t.start()

    while True:
        try:
            line = q.get_nowait()
        except Empty:
            pass
        else:
            sys.stdout.write(line)
            logfile.write(line)
            logfile.flush()

        #break when all processes are done.
        if all(p.poll() is not None for p in processes):
            break

    print('All processes done')