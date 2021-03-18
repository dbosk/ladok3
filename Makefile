SUBDIR_GOALS=	all clean distclean

SUBDIR+= 	src/ladok3
SUBDIR+=	examples
SUBDIR+=	doc
SUBDIR+=	docker

.PHONY: all
all:
	true

.PHONY: install
install: all
	pip3 install -e .

.PHONY: build
build: all
	python3 -m build

.PHONY: publish publish-ladok3 publish-docker
publish: publish-ladok3 publish-docker

publish-ladok3: build
	python3 -m twine upload -r testpypi dist/*

publish-docker: publish-ladok3
	${MAKE} -C docker publish


.PHONY: clean
clean:

.PHONY: distclean
distclean:
	${RM} -R build dist ladok3.egg-info src/ladok3.egg-info


INCLUDE_MAKEFILES=./makefiles
include ${INCLUDE_MAKEFILES}/subdir.mk
