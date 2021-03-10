.PHONY: all
all: ladok3.pdf

LATEXFLAGS+=	-shell-escape
TEX_PYTHONTEX=	yes

ladok3.pdf: ladok3.tex preamble.tex
ladok3.pdf: abstract.tex ../LICENSE
ladok3.pdf: example_LadokSession.py
ladok3.pdf: example_Student.py
ladok3.pdf: example_Course.py
ladok3.pdf: prgi.tex
ladok3.pdf: stats.tex stats-data.tex
ladok3.pdf: ladok3.py

ladok3.tex: ladok3.nw


.PHONY:
all: ladok3.py

ladok3.py: ladok3.nw


.PHONY: all
all: prgi.py

prgi.py: prgi.nw


.PHONY: all
all: stats-data.py

stats-data.py: stats-data.nw ladok3.py


.PHONY: stats
stats: DD1315.csv DD1310.csv DD1312.csv

DD1315.csv: stats-data.py
	python stats-data.py DD1315 > $@

DD1310.csv: stats-data.py
	python stats-data.py DD1310 > $@

DD1312.csv: stats-data.py
	python stats-data.py DD1312 > $@

.PHONY: clean
clean:
	${RM} ladok3 ladok3.py ladok3.pdf ladok3.tex
	${RM} prgi.pdf prgi.py prgi.tex
	${RM} stats-data.py

.PHONY: distclean
	${RM} DD1315.csv DD1310.csv DD1312.csv


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
