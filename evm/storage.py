import copy

import rlp

from trie import (
    Trie
)

from evm.constants import (
    BLANK_TRIE_HASH,
    EMPTY_SHA3,
)
from evm.rlp.account import (
    Account,
)
from evm.validation import (
    validate_is_bytes,
    validate_uint256,
    validate_canonical_address,
    validate_storage_slot,
)

from evm.utils.sha3 import (
    keccak,
)


class AccountStorage(object):
    db = None

    def __init__(self, db, storage_root):
        self.db = Trie(db, root_hash=storage_root)

    def __getitem__(self, key):
        return self.db[key]

    def __setitem__(self, key, value):
        self.db[key] = value

    def __delitem__(self, key):
        del self.db[key]

    def __contains__(self, key):
        return key in self.db


class Storage(object):
    db = None

    def __init__(self, db):
        self.db = db

    #
    # Public API
    #
    def set_storage(self, address, slot, value):
        validate_is_bytes(value)
        validate_storage_slot(slot)
        validate_canonical_address(address)

        storage = self._get_account_storage(address)
        encoded_value = rlp.encode(value)
        storage[slot] = encoded_value

    def get_storage(self, address, slot):
        validate_canonical_address(address)
        validate_storage_slot(slot)

        storage = self._get_account_storage(address)

        if slot in storage:
            raw_value = storage[slot]
            return rlp.decode(raw_value)
        else:
            return b''

    def delete_storage(self, address):
        validate_canonical_address(address)

        account = self._get_account(address)
        account.storage_root = BLANK_TRIE_HASH
        self.db[address] = Account.serialize(account)

    def set_balance(self, address, balance):
        validate_canonical_address(address)
        validate_uint256(balance)

        account = self._get_account(address)
        account.balance = balance

        self.db[address] = Account.serialize(account)

    def get_balance(self, address):
        validate_canonical_address(address)

        account = self._get_account(address)
        return account.balance

    def set_nonce(self, address, nonce):
        validate_canonical_address(address)
        validate_uint256(nonce)

        account = self._get_account(address)
        account.nonce = nonce

        self.db[address] = Account.serialize(account)

    def get_nonce(self, address):
        validate_canonical_address(address)

        account = self._get_account(address)
        return account.nonce

    def set_code(self, address, code):
        validate_canonical_address(address)
        validate_is_bytes(code)

        account = self._get_account(address)
        if account.code_hash != EMPTY_SHA3:
            raise ValueError("Should not be overwriting account code")

        account.code_hash = keccak(code)
        self.db[account.code_hash] = code
        self.db[address] = Account.serialize(account)

    def get_code(self, address):
        validate_canonical_address(address)
        account = self._get_account(address)
        return self.db[account.code_hash]

    def delete_code(self, address):
        validate_canonical_address(address)
        account = self._get_account(address)
        del self.db[account.code_hash]

    #
    # Account Methods
    #
    def account_exists(self, address):
        validate_canonical_address(address)
        return address in self.db

    #
    # Snapshoting and Restore
    #
    def snapshot(self):
        # TODO: can we just use the state-root?
        return copy.deepcopy(self.db)

    def revert(self, snapshot):
        self.db = snapshot

    #
    # Internal
    #
    def _get_account(self, address):
        if address in self.db:
            account = Account.deserialize(self.db[address])
        else:
            account = Account()
        return account

    def _get_account_storage(self, address):
        account = self._get_account(address)
        return AccountStorage(db=self.db, storage_root=account.storage_root)
