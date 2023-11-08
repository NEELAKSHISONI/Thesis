#import multiprocessing
import os
import sys

# The full path to the directory a Python file is contained in
curDir = os.path.dirname(os.path.realpath(__file__))
# Add the path to the current directory to sys.path
sys.path.append(curDir)
# Import a module from the newly added path
from api import FLASK_PORT


# Server Socket
bind = "0.0.0.0:%s" % FLASK_PORT


# Worker Processes
# The number of worker processes for handling requests.
# Recommended (2 x $num_cores) + 1
# http://gunicorn-docs.readthedocs.io/en/19.7.1/design.html
workers = 1#(2*multiprocessing.cpu_count())+1
# Run each worker with the specified number of threads.
threads = 1

keepalive = 75 # default: 2 seconds
timeout = 90

# The type of workers to use. The default class is sync.
worker_class = 'gevent'
# The maximum number of simultaneous clients.
# Affects the Eventlet and Gevent worker types.
#worker_connections = 30


if os.getenv('ISGAME', False) == 'True':
	try:
		from syncworkerzmq import SyncWorkerZMQ
		worker_class = 'syncworkerzmq.SyncWorkerZMQ'
	except ImportError as e:
		pass

# Security
if os.getenv('MTLS', False) == 'True':
	# SSL key file
	keyfile = 'servicekey.key'
	# SSL certificate file
	certfile = 'servicecert.pem'
	# Whether client certificate is required (see stdlib ssl module)
	cert_reqs = 1
	# CA certificates file
	ca_certs = 'cacert.pem'

# The maximum size of HTTP request line in bytes.
# Request-line consists of the HTTP method, URI, and protocol version.
# Value is a number from 0 (unlimited) to 8190.
limit_request_line = 1024
# Limit the number of HTTP headers fields in a request.
# Default = 100, cannot be larger than 32768.
limit_request_fields = 10
# Limit the allowed size of an HTTP request header field.
limit_request_field_size = 2048


# Debugging
# Restart workers when code changes.
reload = False

# Logging
#loglevel = warning


