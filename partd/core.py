from __future__ import absolute_import

import os
import shutil
import locket
from toolz import memoize
from contextlib import contextmanager


locks = dict()


def lock(path):
    try:
        return locks[path]
    except KeyError:
        lock = locket.lock_file(os.path.join(path, '.lock'))
        locks[path] = lock
    return lock


def escape_filename(fn):
    """ Escape text so that it is a valid filename

    >>> escape_filename('Foo!/bar')
    'Foobar'

    http://stackoverflow.com/questions/295135/turn-a-string-into-a-valid-filename-in-python
    """
    import string
    valid_chars = "-_.() %s%s" % (string.ascii_letters, string.digits)
    return ''.join(filter(valid_chars.__contains__, fn))

def filename(path, key):
    return os.path.join(path, escape_filename(str(key)))


def create(path):
    os.mkdir(path)
    lock(path)


def put(path, data, lock=lock):
    if not lock:
        lock = do_nothing
    with lock(path):
        for k, v in data.items():
            with open(filename(path, k), 'ab') as f:
                f.write(v)


def get(path, keys, lock=lock):
    assert isinstance(keys, (list, tuple, set))
    if not lock:
        lock = do_nothing
    with lock(path):
        result = []
        for key in keys:
            with open(filename(path, key), 'rb') as f:
                result.append(f.read())
    return result


def destroy(path):
    shutil.rmtree(path)


@contextmanager
def do_nothing(*args, **kwargs):
    yield
