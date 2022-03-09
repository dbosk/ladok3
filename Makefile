SUBDIR_GOALS=	all clean distclean

SUBDIR+= 	src/ladok3
SUBDIR+=	examples
SUBDIR+=	doc
SUBDIR+=	docker

version=$(shell sed -n 's/^ *version *= *\"\([^\"]\+\)\",/\1/p' setup.py)
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

.PHONY: build
build: compile
	python3 setup.py sdist bdist_wheel

.PHONY: publish publish-ladok3 publish-docker
publish: publish-ladok3 publish-docker doc/ladok3.pdf
	git push
	gh release create -t v${version} v${version} doc/ladok3.pdf

doc/ladok3.pdf:
	${MAKE} -C $(dir $@) $(notdir $@)

publish-ladok3: ${dist}
	python3 -m twine upload -r pypi ${dist}

${dist}: build

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
