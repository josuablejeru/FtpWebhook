# FTP Webhook

Upload Text files via FTP and send them to a Webhook.

This service is particularly useful in contexts where legacy programs can only export data via FTP and cannot communicate over HTTP.

> This Project is focused at csv files right now and sends them as normal string body

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

## Docker Compose

```yml
services:
  ftp-webhook:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: ftp-webhook
    cap_add:
      - NET_ADMIN
    devices:
      - /dev/net/tun
    ports:
      - "2121:2121"
      - "50000-50010:50000-50010"
    command:
      [
        "python",
        "app/ftp_server.py",
        "-p 2121",
        "-w https://example.webhook",
      ]
```
