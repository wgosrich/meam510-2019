# RoBALogs.py

from RoBAThreading import ProtectedLoop
import time


class LogLoop(ProtectedLoop):

    def __init__(self, filename):
        """Summary

        Args:
            host (TYPE): Description
            port (TYPE): Description
        """
        ProtectedLoop.__init__(self)
        self.filename = filename
        self.lines = []
    def prot_loop_startup(self):
        """Summary
        """
        print('Log File Thread #%s started: ' % self.ident  + self.filename)
        try:
            self.fh = open(self.filename, 'w')
        except IOError:
            self.fh = open(self.filename, 'w+')
        self.fh.close()


    def prot_loop_run(self):
        """Summary
        """
        time.sleep(1)
        while not self.fh.closed:
            time.sleep(.1)
        try:
            if self.lines:
                with open(self.filename, 'a') as self.fh:
                    for ind, line in enumerate(self.lines):
                        self.fh.write(self.lines.pop(0))
        except PermissionError as e:
            print(e, " trying again")

    def prot_loop_shutdown(self):
        """Summary
        """
        # ... Clean shutdown code here ...
        print('Thread #%s stopped' % self.ident)



    def write(self, line):
        """Summary

        Args:
            line (TYPE): Description
        """
        self.lines.append(line)

if __name__ == '__main__':

    try:
        test = LogLoop('testLog.txt')
        test.start()
        while True:
            test.write(str(time.time()))
            test.write('\n')
            time.sleep(.25)

    except KeyboardInterrupt:
        print("Ended by USER")

    finally:
        test.shutdownFlag.set()
        test.join()

