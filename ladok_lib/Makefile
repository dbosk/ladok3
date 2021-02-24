.PHONY: all
all: ladok3.pdf

LATEXFLAGS+=	-shell-escape

ladok3.pdf: ladok3.tex preamble.tex
ladok3.pdf: abstract.tex ../LICENSE
ladok3.pdf: example_LadokSession.py
ladok3.pdf: example_Student.py
ladok3.pdf: example_Course.py
ladok3.pdf: prgi.tex
ladok3.pdf: stats.tex

ladok3.tex: ladok3.nw


.PHONY:
all: ladok3.py

ladok3.py: ladok3.nw


.PHONY: all
all: prgi.py

prgi.py: prgi.nw


.PHONY: all
all: stats.py

stats.py: stats.nw


.PHONY: clean
clean:
	${RM} ladok3 ladok3.py ladok3.pdf ladok3.tex
	${RM} prgi.pdf prgi.py prgi.tex
	${RM} stats.pdf stats.py stats.tex


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
