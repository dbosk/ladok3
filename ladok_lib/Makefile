.PHONY: all
all: ladok3.pdf

LATEXFLAGS+=	-shell-escape

ladok3.pdf: ladok3.tex preamble.tex
ladok3.pdf: abstract.tex
ladok3.pdf: example_LadokSession.py
ladok3.pdf: example_Student.py
ladok3.pdf: example_Course.py

ladok3.tex: ladok3.nw


.PHONY:
all: ladok3.py

ladok3.py: ladok3.nw


.PHONY: all
all: prgi.pdf
all: prgi.py

prgi.pdf: prgi.tex
prgi.py: prgi.nw


.PHONY: clean
clean:
	${RM} ladok3 ladok3.py ladok3.pdf ladok3.tex
	${RM} prgi.pdf prgi.py prgi.tex


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
