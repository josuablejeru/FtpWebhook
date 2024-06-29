# FTP Webhook

Upload files via FTP and send them to a Webhook.

This service is particularly useful in contexts where legacy programs can only export data via FTP and cannot communicate over HTTP.

## Features

- Simple FTP server setup.
- Automatic sending of uploaded files to a specified webhook URL.
- Minimal user authentication for secure uploads.
- Configurable FTP root directory and port.

## Requirements

- Python 3.12
- Twisted

## Usage

To start the FTP server, use the following command:

```bash
python app/ftp_server.py [options]
```

Options:

```
--help           Display this help and exit.
-p, --port=      The port number to listen on [default: 21]
-r, --root=      The root directory for the FTP server [default: ./upload]
--version        Display Twisted version and exit.
-w, --webhook=   The webhook URL to send uploaded files to
```

## Example

To start the FTP server on port 2121, with the root directory as /data/uploads, and sending uploaded files to <http://example.com/webhook>, you would use:

```bash
python app/ftp_server.py -p 2121 -r /data/uploads -w http://example.com/webhook
```
