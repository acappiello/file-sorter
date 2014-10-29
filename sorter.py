"""Runtime logic for FileSorter."""

__author__ = "Alex Cappiello"
__license__ = "See LICENSE.txt"


import os
import shutil
import time
import util


COPY = 0
MOVE = 1


MTIME = 0
CTIME = 1
ATIME = 2


class Sorter:

    def __init__(self):
        self.use_year = False
        self.use_month = False
        self.use_day = False
        self.use_dow = False
        self.use_hour = False
        self.use_minute = False
        self.use_second = False
        self.keep_directory = False
        self.recurse = True
        self.time_type = MTIME
        self.op_type = COPY

    def set_use_year(self, value):
        if (type(value) != bool):
            raise TypeError("Expected <type 'bool'>, got %s." % type(value))
        self.use_year = value

    def set_use_month(self, value):
        if (type(value) != bool):
            raise TypeError("Expected <type 'bool'>, got %s." % type(value))
        self.use_month = value

    def set_use_day(self, value):
        if (type(value) != bool):
            raise TypeError("Expected <type 'bool'>, got %s." % type(value))
        self.use_day = value

    def set_use_dow(self, value):
        if (type(value) != bool):
            raise TypeError("Expected <type 'bool'>, got %s: %s." % (type(value), value))
        self.use_dow = value

    def set_use_hour(self, value):
        if (type(value) != bool):
            raise TypeError("Expected <type 'bool'>, got %s." % type(value))
        self.use_hour = value

    def set_use_minute(self, value):
        if (type(value) != bool):
            raise TypeError("Expected <type 'bool'>, got %s." % type(value))
        self.use_minute = value

    def set_use_second(self, value):
        if (type(value) != bool):
            raise TypeError("Expected <type 'bool'>, got %s." % type(value))
        self.use_second = value

    def set_keep_directory(self, value):
        if (type(value) != bool):
            raise TypeError("Expected <type 'bool'>, got %s." % type(value))
        self.keep_directory = value

    def set_recurse(self, value):
        if (type(value) != bool):
            raise TypeError("Expected <type 'bool'>, got %s." % type(value))
        self.recurse = value

    def set_time_type(self, value):
        if (type(value) != type(MTIME)):
            raise TypeError("Expected %s, got %s." % (type(MTIME), type(value)))
        if (value != MTIME and value != CTIME and value != ATIME):
            raise ValueError("Value must be one of sorter.MTIME, sorter.CTIME, sorter.ATIME.")
        self.time_type = value

    def set_op_type(self, value):
        if (type(value) != type(MOVE)):
            raise TypeError("Expected %s, got %s." % (type(MOVE), type(value)))
        if (value != MOVE and value != COPY):
            raise ValueError("Value muse be either sorter.MOVE or sorter.COPY.")
        self.op_type = value

    def get_outdir(self, ts):
        out = ""

        if self.use_year:
            out += str(ts.tm_year) + os.sep
        if self.use_month:
            out += "%.2d%s" % (ts.tm_mon, os.sep)
        if self.use_day:
            out += "%.2d%s" % (ts.tm_mday, os.sep)
        if self.use_dow:
            days = ['Mon', 'Tues', 'Wed', 'Thurs', 'Fri', 'Sat', 'Sun']
            out += days[ts.tm_wday] + os.sep
        if self.use_hour:
            out += "%.2d%s" % (ts.tm_hour, os.sep)
        if self.use_minute:
            out += "%.2d%s" % (ts.tm_min, os.sep)
        if self.use_second:
            out += "%.2d%s" % (ts.tm_sec, os.sep)

        return os.path.normpath(out)  # normpath removes trailing os.sep.

    def run(self, src, dest):
        print src, dest
        if (not os.path.exists(src)):
            raise Exception("Source path not valid: %s" % (src))
        elif (not os.path.exists(dest)):
            raise Exception("Destination path not valid: %s" % (dest))
        if (dest.find(src) == 0):
            raise Exception("Destination must not be inside Source path.")

        src = os.path.normpath(src)
        dest = os.path.normpath(dest)

        history = {}

        w = os.walk(src)

        for root, dirs, files in w:
            print root

            for f in files:
                fullpath = os.path.join(root, f)
                if self.time_type == MTIME:
                    t = os.path.getmtime(fullpath)
                elif self.time_type == CTIME:
                    t = os.path.getctime(fullpath)
                elif self.time_type == ATIME:
                    t = os.path.getatime(fullpath)
                else:
                    raise Exception("time_type is not one of MTIME, CTIME, ATIME.")

                ts = time.localtime(t)

                if self.keep_directory:
                    subfolder = root[len(src)+1:]
                    outdir = os.path.join(dest, subfolder, self.get_outdir(ts))
                else:
                    outdir = dest + os.sep + self.get_outdir(ts)

                outfile = os.path.join(outdir, f)

                if outfile not in history and not os.path.exists(outfile):
                    version = 0
                else:
                    name = f
                    ext = ''
                    if name.rfind('.') > 0:  # Has ext and not .something.
                        (name, ext) = name.rsplit('.', 1)
                        ext = '.' + ext
                    if outfile not in history:
                        if name.rfind('_') != -1:
                            (tname, tver) = name.rsplit('_', 1)
                            try:
                                version = int(tver)
                                name = tname
                            except ValueError:
                                version = 1
                        else:
                            version = 1
                    else:
                        version = history[outfile]
                    fn = name + '_' + str(version) + ext
                    outfile = os.path.join(outdir, fn)
                    while os.path.exists(outfile):
                        version += 1
                        fn = name + '_' + str(version) + ext
                        outfile = os.path.join(outdir, fn)

                history[outfile] = version + 1

                print "in: %s, out: %s" % (fullpath, outfile)

                if not os.path.exists(outdir):
                    util.create_directory(outdir)
                if self.op_type == MOVE:
                    shutil.move(fullpath, outfile)
                else:
                    shutil.copy2(fullpath, outfile)

            if not self.recurse:
                break

