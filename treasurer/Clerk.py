# coding=utf-8

#
# Copyright (C) dtk <dtk@gmx.de>
#
# Permission to use, copy, modify, and distribute this software for any
# purpose with or without fee is hereby granted, provided that the above
# copyright notice and this permission notice appear in all copies.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
# WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
# ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
# WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
# ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
# OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.
#


import sys
import re
import logging

import pynotify
import subprocess


class Clerk(object):
    '''
    An assistant than handles communication with the customer
    '''

    def __init__(self, app_name, keyring_errors, ask_password_command):

        self.app_name = app_name
        self.ask_password_command = ask_password_command

        # initialize notifications
        if not pynotify.init(app_name):
            logging.error('Could not initialize notification mechanism!')
            sys.exit(1)

        self.keyring_errors = keyring_errors


    def close_shop(self, notification):
        '''
        Notify the user and exit with an error
        '''
        notification = pynotify.Notification(self.app_name, notification)
        notification.set_urgency(pynotify.URGENCY_CRITICAL)

        if not notification.show():
            logging.error('Cannot display notification!')

        sys.exit(1)


    def ask_for_keyring_pass(self, keyring):
        '''
        Ask the customer for the password to the given keyring
        '''
        try:
            self.ask_password_command.append(
                'Please enter the password to unlock the keyring "{}"'.format(
                 keyring))
            keyring_password = bytearray(subprocess.check_output(self.ask_password_command))
            return keyring_password.strip()
        except subprocess.CalledProcessError:
            self.close_shop('No password was provided')


    def get_keyring_error(self):
        '''
        Read the error message the C lib printed to STDERR and
        do some pretty printing
        '''
        return self.keyring_errors.readline().split(':')[-1].strip()


    def is_problem(self, expected, actual):
        '''
        Check whether the actual error matches the expected one
        '''
        return re.search(expected, actual)


