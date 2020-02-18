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
    def __init__(self, ts, name, sf=None, ph='B'):
        self.pid = os.getpid()
        self.tid = threading.current_thread().ident
        self.ts = ts
        self.cat = ''
        self.ph = ph
        if len(name) <= 30:
            self.name = name
        else:
            self.name = name[:27] + '...'
        if sf is not None:
            self.sf = sf
        self.args = {}

    def end(self, ts):
        return Event(
            name=self.name,
            ts=ts,
            ph='E',
            sf=self.sf
        )


class StackFrame:
    def __init__(self, name, parent=None):
        self.name = name
        self.category = ''
        if parent is not None:
            self.parent = parent


class Trace:
    def __init__(self):
        self.traceEvents = []
        self.stackFrames = {}
        self.meta_user = '',
        self.meta_cpu_count = '1'
        self.stackFrames = {}
        self.samples = []


class TraceEventHandler(logging.Handler):
    def __init__(self, use_duration_events=True, max_events=None, entrypoint='<module>'):
        super(TraceEventHandler, self).__init__()
        self.trace = Trace()
        self.start_ts = time.time()
        self.event_stack = []
        self.use_duration_events = use_duration_events
        self.max_events = max_events
        self.stackFrameMapping = {}  # file:ln -> id
        self.entrypoint = entrypoint

    def emit(self, record):
        if self.use_duration_events:
            self._emit_duration_events(record)
        else:
            self._emit_instant_event(record)

    def _emit_instant_event(self, record):
        ts = int((record.created - self.start_ts)*1e6)
        event = Event(ts=ts, name=record.message, ph='I')
        self.trace.traceEvents.append(event)

    def create_id(self, code):
        return f'{code.co_filename}:{code.co_firstlineno}'

    def get_frame_id(self, traces, begin, module_index):
        trace_name = traces[begin].f_code.co_name.replace(self.entrypoint, '__main__')
        trace_id = self.create_id(traces[begin].f_code)
        if trace_id not in self.stackFrameMapping:
            # Parent id
            if module_index == begin:
                sf_parent_id = None
            else:
                sf_parent_id = self.get_frame_id(traces, begin+1, module_index)
            sf_id = str(len(self.trace.stackFrames))
            self.stackFrameMapping[trace_id] = sf_id
            self.trace.stackFrames[sf_id] = StackFrame(trace_name, parent=sf_parent_id)
        else:
            sf_id = self.stackFrameMapping[trace_id]
        return sf_id

    def find_user_code(self, traces, begin_index):
        for i, trace in enumerate(traces[begin_index:]):
            if 'logging/__init__.py' not in trace.f_code.co_filename:
                return begin_index + i
        return -1

    def _emit_duration_events(self, record):
        # Get stack information
        traces = [trace[0]
                  for trace in traceback.walk_stack(sys._getframe().f_back)]
        stack_names = [trace.f_code.co_name
                       for trace in traces]
        log_index = self.find_user_code(traces, stack_names.index('_log'))

        # Get stack frame id
        module_index = stack_names.index(self.entrypoint)
        sf_id = self.get_frame_id(traces, log_index, module_index)

        traces = traces[log_index:module_index]
        # We use <filename>:<line number> as stack ids instead of the standard ids
        # because they are not the same for the same stack frame.
        stack_ids = [self.create_id(trace.f_code) for trace in traces]
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

        msg = getattr(record, 'msg', getattr(record, 'message', 'Unknown message'))
        event = Event(ts=ts, name=msg, sf=sf_id)
        self.trace.traceEvents.append(event)
        if self.max_events is None or len(self.event_stack) + len(self.trace.traceEvents) < self.max_events:
            self.event_stack.append((stack_ids, event))

    def close(self):
        ts = int((time.time() - self.start_ts)*1e6)
        for frame in self.event_stack:
            end = frame[1].end(ts=ts)
            self.trace.traceEvents.append(end)

    def dump(self, filename='trace.json'):
        self.close()

        with open(filename, 'w') as f:
            json.dump(self.trace, f, cls=TrivialEncoder,
                      indent=2, sort_keys=True)
