import sys
import time
import datetime


LOG_TO_TEXT_FILE = True
LOG_TO_STD_OUTPUT = True
# LOG_TO_HTML_FILE = True
LOG_FILENAME = 'log'


_mainLogger = None


def getLogger():
    global _mainLogger
    if _mainLogger is None:
        _mainLogger = Logger()
    return _mainLogger


class LogLevel:
    Debug = 0
    Info  = 1
    Warn  = 2
    Err   = 3
    Ex    = 4


class Logger():

    def __init__(self, ):
        self._levels = ['  Debug  ', '  Info   ', ' Warning ', '  Error  ', 'Exception']
        self._isClosed = False

        # if LOG_TO_TEXT_FILE:
        #     self._txtFile = open(LOG_FILENAME + ".txt", "ta")
        #     self._txtFile.write("\n---- LOG STARTED ----\n")

        # Open HTML log file
        # if LOG_TO_HTML_FILE:
        #     self._htmlFile = open(LOG_FILENAME + ".html", 'tw')


    def log(self, level=LogLevel.Info, text="", ommitPreTrace=False):
        if self._isClosed:
            raise Exception("Tried to log after closing.")

        _now = time.time()
        for _line in text.split('\n'):

            if not ommitPreTrace:
                _logStr = "%s [%s] %s" % (self._timeToAscii(_now), self._levels[level], _line)
            else:
                _logStr = _line

            if LOG_TO_STD_OUTPUT:
                print(_logStr)
                sys.stdout.flush()

            if LOG_TO_TEXT_FILE:
                # self._txtFile.write("\n" + _logStr)
                with open(LOG_FILENAME + ".txt", "ta") as _file:
                    _file.write("\n" + _logStr)

            # if LOG_TO_HTML_FILE:
            #     self._htmlFile.write("\n" + _logStr)


    def _timeToAscii(self, time):
        return datetime.datetime.fromtimestamp(time).strftime('%Y-%m-%d %H:%M:%S')


    def start(self):
        self.log(level=LogLevel.Info, text="-------------------------------------", ommitPreTrace=True)
        self.log(level=LogLevel.Info, text="----       Session started        ---", ommitPreTrace=True)
        self.log(level=LogLevel.Info, text="-------------------------------------", ommitPreTrace=True)


    def stop(self):
        # if LOG_TO_TEXT_FILE:
        #     self._txtFile.write("\n\n---- LOG FINISHED ----\n\n")
        #     self._txtFile.close()
        # if LOG_TO_HTML_FILE:
        #     self._htmlFile.close()
        # Close HTML log file
         self.log(level=LogLevel.Info, text="-------------------------------------", ommitPreTrace=True)
        self.log(level=LogLevel.Info, text="----      Session finished        ---", ommitPreTrace=True)
        self.log(level=LogLevel.Info, text="-------------------------------------", ommitPreTrace=True)
        self._isClosed = True


if __name__ == "__main__":
    _l = Logger()
    _l.log(LogLevel.Info, "hello")
