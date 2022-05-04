wsgi_app = 'app:server'

# logging
accesslog = 'log/access.log'
errorlog = 'log/error.log'

#daemon = True
user = None
group = None

workers = 2
backlog = 64
