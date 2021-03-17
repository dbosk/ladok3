.PHONY: all
all: ladok3.tex api.tex cli.tex data.tex


.PHONY:
all: __init__.py cli.py data.py
all: ladok.bash

ladok3.py: ladok3.nw api.nw

__init__.py: ladok3.py
	mv $^ $@

ladok.bash: __init__.py cli.py data.py
	register-python-argcomplete ladok > $@


.PHONY: clean
clean:
	${RM} __init__.py ladok3.py
	${RM} ladok3.tex api.tex
	${RM} cli.py data.py ladok.bash
	${RM} cli.tex data.tex

.PHONY: distclean
distclean:
	${RM} -Rf __pycache__



INCLUDE_MAKEFILES=../../makefiles
include ${INCLUDE_MAKEFILES}/noweb.mk
