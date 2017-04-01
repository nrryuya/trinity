import rlp
from rlp.sedes import (
    big_endian_int,
)

from evm.constants import (
    EMPTY_SHA3,
    BLANK_TRIE_HASH,
)

from .sedes import (
    trie_root,
    hash32,
)


class Account(rlp.Serializable):
    """
    RLP object for accounts.
    """

    fields = [
        ('nonce', big_endian_int),
        ('balance', big_endian_int),
        ('storage_root', trie_root),
        ('code_hash', hash32)
    ]

    def __init__(self, nonce=0, balance=0, storage_root=BLANK_TRIE_HASH, code_hash=EMPTY_SHA3):
        super(self, Account).__init__(nonce, balance, storage_root, code_hash)
