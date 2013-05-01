################################################################################

import argparse
import sys
import gtk
import logging
from itertools import product
import shlex

################################################################################

def main(argv):
    args = parse_commandline_args(argv)
    set_loglevel(args.verbosity) 
    logging.info("commandline args: %s", args)
    axes = parse_axes_config(args.N)
    logging.info("axes: %s", axes)
    app = UI(axes, callback=groovy_filter)
    gtk.main()

################################################################################

def parse_axes_config(input_):
    config = list()
    for axis_config in input_:
        lexer = shlex.shlex(axis_config)
        axis = lexer.get_token()
        variant = list() 
        for value in lexer:
            variant.append((axis, value))
        config.append(variant)
    return config 

################################################################################

def parse_commandline_args(argv):

    parser = argparse.ArgumentParser(
        description='Generate jenkins matrix filter.',
        epilog='Example: python %(prog)s "foo 1 2 3" "bar 4 5 6"'
    )
    parser.add_argument('--verbose', '-v', action='count', dest='verbosity', 
            default=1)
    parser.add_argument('--version', action='version', version='%(prog)s 0.1')
    parser.add_argument('N', 
                        nargs='+', 
                        help='add matrix axis (e.g. "axis_name value_1 2 3")' )

    args = parser.parse_args(argv[1:])
    return args

################################################################################

def set_loglevel(verbosity):
    level = {4:logging.DEBUG,
             3:logging.INFO,
             2:logging.WARN,
             1:logging.ERROR,
             0:logging.CRITICAL}
    logging.basicConfig(level=level[min(4, verbosity)])

################################################################################

def groovy_filter(axes):
    filter_list = list()
    for config, active in axes:
        if active:
            f = "("
            f+= " && ".join(['%s == "%s"' % (axis, value) 
                            for axis, value in config])
            f += ")"
            filter_list.append(f)
    print " || ".join(filter_list)

################################################################################

class UI(object):

    def __init__(self, axes, callback):
        self.callback = callback
        self.axes = axes
        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.window.set_title("Jenkins Matrix Filter Generator")
        self.window.connect("destroy", gtk.mainquit)
    
        self.layout = gtk.VBox()
        self.window.add(self.layout)

        self._init_check_butttons()
        self._init_button()

        self.window.show_all()

    def _init_check_butttons(self):

        self.checkboxes = [(gtk.CheckButton(self._get_label_name(p), False), p) 
                            for p in product(*self.axes)]
        scrolled_window = gtk.ScrolledWindow()
        layout = gtk.VBox()
        scrolled_window.add_with_viewport(layout)
        for c, v in self.checkboxes:
            layout.add(c)
        self.layout.add(scrolled_window)

    def _get_label_name(self, p):
        return ", ".join(zip(*p)[1])

    def _init_button(self):
        execute_button = gtk.Button("execute")
        execute_button.set_size_request(-1, 20)
        execute_button.connect("clicked", self._execute_button)
        self.layout.add(execute_button)

    def _execute_button(self, button):
        self.callback([ (v, c.get_active()) for c, v in self.checkboxes])

################################################################################

if __name__ == "__main__":
    main(sys.argv)

################################################################################
