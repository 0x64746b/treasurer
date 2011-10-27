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


import random

import gnomekeyring


class KeyringErrors(object):
    '''
    Encapsulate keyring error messages enum style.
    Lend semantic meaning to generic exceptions.
    '''
    LOCKED_KEYRING = 'Cannot get secret of a locked object'
    WRONG_PASSWORD = 'The password was incorrect'


class Treasurer(object):

    def __init__(self, clerk, keyring):

        self.clerk = clerk
        self.keyring = keyring

        # check keyring daemon
        if not gnomekeyring.is_available():
            self.clerk.close_shop('Gnome Keyring Daemon is not available')

        # check keyring
        if not self.keyring in gnomekeyring.list_keyring_names_sync():
            self.clerk.close_shop('There is no keyring with name "{}"'.format(
                self.keyring))


    def get_hints(self):
        '''
        List all available password hints
        '''
        hints = []
        for secret in self.__get_each_secret():
            hints.append(secret.get_display_name())
        return hints


    def get_password(self, hint):
        '''
        Retrieve the password that belongs to the given hint
        '''
        password = None
        for secret in self.__get_each_secret():
            if secret.get_display_name() == hint:
                password = bytearray(secret.get_secret())
                break
        return password


    def shred_password(self, password):
        '''
        Invalidate the given password in memory
        '''
        for index in range(len(password)):
            # overwrite with random bytes so they cannot be easily spotted
            # in memory since they still reveal the length of the password
            password[index] = random.choice(range(256))
        return None


    def lock_keyring(self):
        try:
            gnomekeyring.lock_sync(self.keyring)
        except gnomekeyring.NoSuchKeyringError:
            self.clerk.close_shop('Could not lock keyring "{}"'.format(
                                   self.keyring))


    def __get_each_secret(self):
        try:
            for casket in gnomekeyring.list_item_ids_sync(self.keyring):
                yield gnomekeyring.item_get_info_sync(self.keyring, casket)
        except gnomekeyring.IOError:
            keyring_error = self.clerk.get_keyring_error()
            if self.clerk.is_problem(KeyringErrors.LOCKED_KEYRING, keyring_error):
                # the keyring is locked - ask for the key to unlock it
                keyring_pass = self.clerk.ask_for_keyring_pass(self.keyring)
                try:
                    gnomekeyring.unlock_sync(self.keyring, str(keyring_pass))
                    keyring_pass = self.shred_password(keyring_pass)
                    for secret in self.__get_each_secret():
                        yield secret
                except gnomekeyring.IOError:
                    keyring_error = self.clerk.get_keyring_error()
                    if self.clerk.is_problem(KeyringErrors.WRONG_PASSWORD, keyring_error):
                        self.clerk.close_shop('The password for keyring "{}"'
                                       ' was incorrect'.format(self.keyring))
                    else:
                        self.clerk.close_shop(keyring_error)
            else:
                self.clerk.close_shop(keyring_error)

