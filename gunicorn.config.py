import multiprocessing

#An example Gunicorn configuration for a WebSockets compatible server with Gevent worker, 
#you can use either this or run gunicorn as shown in the readme file

bind = '0.0.0.0:8000'
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = 'gevent' 
worker_tmp_dir = '/dev/shm'