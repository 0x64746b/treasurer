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
import os

from .Clerk import Clerk
from .Treasurer import Treasurer


# poor man's substitute for a config file
APP_NAME = 'The Treasurer'
ask_password_cmd = ['zenity', '--entry', '--hide-text',
                             '--title', APP_NAME, '--text']


def main(args):
    '''
    Main flow control
    '''
    # overhear STDERR
    keyring_channel = __capture_stderr()

    # start the business
    clerk = Clerk(APP_NAME, keyring_channel, ask_password_cmd)
    treasurer = Treasurer(clerk, args.keyring)

    if args.list:
        # --list
        hints = treasurer.get_hints()
        print 'Keyring "{}" stores the hints:'.format(args.keyring)
        for hint in hints:
            print ' * {}'.format(hint)
    else:
        # get password
        password = treasurer.get_password(args.hint)
        if password:
            print password
            password = treasurer.shred_password(password)
        else:
            clerk.close_shop('Cannot find password for "{}" in keyring'
                                   ' "{}"'.format(args.hint, args.keyring))

    # lock keyring before leaving?
    if args.lock:
        treasurer.lock_keyring()

    sys.exit(0)


def __capture_stderr():
    '''
    Captures printed to STDERR by the underlying libgnomekeyring
    '''
    ## backup old fd 2 first
    backupped_two = os.dup(2)
    sys.stderr = os.fdopen(backupped_two, 'w', 1)
    ## capture lib's stderr
    pipe_end, error_adaptor = os.pipe()
    os.dup2(error_adaptor, 2)
    return os.fdopen(pipe_end, 'r', 1)
