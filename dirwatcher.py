#!/usr/bin/env python3
"""
Dirwatcher - A long-running program
"""

__author__ = "Timothy Reynoso, Peter Mayor and students"

import sys
import argparse
import os
import signal
import logging
import time

exit_flag = False
watch_dict = {}

logging.basicConfig(
    format='%(asctime)s.%(msecs)03d %(name)-12s %(levelname)-8s %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S', level=logging.DEBUG)
logger = logging.getLogger(__name__)


def search_for_magic(filename, start_line, magic_string, path):
    """
    """
    with open(path + '/' + filename) as f:
        found_lines = []
        for line_num, line in enumerate(f):
            if line_num < start_line:
                continue
            result = line.find(magic_string)
            watch_dict[filename] = line_num + 1
            if result != -1:
                found_lines.append(line_num + 1)
        if len(found_lines) > 0:
            logging.info(
                f"""
                New Magic-String detected at: {filename}
                Line #'s:{found_lines}""")
    return


def watch_directory(path, magic_string, extension, interval):
    """
    """
    if not os.path.isdir(path):
        logger.warning(f"Directory {path} does  not exist")
        return
    file_list = os.listdir(path)
    for k, v in watch_dict.items():
        if k not in file_list:
            logger.info(f"file deleted: {k} {v}")
            watch_dict.pop(k)
    for _file in file_list:
        if _file not in watch_dict and _file.endswith(extension):
            logger.info(f"New File Added: {_file}")
            watch_dict[_file] = 0
        search_for_magic(_file, watch_dict[_file], magic_string, path)
    return


def create_parser():
    """
    """
    parser = argparse.ArgumentParser(description='some dirwatcher stuff')
    parser.add_argument('-d', '--dir', help="dir to watch")
    parser.add_argument('-i', '--int', default=1, type=int, help='''
    controls the polling interval''')
    parser.add_argument('-e', '--ext', default='.txt', help='''
    filters what kind of file extension to search within''')
    parser.add_argument('text', help='magic text string to look at')

    args = parser.parse_args()
    return args


def signal_handler(sig_num, frame):
    """
    This is a handler for SIGTERM and SIGINT.
    Other signals can be mapped here as well (SIGHUP?)
    Basically, it just sets a global flag, and main()
    will exit its loop if the signal is trapped.
    :param sig_num: The integer signal number that
    was trapped from the OS.
    :param frame: Not used
    :return None
    """

    if signal.Signals(sig_num).name == 'SIGINT':
        logger.warning('Received ' + signal.Signals(sig_num).name)
    global exit_flag
    exit_flag = True
    if signal.Signals(sig_num).name == 'SIGTERM':
        logger.warning('Received ' + signal.Signals(sig_num).name)
    # log the associated signal name
    logger.info("""
    ____________________________________________\n
    Exiting the Program
    ____________________________________________\n""")
    return


def main(args):
    """
    """
    args = create_parser()
    # Hook into these two signals from the OS
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    # Now my signal_handler will get called if OS sends
    # either of these to my process.
    logger.info(f"""
    ____________________________________________\n
    Starting the to watch the directory {args.dir} for text of <{args.text}>
    ____________________________________________\n""")
    while not exit_flag:
        try:
            watch_directory(args.dir, args.text, args.ext, args.int)
            # print(watch_dict)
            # call my directory watching function
            pass
        except Exception as e:
            print(e)
            # This is an UNHANDLED exception
            # Log an ERROR level message here
            pass

        # put a sleep inside my while loop so I don't peg the cpu usage at 100%
        time.sleep(args.int)

    # final exit point happens here
    # Log a message that we are shutting down
    # Include the overall uptime since program start
    return


if __name__ == '__main__':
    main(sys.argv[1:])
