SUBDIR_GOALS=	all clean distclean

SUBDIR+= 	src/ladok3
SUBDIR+=	examples
SUBDIR+=	doc
SUBDIR+=	docker

version=$(shell sed -n 's/^ *version *= *"\([^"]\+\)"/\1/p' pyproject.toml)
dist=$(addprefix dist/ladok3-${version}, -py3-none-any.whl .tar.gz)


.PHONY: all
all:
	true

.PHONY: install
install:
	pip3 install -e .

.PHONY: compile
compile:
	${MAKE} -C src/ladok3 all

requirements.txt:
	poetry export -f requirements.txt --output $@

.PHONY: build
build: compile
	poetry build

.PHONY: test
test: compile
	${MAKE} -C tests clean all test

.PHONY: publish publish-github publish-pypi publish-docker
publish: test publish-github publish-pypi publish-docker

publish-github: doc/ladok3.pdf
	git push
	gh release create -t v${version} v${version} doc/ladok3.pdf

doc/ladok3.pdf:
	${MAKE} -C $(dir $@) $(notdir $@)

publish-pypi: build
	poetry publish

publish-docker:
	sleep 60
	${MAKE} -C docker publish


.PHONY: clean
clean:
	true

.PHONY: distclean
distclean:
	${RM} -R build dist ladok3.egg-info src/ladok3.egg-info


INCLUDE_MAKEFILES=./makefiles
include ${INCLUDE_MAKEFILES}/subdir.mk
