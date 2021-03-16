.PHONY: all
all: ladok3.pdf

LATEXFLAGS+=	-shell-escape
TEX_PYTHONTEX=	yes

ladok3.pdf: ladok3.tex preamble.tex
ladok3.pdf: abstract.tex ../../LICENSE
ladok3.pdf: __init__.py
ladok3.pdf: ../../examples/example_LadokSession.py
ladok3.pdf: ../../examples/example_Student.py
ladok3.pdf: ../../examples/example_Course.py
ladok3.pdf: ../../examples/prgi.tex
ladok3.pdf: ../../examples/stats.tex
ladok3.pdf: DD1315.csv

ladok3.tex: ladok3.nw

../%:
	${MAKE} -C $(dir $@) $(notdir $@)


.PHONY:
all: __init__.py

ladok3.py: ladok3.nw

__init__.py: ladok3.py
	mv $^ $@

DD1315.csv: ../../examples/DD1315.csv
	ln -sf $^ $@

.PHONY: clean
clean:
	${RM} __init__.py ladok3.py ladok3.pdf ladok3.tex

.PHONY: distclean
distclean:
	${RM} -Rf __pycache__
	${MAKE} -C ../../examples clean distclean



INCLUDE_MAKEFILES=../../makefiles
include ${INCLUDE_MAKEFILES}/tex.mk
include ${INCLUDE_MAKEFILES}/noweb.mk
