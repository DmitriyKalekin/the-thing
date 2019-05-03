export ENV="Master"
export HOST="0.0.0.0"
export PORT="8443"
hypercorn --debug --reload --access-log - --keep-alive 5 --certfile /etc/ssl/eva-bot.ru/flask.pem --keyfile /etc/ssl/eva-bot.ru/certificate.key --bind 0.0.0.0:8443 main:app

