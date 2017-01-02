# Copyright 2011 Ian Goldberg
# Copyright 2016-2017 David Stainton
#
# This file is part of Sphinx.
#
# Sphinx is free software: you can redistribute it and/or modify
# it under the terms of version 3 of the GNU Lesser General Public
# License as published by the Free Software Foundation.
#
# Sphinx is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with Sphinx.  If not, see
# <http://www.gnu.org/licenses/>.

from sphinxmixcrypto.node import UnwrappedMessage
from sphinxmixcrypto.padding import add_padding
from sphinxmixcrypto.crypto_primitives import SphinxLioness, SphinxDigest, PAYLOAD_SIZE, SECURITY_PARAMETER


class SphinxNoSURBSAvailableError(Exception):
    pass


class NymResult:
    def __init__(self):
        self.message_result = None


class Nymserver:
    def __init__(self):
        self.database = {}
        self.digest = SphinxDigest()
        self.block_cipher = SphinxLioness()

    def add_surb(self, nym, nymtuple):
        db = self.database
        if nym in db:
            db[nym].append(nymtuple)
        else:
            db[nym] = [nymtuple]

    def process(self, nym, message):
        result = NymResult()
        db = self.database
        if nym in db and len(db[nym]) > 0:
            n0, header0, ktilde = db[nym].pop(0)
            key = self.block_cipher.create_block_cipher_key(ktilde)
            block = add_padding((b"\x00" * SECURITY_PARAMETER) + message, PAYLOAD_SIZE)
            body = self.block_cipher.encrypt(key, block)
            unwrapped_message = UnwrappedMessage()
            unwrapped_message.tuple_next_hop = (n0, header0, body)
            result.message_result = unwrapped_message
        else:
            raise SphinxNoSURBSAvailableError
        return result
