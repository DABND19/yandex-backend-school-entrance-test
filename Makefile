PROJECT_NAME ?= market
VERSION = $(shell python3 setup.py --version | tr '+' '-')
PROJECT_NAMESPACE ?= dabnd
REGISTRY_IMAGE ?= $(PROJECT_NAMESPACE)/$(PROJECT_NAME)


clean:
	rm -fr *.egg-info dist

venv: clean
	rm -fr venv
	python3 -m venv venv
	venv/bin/pip3 install -U pip
	venv/bin/pip3 install -r requirements.txt

stop-local:
	docker-compose -f docker-compose.dev.yml down

start-local: stop-local
	docker-compose -f docker-compose.dev.yml up -d

test:
	venv/bin/pytest

sdist: clean
	python3 setup.py sdist

docker: sdist
	docker build -t $(PROJECT_NAME):$(VERSION) .

upload: docker
	docker tag $(PROJECT_NAME):$(VERSION) $(REGISTRY_IMAGE):$(VERSION)
	docker tag $(PROJECT_NAME):$(VERSION) $(REGISTRY_IMAGE):latest
	docker push $(REGISTRY_IMAGE):$(VERSION)
	docker push $(REGISTRY_IMAGE):latest
