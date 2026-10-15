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
	${MAKE} -C tests clean all

.PHONY: publish publish-github publish-pypi publish-docker
publish: test publish-github publish-pypi publish-docker

publish-github: doc/ladok3.pdf check-doc-privacy
	git push
	gh release create -t v${version} v${version} doc/ladok3.pdf

doc/ladok3.pdf:
	${MAKE} -C $(dir $@) $(notdir $@)

publish-pypi: build check-doc-privacy
	poetry publish

# The manual's example outputs come from live calls to LADOK's test
# environment, which holds real people, and the wheel bundles the manual.
# Before publishing, scan the outputs and the PDF for personal data.
# The key census lists each key's number of distinct values: a key that
# pseudonymize() scrubs has one, so a new key that carries names stands out.
# scan_leaks.py comes from the testing skill; point SCAN_LEAKS elsewhere if
# it is installed somewhere else.
SCAN_LEAKS?=	${HOME}/.claude/skills/testing/scripts/scan_leaks.py
PRIVACY_ALLOW=	doc/privacy-allow.txt

.PHONY: check-doc-privacy
check-doc-privacy: doc/ladok3.pdf
	@test -f ${SCAN_LEAKS} || \
	  { echo "$@: no scanner at SCAN_LEAKS=${SCAN_LEAKS}" >&2; exit 1; }
	python3 ${SCAN_LEAKS} --key-census doc/py_*.stdout
	python3 ${SCAN_LEAKS} --allow ${PRIVACY_ALLOW} doc/py_*.stdout
	pdftotext doc/ladok3.pdf - | \
	  python3 ${SCAN_LEAKS} --allow ${PRIVACY_ALLOW} -

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
