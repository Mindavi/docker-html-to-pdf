# wkhtmltopdf service

wkhtmltopdf in a docker container as a web service.
Adapted from https://github.com/openlabs/docker-wkhtmltopdf-aas

## Running with docker-compose

Bring up the service, exposing port 2000 to communicate with the service.

```sh
docker-compose up
```

## Building

```sh
docker build --tag mindavi/html-to-pdf .
```

## Running the service

Run the container with docker run and binding the ports to the host.
The web service is exposed on port 80 in the container, on port 2000 on the host.

```sh
docker run --detach --publish 2000:80 mindavi/html-to-pdf
```

The container now runs as a daemon on port 2000 on the host.

## Using the webservice

### Uploading a HTML file

This is a convenient way to use the service from command line
utilities like curl.

```sh
curl -vv -F 'file=@path/to/local/file.html' http://<docker-host>:<port>/ -o path/to/output/file.pdf
```

To send options to you can encode them as json and send them too.

```sh
curl -vv -F 'file=@path/to/local/file.html' -F 'options={"orientation":"Landscape", "print-media-type": null"}' http://<docker-host>:<port>/ -o path/to/output/file.pdf
```

### JSON API

If you are planning on using this service in your application,
it might be more convenient to use the JSON API that the service
uses.

Here is an example in python, we pass options to wkhtmltopdf.
When passing our settings we omit the double dash "--" at the start of the option.
For documentation on what options are available, visit http://wkhtmltopdf.org/usage/wkhtmltopdf.txt

```python
#!/usr/bin/env python3

import json
import requests
import base64

url = 'http://<docker_host>:<port>/'
file_name = '/file/to/convert.html'
data = open(file_name).read().encode('utf-8')
encoded_file = str(base64.standard_b64encode(data), 'utf-8')
data = {
    'contents': encoded_file,
    'options': {
        #Omitting the "--" at the start of the option
        'footer-center': '[page]/[topage]',
        'orientation': 'Portrait',
        'print-media-type': None,
        'viewport-size': '850x850',
    }
}
headers = {
    'Content-Type': 'application/json',    # This is important
}
response = requests.post(url, data=json.dumps(data), headers=headers)

# Save the response contents to a file
with open('/path/to/local/file.pdf', 'wb') as f:
    f.write(response.content)
```

where:

* docker-host is the hostname or address of the docker host running the container
* port is the public port to which the container is bound to (2000 in this example).

