# coding: utf-8

import functools
import contexter

try:
    from unittest import mock
except ImportError:
    import mock


def in_context(func):
    @functools.wraps(func)
    def new_func(self, *args, **kwargs):
        with contexter.Contexter() as ctx:
            return func(self, ctx, *args, **kwargs)
    return new_func
