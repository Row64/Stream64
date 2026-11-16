<img src="images/Stream64_White.png">

<br>

# Stream64

Stream64 is a powerful and robust API that enables live data to be sent to Row64 Server for instantaneous dashboard updates. Stream64 supports a variety of data formats and signal protocols to cover a broad range of use cases. When organizations need to process and visualize live data, the Stream API closes the gap between data retrieval and analysis.

The Stream API can stream different data types, including text, images, and emails, using various signal protocols, such as MQTT, Kafka, WebSockets, and more.

## Getting Started

Stream64 is simple to operate and conforms to the same usage patterns as the other APIs, like the DashAPI, where Python scripts are used to interact with various aspects of the Row64 platform. To work with Stream64, a Python script, which contains the `stream64()` object initialization and desired logic, is executed with Row64 Server running. The `stream64` object is provided with the URL of Row64 Server, with which it establishes a connection, and exposes functions a user can utilize to interact with the server, such as to push live updates.

The Stream API provides many example scripts that work out-of-the-box to demonstrate the capabilities of the API, as well as to offer templates users can base their custom scripts on. All the available examples are listed, with explanations, on the Help site. Reviewing these examples is the recommended way to explore the API's capabilities.

## Core Syntax

Building a minimal Stream64 Python script requires the following components:

* The `stream64` library import from `row64tools`.
* The `asyncio` library import, used for sending messages asynchronously.
* An object initialization for the `stream64` class with a valid URL for Row64 Server.
    * For example, if you're executing scripts on the same local machine that's hosting Server, such as for experimentation, Server's URL would be the local address:<br>`ws://localhost:9002?login=api`
* A call to the *connect* method for the desired protocol, such as WebSockets. For example:<br>`websockets.connect(s64.url)`
* An `async` method or loop for streaming messages.

As an example, the following code is from the `01_Pandas_CREATE` script, which is the most basic example:

```
# For sending async messages
import asyncio as asyn

# The communication protocol
import websockets as ws

# Stream API library
from row64tools.stream64 import stream64

# For the added functionality
import pandas as pd

# Pandas CREATE a new .ramdb file only

# Async function to send a single function
async def single_msg():

    # Stream64 object initialization with server URL parameter
    s64 = stream64("ws://localhost:9002?login=api")

    # Dataframe details
    df = pd.DataFrame( {"txt": ["a","b", "hello world"],"num": [1, 2, 3]} )

    # Connect over WebSockets to Server using URL
    async with ws.connect(s64.url) as w:

        # Message details
        msg = s64.msg_from_pandas(df, db="Temp", table="Pandas_Table1")

        # Send message
        await w.send(msg);await w.recv()

# Execute the async function defined above
asyn.run(single_msg())
```

This minimal script demonstrates the interaction of the core components. This specific example script creates a new dataframe (table) on the server using Pandas, so it additionally includes functionality to create a dataframe. Added functionality will vary significantly based on your design goals.
