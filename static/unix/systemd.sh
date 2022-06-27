[Unit]
Description=Flask Web Application Server using Gunicorn
After=network.target

[Service]
User=kai
Group=kai
WorkingDirectory=/home/kai/git/NNF
Environment="PATH=/home/kai/git/NNF/menv/bin"
# ExecStart=sudo /bin/bash -c 'source /home/kai/git/NNF/menv/bin/activate; gunicorn -w 1 -k gthread --thread=8 --bind 0.0.0.0:8000 app:app --preload --error-logfile /home/kai/git/NNF/log.log --capture-output --log-level debug;'
ExecStart=sudo /bin/bash -c 'source /home/kai/git/NNF/menv/bin/activate; gunicorn -w 1 -k gthread --thread=8 --bind unix:/tmp/my-server/ipc.sock app:app --preload --error-logfile /home/kai/git/NNF/log.log --capture-output --log-level debug;'

Restart=always

[Install]
WantedBy=multi-user.target