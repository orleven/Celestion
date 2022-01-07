#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @author: orleven

import os
import sys
import logging
from logging.handlers import TimedRotatingFileHandler
from lib.core.enums import CUSTOM_LOGGING
from lib.core.config import Config
from lib.utils.util import get_safe_ex_string


class Logger:
    def __init__(self, name=os.path.split(os.path.splitext(sys.argv[0])[0])[-1], level=CUSTOM_LOGGING.INFO,
                 use_console=True):

        formatter = logging.Formatter("[%(asctime)s] [%(levelname)s] %(message)s", "%H:%M:%S")
        logging.addLevelName(CUSTOM_LOGGING.INFO, "*")
        logging.addLevelName(CUSTOM_LOGGING.SUCCESS, "+")
        logging.addLevelName(CUSTOM_LOGGING.ERROR, "-")
        logging.addLevelName(CUSTOM_LOGGING.WARNING, "!")
        logging.addLevelName(CUSTOM_LOGGING.DEBUG, "DEBUG")
        logging.addLevelName(CUSTOM_LOGGING.CRITICAL, "CRITICAL")
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)

        log_name = f'{name}.log'
        log_dir = Config.LOGS_PATH
        log_path = os.path.join(log_dir, log_name)
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)

        self.log_handler = TimedRotatingFileHandler(log_path, when='D', encoding='utf-8')
        self.log_handler.setFormatter(formatter)
        self.logger.addHandler(self.log_handler)

        if use_console:
            try:
                console_handler = ColorizingStreamHandler(sys.stdout)
                console_handler.level_map[CUSTOM_LOGGING.INFO] = (None, "white", False)
                console_handler.level_map[CUSTOM_LOGGING.SUCCESS] = (None, "green", False)
                console_handler.level_map[CUSTOM_LOGGING.ERROR] = (None, "red", False)
                console_handler.level_map[CUSTOM_LOGGING.WARNING] = (None, "yellow", False)
                console_handler.level_map[CUSTOM_LOGGING.DEBUG] = (None, "cyan", False)
                console_handler.level_map[CUSTOM_LOGGING.CRITICAL] = (None, "red", False)
                self.console_handler = console_handler
            except Exception:
                self.console_handler = logging.StreamHandler(sys.stdout)
            finally:
                self.console_handler.setFormatter(formatter)
                self.logger.addHandler(self.console_handler)

    def set_level(self, level):
        self.logger.setLevel(level)

    def log(self, level, msg, *args, **kwargs):
        try:
            if isinstance(msg, str):
                for sub_msg in msg.replace('\r', '\n').split('\n'):
                    self.logger.log(level, sub_msg, *args, **kwargs)
            else:
                self.logger.log(level, msg, *args, **kwargs)
        except UnicodeEncodeError as e:
            msg = get_safe_ex_string(e)
            print(f"Error log: {msg}")

    def info(self, msg, *args, **kwargs):
        self.log(CUSTOM_LOGGING.INFO, msg, *args, **kwargs)

    def error(self, msg, *args, **kwargs):
        self.log(CUSTOM_LOGGING.ERROR, msg, *args, **kwargs)

    def success(self, msg, *args, **kwargs):
        self.log(CUSTOM_LOGGING.SUCCESS, msg, *args, **kwargs)

    def warning(self, msg, *args, **kwargs):
        self.log(CUSTOM_LOGGING.WARNING, msg, *args, **kwargs)

    def debug(self, msg, *args, **kwargs):
        self.log(CUSTOM_LOGGING.DEBUG, msg, *args, **kwargs)

    def critical(self, msg, *args, **kwargs):
        self.log(CUSTOM_LOGGING.CRITICAL, msg, *args, **kwargs)


class ColorizingStreamHandler(logging.StreamHandler):
    color_map = {
        'black': 0,
        'red': 1,
        'green': 2,
        'yellow': 3,
        'blue': 4,
        'magenta': 5,
        'cyan': 6,
        'white': 7,
    }

    level_map = {
        logging.DEBUG: (None, 'blue', False),
        logging.INFO: (None, None, False),
        logging.WARNING: (None, 'yellow', False),
        logging.ERROR: (None, 'red', False),
        logging.CRITICAL: ('red', 'white', True),
    }
    csi = '\x1b['
    reset = '\x1b[0m'

    @property
    def is_tty(self):
        isatty = getattr(self.stream, 'isatty', None)
        return isatty and isatty()

    def emit(self, record):
        try:
            message = self.format(record)
            stream = self.stream
            if not self.is_tty:
                stream.write(message)
            else:
                self.output_colorized(message)
            stream.write(getattr(self, 'terminator', '\n'))
            self.flush()
        except (KeyboardInterrupt, SystemExit):
            raise
        except:
            self.handleError(record)

    if os.name != 'nt':
        def output_colorized(self, message):
            self.stream.write(message)
    else:
        import re
        ansi_esc = re.compile(r'\x1b\[((?:\d+)(?:;(?:\d+))*)m')

        nt_color_map = {
            0: 0x00,  # black
            1: 0x04,  # red
            2: 0x02,  # green
            3: 0x06,  # yellow
            4: 0x01,  # blue
            5: 0x05,  # magenta
            6: 0x03,  # cyan
            7: 0x07,  # white
        }

        def output_colorized(self, message):
            import ctypes
            ctypes.windll.kernel32.SetConsoleTextAttribute.argtypes = [ctypes.c_ulong, ctypes.c_ushort]
            parts = self.ansi_esc.split(message)
            write = self.stream.write
            h = None
            fd = getattr(self.stream, 'fileno', None)
            if fd is not None:
                fd = fd()
                if fd in (1, 2):  # stdout or stderr
                    h = ctypes.windll.kernel32.GetStdHandle(-10 - fd)
            while parts:
                text = parts.pop(0)
                if text:
                    write(text)
                    self.stream.flush()  # For win 10
                if parts:
                    params = parts.pop(0)
                    if h is not None:
                        params = [int(p) for p in params.split(';')]
                        color = 0
                        for p in params:
                            if 40 <= p <= 47:
                                color |= self.nt_color_map[p - 40] << 4
                            elif 30 <= p <= 37:
                                color |= self.nt_color_map[p - 30]
                            elif p == 1:
                                color |= 0x08  # foreground intensity on
                            elif p == 0:  # reset to default color
                                color = 0x07
                            else:
                                pass  # error condition ignored

                        ctypes.windll.kernel32.SetConsoleTextAttribute(h, color)

    def colorize(self, message, record):
        if record.levelno in self.level_map:
            bg, fg, bold = self.level_map[record.levelno]
            params = []
            if bg in self.color_map:
                params.append(str(self.color_map[bg] + 40))
            if fg in self.color_map:
                params.append(str(self.color_map[fg] + 30))
            if bold:
                params.append('1')
            if params:
                message = ''.join((self.csi, ';'.join(params), 'm', message, self.reset))
        return message

    def format(self, record):
        message = logging.StreamHandler.format(self, record)
        if self.is_tty:
            parts = message.split('\n', 1)
            parts[0] = self.colorize(parts[0], record)
            message = '\n'.join(parts)
        return message
