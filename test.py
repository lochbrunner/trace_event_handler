#!/usr/bin/env python

import unittest
import logging
from trace_event_handler import TraceEventHandler


def bar():
    logging.warning('bar msg')


def foo():
    logging.warning('foo msg')
    bar()


def middle():
    foo()


def find_key_and_value(dictionary, predicate):
    for k, v in dictionary.items():
        if predicate(v):
            return k, v
    return None, None


class TestTrace(unittest.TestCase):
    def test_example(self):
        handler = TraceEventHandler(entrypoint='test_example')
        logging.basicConfig(
            handlers=[handler],
            level=logging.INFO
        )
        middle()
        handler.close()
        trace = handler.trace

        # Check stack frames
        deep_strace_names = ['__main__', 'middle', 'foo', 'bar']
        self.assertCountEqual([sf.name for sf in trace.stackFrames.values()], deep_strace_names)

        def find(name):
            return find_key_and_value(trace.stackFrames, lambda v: v.name == name)

        main_key, main_fs,  = find('__main__')
        self.assertFalse(hasattr(main_fs, 'parent'))

        middle_key, middle_fs,  = find('middle')
        self.assertEqual(middle_fs.parent, main_key)

        foo_key, foo_fs,  = find('foo')
        self.assertEqual(foo_fs.parent, middle_key)

        bar_key, bar_fs,  = find('bar')
        self.assertEqual(bar_fs.parent, foo_key)

        # Check events
        self.assertEqual([e.name for e in trace.traceEvents], ['foo msg', 'foo msg', 'bar msg', 'bar msg'])
        self.assertEqual(trace.traceEvents[0].sf, foo_key)
        self.assertEqual(trace.traceEvents[1].sf, foo_key)
        self.assertEqual(trace.traceEvents[2].sf, bar_key)
        self.assertEqual(trace.traceEvents[3].sf, bar_key)


if __name__ == '__main__':
    unittest.main()
