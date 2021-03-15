SUBDIR_GOALS=	all

.PHONY: all
all:
	true

.PHONY: install
install: all
	pip3 install -e .

.PHONY: build
build: all
	python3 -m build

.PHONY: publish
publish: build
	python3 -m twine upload -r testpypi dist/*


INCLUDE_MAKEFILES=./makefiles
include ${INCLUDE_MAKEFILES}/subdir.mk
