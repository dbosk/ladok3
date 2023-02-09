LIB=	ladok3.nw api.nw undoc.nw
CLI=	cli.nw data.nw report.nw student.nw

.PHONY: all
all: ${LIB:.nw=.tex} __init__.py
all: ${CLI:.nw=.tex} ${CLI:.nw=.py} ladok.bash

__init__.py: ladok3.py
	mv $^ $@

ladok3.py: ${LIB}

ladok.bash: __init__.py ${CLI:.nw=.py}
	register-python-argcomplete ladok > $@


.PHONY: clean
clean:
	${RM} __init__.py ladok3.py
	${RM} ${LIB:.nw=.tex}
	${RM} ${CLI:.nw=.tex}
	${RM} ${CLI:.nw=.py} ladok.bash

.PHONY: distclean
distclean:
	${RM} -Rf __pycache__



INCLUDE_MAKEFILES=../../makefiles
include ${INCLUDE_MAKEFILES}/noweb.mk
