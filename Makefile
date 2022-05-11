NSPACE="ianwood314"
APP="human-sleep-stress-analysis"
VER="1.0"
RPORT="6438"
FPORT="5038"
UID="876585"
GID="816966"

list-targets:
	@$(MAKE) -pRrq -f $(lastword $(MAKEFILE_LIST)) : 2>/dev/null | awk -v RS= -F: '/^# File/,/^# Finished Make data base/ {if ($$1 !~ "^[#.]") {print $$1}}' | sort | egrep -v -e '^[^[:alnum:]]' -e '^$@$$'

dev: git-pull clean-api build-api run-api

deploy-prod:
	kubectl apply -f ./kubernetes/prod/app-prod-db-pvc.yml
	kubectl apply -f ./kubernetes/prod/app-prod-db-deployment.yml
	kubectl apply -f ./kubernetes/prod/app-prod-db-service.yml
	kubectl apply -f ./kubernetes/prod/app-prod-api-deployment.yml
	kubectl apply -f ./kubernetes/prod/app-prod-api-service.yml
	
delete-prod:
	kubectl delete deployments app-prod-api-deployment app-prod-db-deployment
	kubectl delete services app-prod-api-service app-prod-db-service

list:
	docker ps -a | grep ${NSPACE} || true
	docker images | grep ${NSPACE} || true

start-flask:
	export FLASK_APP=./src/flask_api.py
	export FLASK_ENV=development
	flask run -p ${FPORT}

git-pull:
	git pull

build-db:
	docker pull redis:6

build-api:
	docker build -t ${NSPACE}/${APP}-api:${VER} \
                     -f docker/Dockerfile.api \
                     ./
push:
	docker push ${NSPACE}/${APP}-api:${VER}
	docker push ${NSPACE}/${APP}-wrk:${VER}

build-wrk:
	docker build -t ${NSPACE}/${APP}-wrk:${VER} \
                     -f docker/Dockerfile.wrk \
                     ./


run-db: build-db
	docker run --name ${NSPACE}-db \
                   -p ${RPORT}:6379 \
                   -d \
                   -u ${UID}:${GID} \
                   -v ${PWD}/data/:/data \
                   redis:6 \
                   --save 1 1

run-api: build-api
	RIP=$$(docker inspect ${NSPACE}-db | grep \"IPAddress\" | head -n1 | awk -F\" '{print $$4}') && \
	docker run --name ${NSPACE}-api \
                   --env REDIS_IP=${RIP} \
                   -p ${FPORT}:5000 \
                   -d \
                   ${NSPACE}/${APP}-api:${VER} 

run-wrk: # build-wrk
	RIP=$$(docker inspect ${NSPACE}-db | grep \"IPAddress\" | head -n1 | awk -F\" '{print $$4}') && \
	docker run --name ${NSPACE}-wrk \
                   --env REDIS_IP=172.17.0.34 \
                   -d \
                   ${NSPACE}/${APP}-wrk:${VER} 


clean-db:
	docker stop ${NSPACE}-db && docker rm -f ${NSPACE}-db || true

clean-api:
	docker stop ${NSPACE}-api && docker rm -f ${NSPACE}-api || true

clean-wrk:
	docker stop ${NSPACE}-wrk && docker rm -f ${NSPACE}-wrk || true



build-all: build-db build-api build-wrk

run-all: run-db run-api run-wrk

clean-all: clean-db clean-api clean-wrk


all: clean-all build-all run-all
