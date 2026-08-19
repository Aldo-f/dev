import os, json, time, fcntl

LOCK_PATH = 'queue.lock'


def acquire_lock():
    fd = os.open(LOCK_PATH, os.O_CREAT | os.O_RDWR)
    fcntl.flock(fd, fcntl.LOCK_EX)
    return fd


def release_lock(fd):
    fcntl.flock(fd, fcntl.LOCK_UN)
    os.close(fd)
