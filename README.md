# Logging Handler writing Trace Event Format

This logging writes the logs in the [Trace Event Format](https://docs.google.com/document/d/1CvAClvFfyA5R-PhYUmn5OOQtYMH4h6I0nSsKchNAySU/).

## Installation

```zsh
pip install trace-event-handler
```

## Usage

```python
import logging
from trace_event_handler import TraceEventHandler

handler = TraceEventHandler()
logging.basicConfig(
    handlers=[
        logging.StreamHandler(None),
        handler
    ]
)

# Do you stuff and log it
# ...

# Dump the trace to file
handler.dump('trace.json')
```

Open your Chromium based browser and navigate to `chrome://tracing`.
Click on `Load` and select your dumped trace file.

## Publishing manually

```zsh
python3 setup.py sdist bdist_wheel
python3 -m twine upload  dist/*
```
