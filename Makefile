# for local development if not using docker-compose to star the backend services

check:
	@docker -v; echo
	@docker-compose -v; echo
	@python3 --version; echo
	@echo Node `node -v`; echo

redis-stack-up:
	@docker-compose -f redis-stack.yml up

install_dev:
	@rm -rf app/.env
	@python3 -m venv app/.env
	@. app/.env/bin/activate
	@python3 -m pip install --upgrade pip
	@pip install -r app/requirements.txt
	@pip install -r app/requirements_dev.txt

clean:
	@rm -rf .env

flask:
	@. app/.env/bin/activate
	@cd app && gunicorn -k geventwebsocket.gunicorn.workers.GeventWebSocketWorker -w 1 wsgi:app --reload

celery:
	@. app/.env/bin/activate
	@cd app && celery --app app.celery worker --loglevel=info

celerybeat:
	@. app/.env/bin/activate
	@cd app && celery --app app.celery beat --loglevel=info

nuxt:
	@cd client && npm i && npm run dev

flushall:
	@docker exec -it redis redis-cli flushall

cloc:
	cloc \
		--exclude-dir=$$(tr '\n' ',' < .clocignore) \
		--exclude-ext=json \
		.
