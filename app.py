#! /usr/bin/env python3
"""
    WSGI APP to convert wkhtmltopdf As a webservice
    adapted from https://github.com/openlabs/docker-wkhtmltopdf-aas
"""
import json
import tempfile
import base64

from werkzeug.wsgi import wrap_file
from werkzeug.wrappers import Request, Response
from executor import execute


@Request.application
def application(request):
    """
    To use this application, the user must send a POST request with
    base64 or form encoded encoded HTML content and the wkhtmltopdf Options in
    request data, with keys 'base64_html' and 'options'.
    The application will return a response with the PDF file.
    """
    if request.method != 'POST':
        return Response(
            response='{"error": "expected POST request"}',
            status=405,
            content_type='application/json'
        )

    if not request.content_type:
        return Response(
            response='{"error": "expected content-type header (form data or application/json"}',
            status=406,
            content_type='application/json'
        )
    request_is_json = request.content_type.endswith('json')

    with tempfile.NamedTemporaryFile(suffix='.html') as source_file:

        if request_is_json:
            # If a JSON payload is there, all data is in the payload
            data = request.data.decode('utf-8')
            payload = json.loads(data)
            decoded_payload = base64.standard_b64decode(payload['contents'])
            source_file.write(decoded_payload)
            options = payload.get('options', {})
        elif request.files:
            # First check if any files were uploaded
            source_file.write(request.files['file'].read())
            # Load any options that may have been provided in options
            options = json.loads(request.form.get('options', '{}'))
        else:
            return Response(
                response='{"error": "expected json or form request"}',
                status=406,
                content_type='application/json'
            )

        source_file.flush()

        # Evaluate argument to run with subprocess
        args = ['wkhtmltopdf', '--log-level', 'warn']

        # Add Global Options
        if options:
            for option, value in options.items():
                args.append('--{}'.format(option))
                if value:
                    args.append('"{}"'.format(value))

        # Add source file name and output file name
        file_name = source_file.name
        args += [file_name, file_name + ".pdf"]

        # Execute the command using executor
        execute(' '.join(args))

        return Response(
            wrap_file(request.environ, open(file_name + '.pdf', 'rb')),
            mimetype='application/pdf',
        )
