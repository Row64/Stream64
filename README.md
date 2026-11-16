# Stream64

Stream64 is a powerful and robust API that enables live data to be sent to Row64 Server for instantaneous dashboard updates. Stream64 supports a variety of data formats and signal protocols to cover a broad range of use cases. When organizations need to process and visualize live data, the Stream API closes the gap between data retrieval and analysis.

The Stream API can stream different data types, including text, images, and emails, using various signal protocols, such as MQTT, Kafka, WebSockets, and more.

## Getting Started

Stream64 is simple to operate and conforms to the same usage patterns as the other APIs, like the DashAPI, where Python scripts are used to interact with various aspects of the Row64 platform. To work with Stream64, a Python script, which contains the `stream64()` object initialization and desired logic, is executed with Row64 Server running. The `stream64` object is provided with the URL of Row64 Server, with which it establishes a connection, and exposes functions a user can utilize to interact with the server, such as to push live updates.

The Stream API provides many example scripts that work out-of-the-box to demonstrate the capabilities of the API, as well as to offer templates users can base their custom scripts on. All the available examples are listed, with explanations, on the Help site. Reviewing these examples is the recommended way to explore the API's capabilities.
