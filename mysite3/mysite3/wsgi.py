"""
WSGI config for mysite3 project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/2.0/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mysite3.settings")

application = get_wsgi_application()

#
# from helloworld.wsgi import HelloWorldApplication
# application = HelloWorldApplication(application)


# def application(environ, start_response):
#     status = '200 OK'
#     output = b'Hello World!'
#
#     response_headers = [('Content-type', 'text/plain'),
#                         ('Content-Length', str(len(output)))]
#     start_response(status, response_headers)
#
#     return [output]


