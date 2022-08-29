# docker-compose

# start the backend services (flask, celery, celerybeat, redis-stack)
docker-compose:
	@docker-compose up --build

# start the client
nuxt:
	@cd client && npm i && npm run dev

# for local development if not using docker-compose to stat the backend services

# check versions of locally installed tools
check:
	@docker -v; echo
	@docker-compose -v; echo
	@python3 --version; echo
	@echo Node `node -v`; echo

# stand up only redis stack
redis-stack-up:
	@docker-compose -f redis-stack.yml up

# install dependencies in a python virtual environment
install_dev:
	@rm -rf app/.env
	@python3 -m venv app/.env
	@. app/.env/bin/activate
	@python3 -m pip install --upgrade pip
	@pip install -r app/requirements.txt
	@pip install -r app/requirements_dev.txt

# delete the python virtual environment
clean:
	@rm -rf .env

# start the flask app (api and websockets)
flask:
	@. app/.env/bin/activate
	@cd app && gunicorn -k geventwebsocket.gunicorn.workers.GeventWebSocketWorker -w 1 wsgi:app --reload

# start the celery worker
celery:
	@. app/.env/bin/activate
	@cd app && celery --app app.celery worker --loglevel=info

# start the celerybeat process
celerybeat:
	@. app/.env/bin/activate
	@cd app && celery --app app.celery beat --loglevel=info

# delete all keys from all redis databases
flushall:
	@docker exec -it redis redis-cli flushall

# count lines of code
cloc:
	cloc \
		--exclude-dir=$$(tr '\n' ',' < .clocignore) \
		--exclude-ext=json \
		.
