wsgi_app = 'app:server'

# logging
accesslog = '/var/log/gunicorn/zh_access.log'
errorlog = '/var/log/gunicorn/zh_error.log'

#daemon = True
user = None
group = None

workers = 2
backlog = 64

# TODO bind to a unix socket