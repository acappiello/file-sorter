"""Tkinter-based GUI for FileSorter."""

import os
import platform
import sorter
import sys
from Tkinter import *
import tkFileDialog
import util

__author__ = "Alex Cappiello"
__license__ = "See LICENSE.txt"


import sys
import util


# Workaround for wonky Python handling of lambdas in the widget commands.
# Workaround for get() on BooleanVar returning an int.
lambda_wrapper = lambda f, v: lambda: f(v)
lambda_getbool_wrapper = lambda f, v: lambda: f(bool(v.get()))


class Gui:

    @staticmethod
    def browse_for_file(e):
        """Pull up a file browsing dialog and dump the resulting path into the
        Tkinter.Entry widget e."""
        path = tkFileDialog.askopenfilename(filetypes=[("PNG", ".png")])
        if (path != ""):  # Unless they hit cancel.
            e.delete(0, END)
            e.insert(0, path)

    @staticmethod
    def browse_for_folder(e):
        """Pull up a folder browsing dialog and dump the resulting path into
        the Tkinter.Entry widget e."""
        path = tkFileDialog.askdirectory()
        if (path != ""):  # Unless they hit cancel.
            e.delete(0, END)
            e.insert(0, path)

    def init_extras_dict(self):
        """Extras is the category of other unrelated options.
        Dictionary format is:
        display text : (action on button press, checked on default)
        """
        d = dict()
        d["Recurse into subfolders."] = (self.sorter.set_recurse, True)
        d["Preserve directory structure."] = \
            (self.sorter.set_keep_directory, False)
        self.extras_dict = d

    def init_path_inputs(self):
        """Add an Entry field to the GUI for each file and one for the working
        directory. Each is in its own Frame with a browse Button."""

        Label(self.canvas, text="Source directory:").pack(anchor="w")
        container = Frame(self.canvas)
        source_path = Entry(container, width=80)
        source_path.pack(side=LEFT)
        self.source_path = source_path
        Button(container, text="Browse",
               command=
               lambda: Gui.browse_for_folder(source_path)).pack(side=LEFT)
        container.pack()

        Label(self.canvas,
              text="Destination directory (must not be in source):").pack(anchor="w")
        container = Frame(self.canvas)
        dest_path = Entry(container, width=80)
        dest_path.pack(side=LEFT)
        self.dest_path = dest_path
        Button(container, text="Browse",
               command=
               lambda: Gui.browse_for_folder(dest_path)).pack(side=LEFT)
        container.pack()

    def init_time_checkboxes(self, parent):
        """Add checkboxes to the GUI for each date/time component."""
        components = [
            ('Year', self.sorter.set_use_year),
            ('Month', self.sorter.set_use_month),
            ('Day', self.sorter.set_use_day),
            ('Day of Week', self.sorter.set_use_dow),
            ('Hour', self.sorter.set_use_hour),
            ('Minute', self.sorter.set_use_minute),
            ('Second', self.sorter.set_use_second)
            ]
        defaults = ['Year', 'Month', 'Day']
        checkboxes = Frame(parent)
        Label(checkboxes, text="Organize based on:").pack()
        for (component, action) in components:
            state = BooleanVar()
            box = Checkbutton(checkboxes, text=component, variable=state,
                              onvalue=True, offvalue=False,
                              command=lambda_getbool_wrapper(action, state))
            box.pack(anchor="w")
            if (component in defaults):
                box.select()
                action(bool(state.get()))

        checkboxes.pack(side=LEFT)

    def init_selectors(self, parent):
        """Add radio buttons to select which time to look at and copy/move."""
        options = [(sorter.MTIME, 'Modification Time'),
                   (sorter.ATIME, 'Access Time')]
        if ('Windows' in platform.platform()):
            options += [(sorter.CTIME, 'Creation Time')]
        else:
            options += [(sorter.CTIME, 'Metadata Change Time')]

        radiobuttons = Frame(parent)
        Label(radiobuttons, text="Time Option:").pack()
        self.time_type = IntVar()

        for (short_name, long_name) in options:
            radio = Radiobutton(radiobuttons, text=long_name,
                                variable=self.time_type, value=short_name,
                                command=lambda_wrapper(self.sorter.set_time_type, short_name))
            radio.pack(anchor="w")

        self.time_type.set(sorter.MTIME)

        Label(radiobuttons, text="Operation Type:").pack()
        self.op_type = IntVar()

        Radiobutton(radiobuttons, text="Copy Files", variable=self.op_type,
                    command=lambda: self.sorter.set_op_type(sorter.COPY),
                    value=sorter.COPY).pack(anchor="w")
        Radiobutton(radiobuttons, text="Move Files", variable=self.op_type,
                    command=lambda: self.sorter.set_op_type(sorter.MOVE),
                    value=sorter.MOVE).pack(anchor="w")

        self.op_type.set(sorter.COPY)
        self.sorter.set_op_type(sorter.COPY)

        radiobuttons.pack(side=LEFT, anchor="n")

    def init_options(self):
        """Wrapper for calling everything in the Frame for various options."""
        opt_box = Frame(self.canvas)
        self.init_time_checkboxes(opt_box)
        self.init_selectors(opt_box)
        self.init_extras(opt_box)
        opt_box.pack(anchor="w")

    def init_extras(self, parent):
        """Various options that don't fall into any more broad category."""
        self.init_extras_dict()

        extras_box = Frame(parent)
        Label(extras_box, text="Other options:").pack(anchor="w")
        for item in self.extras_dict.keys():
            state = BooleanVar()
            (action, default) = self.extras_dict[item]
            button = Checkbutton(extras_box, text=item, variable=state,
                        command=lambda_getbool_wrapper(action, state))
            if (default):
                button.select()
                action(state.get())
            button.pack(anchor="w")

        extras_box.pack(side=LEFT, anchor="nw")

    def build(self):
        """Wrapper for calling init functions for various other pieces of the
        GUI."""
        self.init_path_inputs()
        self.init_options()

        start = Button(self.canvas, text="Start",
                       command=lambda: self.start())
        start.pack(side=RIGHT)

    def start(self):
        print self.sorter.__dict__

        self.sorter.run(self.source_path.get(), self.dest_path.get())

    def __init__(self):
        """Create the root and canvas. Then, build the GUI and run."""
        root = Tk()

        self.sorter = sorter.Sorter()
        self.canvas = Canvas(root)
        self.canvas.pack()
        root.resizable(width=0, height=0)

        self.build()
        # and launch the app
        # This call BLOCKS (so your program waits until you close the window!)
        root.mainloop()
