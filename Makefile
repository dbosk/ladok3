SUBDIR_GOALS=	all clean distclean

SUBDIR+= 	src/ladok3
SUBDIR+=	examples
SUBDIR+=	doc
SUBDIR+=	docker

.PHONY: all
all:
	true

.PHONY: install
install: build
	pip3 install -e .

LADOK3+=	src/ladok3/__init__.py
LADOK3+=	src/ladok3/cli.py
LADOK3+=	src/ladok3/data.py
LADOK3+=	src/ladok3/ladok.bash

${LADOK3}:
	${MAKE} -C $(dir $@) $(notdir $@)

.PHONY: build
build: ${LADOK3}
	python3 -m build

.PHONY: publish publish-ladok3 publish-docker
publish: publish-ladok3 publish-docker

publish-ladok3: build
	python3 -m twine upload -r pypi dist/*

publish-docker:
	sleep 30
	${MAKE} -C docker publish


.PHONY: clean
clean:
	true

.PHONY: distclean
distclean:
	${RM} -R build dist ladok3.egg-info src/ladok3.egg-info


INCLUDE_MAKEFILES=./makefiles
include ${INCLUDE_MAKEFILES}/subdir.mk
