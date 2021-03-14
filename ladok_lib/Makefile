.PHONY: all
all: ladok3.pdf

LATEXFLAGS+=	-shell-escape
TEX_PYTHONTEX=	yes

ladok3.pdf: ladok3.tex preamble.tex
ladok3.pdf: abstract.tex ../LICENSE
ladok3.pdf: ladok3.py
ladok3.pdf: example_LadokSession.py
ladok3.pdf: example_Student.py
ladok3.pdf: example_Course.py
ladok3.pdf: ../examples/prgi.tex
ladok3.pdf: ../examples/stats.tex
ladok3.pdf: ../examples/DD1315.csv

ladok3.tex: ladok3.nw


.PHONY:
all: ladok3.py

ladok3.py: ladok3.nw


.PHONY: clean
clean:
	${RM} ladok3 ladok3.py ladok3.pdf ladok3.tex

.PHONY: distclean
distclean:
	${RM} -Rf __pycache__
	${MAKE} -C ../examples clean distclean



INCLUDE_MAKEFILES=./makefiles
include ${INCLUDE_MAKEFILES}/tex.mk
include ${INCLUDE_MAKEFILES}/noweb.mk
