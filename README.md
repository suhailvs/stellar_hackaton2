## Stellar Agent

https://dorahacks.io/hackathon/stellar-agents-x402-stripe-mpp/detail

1. Basic Architecture
    1. when user enter a prompt
    2. create invoice and  show QR code
    3. watch payment
    4. if payment success show the replay
2. Important: Use MEMO to Identify the User
    1. Memo = User ID / Order ID
3. Extra Security Checks. Always verify:
    1. ✔ correct amount
    2. ✔ correct memo
    3. ✔ correct asset (XLM)
    4. ✔ payment not processed before

### start watcher

```
$ sudo apt install redis-server
$ celery -A mysite worker -l INFO
```
visit http://localhost:8000/stream_payments/ to start the celery task

#### server setup

sudo apt install supervisor
```
/etc/apache2/sites-available/stellar.conf
<VirtualHost *:80>
	ServerName stellar.stackschools.com	
	WSGIDaemonProcess stellarapp python-home=/var/www/stellar_hackaton2/env python-path=/var/www/stellar_hackaton2/
	WSGIProcessGroup stellarapp
	WSGIScriptAlias / /var/www/stellar_hackaton2/mysite/wsgi.py
	ErrorLog /var/www/stellar_hackaton2/error.log
</VirtualHost>

/etc/supervisor/conf.d/celery.conf
[program:celery_worker]
command=/var/www/stellar_hackaton2/env/bin/celery -A mysite worker -l info
directory=/var/www/stellar_hackaton2
user=www-data
numprocs=1
stdout_logfile=/var/log/celery_worker.log
stderr_logfile=/var/log/celery_worker_error.log
autostart=true
autorestart=true
```

sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start all

#### after certbot run

/etc/apache2/sites-available/stellar.conf becomes:
```
<VirtualHost *:80>
	ServerName stellar.stackschools.com	
RewriteEngine on
RewriteCond %{SERVER_NAME} =stellar.stackschools.com
RewriteRule ^ https://%{SERVER_NAME}%{REQUEST_URI} [END,NE,R=permanent]
</VirtualHost>
```