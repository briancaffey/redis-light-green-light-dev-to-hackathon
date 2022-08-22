# for local development

dcud:
	docker compose -f docker-compose.dev.yml up

dcdd:
	docker compose -f docker-compose.dev.yml down

dcug:
	docker compose -f docker-compose.gunicorn.yml up

dcdg:
	docker compose -f docker-compose.gunicorn.yml down

# for terraform

tf-init:
	terraform -chdir=terraform init

tf-plan:
	terraform -chdir=terraform plan

tf-apply:
	terraform -chdir=terraform apply

tf-fmt:
	terraform fmt -recursive

tf-destroy:
	terraform -chdir=terraform destroy

cloc:
	cloc \
		--exclude-dir=$$(tr '\n' ',' < .clocignore) \
		--exclude-ext=json \
		.