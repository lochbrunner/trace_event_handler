import json
import logging
import os
import sys
import threading
import time
import traceback


class TrivialEncoder(json.JSONEncoder):
    def default(self, o):
        return o.__dict__


class Event:
    def __init__(self, ts, name, ph='B'):
        self.pid = os.getpid()
        self.tid = threading.current_thread().ident
        self.ts = ts
        self.cat = ''
        self.ph = ph
        self.name = name
        self.args = {}

    def end(self, ts):
        return Event(
            name=self.name,
            ts=ts,
            ph='E'
        )


class Trace:
    def __init__(self):
        self.traceEvents = []
        self.meta_user = "",
        self.meta_cpu_count = "1"
        self.stackFrames = {}
        self.samples = []


class TraceEventHandler(logging.Handler):
    def __init__(self):
        super(TraceEventHandler, self).__init__()
        self.trace = Trace()
        self.start_ts = time.time()
        self.event_stack = []

    def emit(self, record):
        # Get stack information
        def create_id(code):
            return f'{code.co_filename}:{code.co_firstlineno}'
        traces = [trace[0]
                  for trace in traceback.walk_stack(sys._getframe().f_back)]
        stack_names = [trace.f_code.co_name
                       for trace in traces]
        module_index = stack_names.index('<module>')
        traces = traces[5:module_index]
        stack_ids = [create_id(trace.f_code) for trace in traces]
        ts = int((record.created - self.start_ts)*1e6)

        def frame_ended(stack):
            if len(stack) >= len(stack_ids):
                return True
            for (prev, curr) in zip(stack, stack_ids[::-1]):
                if prev != curr:
                    return True
            return False

        def remove_outdated_frame(frame):
            stack, frame = frame
            if frame_ended(stack):
                end = frame.end(ts=ts)
                self.trace.traceEvents.append(end)
                return False
            else:
                return True

        self.event_stack = [
            frame for frame in self.event_stack if remove_outdated_frame(frame)]

        event = Event(ts=ts, name=record.message)
        self.trace.traceEvents.append(event)
        self.event_stack.append((stack_ids, event))

    def dump(self, filename='trace.json'):
        ts = int((time.time() - self.start_ts)*1e6)
        for frame in self.event_stack:
            end = frame[1].end(ts=ts)
            self.trace.traceEvents.append(end)

        with open(filename, 'w') as f:
            json.dump(self.trace, f, cls=TrivialEncoder,
                      indent=2, sort_keys=True)
