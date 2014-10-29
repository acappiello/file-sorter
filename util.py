"""Misc. utilities for FileSorter."""

import os
import sys
import tkMessageBox
import multiprocessing

__author__ = "Alex Cappiello"
__license__ = "See LICENSE.txt"


def create_directory(dirname):
    """Traverse the directory name, creating as many new directories as
    needed to produce the full path. On failure, a string representing an error
    message is returned. On success, True is returned.
    """
    drive = os.path.splitdrive(dirname)[0]
    if (drive != "" and not os.path.exists(drive)):
        return "Drive doesn't exist: %s" % (drive)
    if (os.path.splitext(dirname)[1] != ""):
        return "Path is not a directory: %s" % (dirname)

    path = ""
    for folder in dirname.split(os.sep):
        path += folder + os.sep
        if (not os.path.exists(path)):
            try:
                os.mkdir(path)
            except:
                return "Could not create directory: %s" % (path)

    if (not os.path.exists(dirname) or not os.path.isdir(dirname)):
        return "Failed to create directory: %s" % (dirname)
    return True


def raise_error(msg):
    """Handle when things go wrong in some reasonable way.
    Cannot be used with multiprocessing on Linux."""
    print "Error: %s" % (msg)
    try:
        tkMessageBox.showerror("Error", msg)
    except:
        pass
    finally:
        sys.exit(1)


def multiproc_raise_error(msg_queue, msg):
    """Handle errors originating in subprocesses.
    Print error to terminal immediately, but the tkMessageBox will have to
    be produced by the parent.
    """
    print "Error: %s" % (msg)
    assert(type(msg_queue) == multiprocessing.queues.Queue)
    msg_queue.put(msg)
    sys.exit(1)


def flush_errors(msg_queue):
    """Sequentially dequeue and display all errors waiting in the queue."""
    assert(type(msg_queue) ==  multiprocessing.queues.Queue)
    while (not msg_queue.empty()):
        msg = msg_queue.get()
        try:
            tkMessageBox.showerror("Error", msg)
        except:
            print "Error: %s", msg
