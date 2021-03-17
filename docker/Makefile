VERSION+=	latest

.PHONY: all
all: docker-image

.PHONY: publish
publish: docker-image
	for v in ${VERSION}; do docker push dbosk/ladok3:$$v; done

.PHONY: docker-image
docker-image:
	docker build -t ladok3 .
	for v in ${VERSION}; do docker tag ladok3 dbosk/ladok3:$$v; done

