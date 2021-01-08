.PHONY: all
all: ladok3.pdf

LATEXFLAGS+=	-shell-escape

ladok3.pdf: ladok3.tex preamble.tex
ladok3.pdf: abstract.tex ladok3_test.py

ladok3.tex: ladok3.nw


.PHONY:
all: ladok3.py

ladok3.py: ladok3.nw


.PHONY: clean
clean:
	${RM} ladok3 ladok3.py ladok3.pdf ladok3.tex


PKG_NAME-main= 			ladok3
PKG_INSTALL_FILES-main=	ladok3.py
PKG_TARBALL_FILES-main= ${PKG_INSTALL_FILES-main} Makefile

.PHONY: install
install:
	pip3 install .


INCLUDE_MAKEFILES=./makefiles
include ${INCLUDE_MAKEFILES}/tex.mk
include ${INCLUDE_MAKEFILES}/noweb.mk
include ${INCLUDE_MAKEFILES}/pkg.mk
