![PyPI - Python Version](https://img.shields.io/pypi/pyversions/trace_event_handler)
[![PyPI](https://img.shields.io/pypi/v/trace_event_handler)](https://pypi.org/project/trace-event-handler/)
![PyPI - License](https://img.shields.io/pypi/l/trace_event_handler)
[![PyPI - Downloads](https://img.shields.io/pypi/dm/trace_event_handler)](https://pypi.org/project/trace-event-handler/)
![Python package](https://github.com/lochbrunner/trace_event_handler/workflows/Python%20package/badge.svg)

# Logging Handler writing Trace Event Format


This logging writes the logs in the [Trace Event Format](https://docs.google.com/document/d/1CvAClvFfyA5R-PhYUmn5OOQtYMH4h6I0nSsKchNAySU/).

![Screenshot](https://github.com/lochbrunner/trace_event_handler/blob/master/assets/screenshot.png)

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

# Do your stuff and log it
# ...

# Dump the trace to file
handler.dump('trace.json')
```

Open your Chromium based browser and navigate to `chrome://tracing`.
Click on `Load` and select your dumped trace file.

The [example](https://github.com/lochbrunner/trace_event_handler/blob/master/example.py) leads to the trace seen in the figure above.

## Publishing manually

```zsh
python3 setup.py sdist bdist_wheel
python3 -m twine upload  dist/*
```
