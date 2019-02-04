#!/usr/bin/env python3

"""Python 3 implementation of the 3D-DART protocol"""

import argparse
import os
import sys
from time import ctime

# Set environment
base, dirs = os.path.split(os.path.join(os.getcwd(), __file__))
split_path = base.split('/')
dart_base_path = '/'.join(split_path[0:-1])

if base not in sys.path:
    sys.path.append(base)

from dart.system.version import __version__
from dart.system.command_line_parser import CommandLineOptionParser
from dart.system.FrameWork import PluginExecutor

# Logging
import logging
logging.basicConfig(format='%(name)s [%(levelname)s] %(message)s', level=logging.INFO)
log = logging.getLogger("3D-DART")

platform = os.uname()[0]
if platform == 'Darwin':
    os.environ['X3DNA'] = '/opt/personal/X3DNA'
    os.environ['PATH'] = '{0}:/opt/personal/X3DNA/bin'.format(os.getenv("PATH"))
    #os.environ["X3DNA"] = os.path.join(dart_base_path, 'software', 'X3DNA-mac')
    #os.environ["PATH"] = "{0}:{1}/software/X3DNA-mac/bin".format(os.getenv("PATH"), dart_base_path)
elif platform == 'Linux':
    os.environ["X3DNA"] = os.path.join(dart_base_path, 'software', 'X3DNA-linux')
    os.environ["PATH"] = "{0}:{1}/software/X3DNA-linux/bin".format(os.getenv("PATH"), dart_base_path)
else:
    log.error('Platform {0} not supported'.format(platform))
    raise SystemExit

def system_checks():
    """Checks the system environment"""
    log.info("Performing System Checks:")

    """Python version check"""
    interpreter_version = float(sys.version[:3])
    if interpreter_version < 3.0:
        log.error("   * Python version 3.0 or higher required")
        log.error("   * Current version is: {}".format(sys.version[:5]))
        raise SystemExit
    else:
        log.info("   * Python version is: {}".format(sys.version[:5]))

    try:
        import numpy
        log.info("   * NumPy version is: {}".format(numpy.__version__))
    except:
        log.error("   * NumPy is required")
        raise SystemExit

    """General messages"""
    log.info("Your current working directory is: {}".format(os.getcwd()))


def exit_message():
    log.info("-"*110)
    log.info("3D-DART workflow sequence is executed succesfully")
    log.info("-"*110)
    raise SystemExit


def welcome_message():
    """Shows a welcome message"""
    print("-" * 110)
    print("Welcome to 3D-DART version {}  {}".format(__version__, ctime()))
    print("-" * 110)


if __name__ == "__main__":
    welcome_message()

    system_checks()

    options = CommandLineOptionParser(dart_path=base)

    PluginExecutor(opt_dict=options.option_dict, DARTdir=base)

    exit_message()
