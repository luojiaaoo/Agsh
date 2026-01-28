REM netsh interface portproxy add v4tov4  listenaddress=0.0.0.0 listenport=8101  connectaddress=172.26.32.139 connectport=8101

bash -c "source .venv/bin/activate && cd dash_frontend && gunicorn --capture-output -w 4 -b 0.0.0.0:8101 app:server"