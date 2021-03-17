.PHONY: all
all: ladok3.tex api.tex

ladok3.tex: ladok3.nw
api.tex: api.nw


.PHONY:
all: __init__.py

ladok3.py: ladok3.nw api.nw

__init__.py: ladok3.py
	mv $^ $@


.PHONY: clean
clean:
	${RM} __init__.py ladok3.py
	${RM} ladok3.tex api.tex

.PHONY: distclean
distclean:
	${RM} -Rf __pycache__



INCLUDE_MAKEFILES=../../makefiles
include ${INCLUDE_MAKEFILES}/noweb.mk
