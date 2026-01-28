REM netsh interface portproxy add v4tov4  listenaddress=0.0.0.0 listenport=8102  connectaddress=172.26.32.139 connectport=8102

bash -c "source .venv/bin/activate && cd agno_backend && python app.py"