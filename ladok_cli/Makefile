.PHONY: all
all: ladok.pdf

LATEXFLAGS+=		-shell-escape
NOWEAVEFLAGS.tex=	-delay -t2 -latex

ladok.pdf: ladok.tex ladok.bib
ladok.pdf: abstract.tex

ladok.tex: ladok.nw

ladok.pdf: student.tex
student.tex: student.nw


.PHONY:
all: ladok

ladok.py: ladok.nw
ladok.py: student.nw
ladok: ladok.py
	ln $^ $@
	chmod +x $@


.PHONY: clean
clean:
	${RM} ladok ladok.py ladok.pdf ladok.tex
	${RM} student.tex


PKG_NAME-main= 			ladok
PKG_INSTALL_FILES-main=	ladok
PKG_PREFIX-main= 		/usr/local
PKG_INSTALL_DIR-main=	/bin
PKG_TARBALL_FILES-main= ${PKG_FILES-main} Makefile


INCLUDE_MAKEFILES=./makefiles
include ${INCLUDE_MAKEFILES}/tex.mk
include ${INCLUDE_MAKEFILES}/noweb.mk
include ${INCLUDE_MAKEFILES}/pkg.mk
