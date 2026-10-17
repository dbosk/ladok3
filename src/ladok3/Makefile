# notangle exits with status 2 when a chunk is used but never defined, and
# tangles the use as nothing.  The shared noweb.mk pipes notangle into cpif,
# so without pipefail the pipeline reports cpif's status and the build goes
# on with code silently missing (issue #145).  pipefail makes the undefined
# chunk fail the build; .DELETE_ON_ERROR removes the incomplete output, so
# the next make tangles again and fails again instead of using it.
SHELL=		/bin/bash
.SHELLFLAGS=	-o pipefail -c
.DELETE_ON_ERROR:

LIB=	ladok3.nw api.nw undoc.nw
CLI=	cli.nw data.nw report.nw student.nw
SCRIPTS=$(shell noroots scripts.nw | sed -E "s/(<<|>>|\[\[|\]\])//g")

.PHONY: all
all: ${LIB:.nw=.tex} __init__.py
all: ${CLI:.nw=.tex} ${CLI:.nw=.py} ladok.bash
all: scripts.tex ${SCRIPTS}
all: testing.tex

__init__.py: ladok3.py
	mv $^ $@

ladok3.py: ${LIB}

ladok.bash: __init__.py ${CLI:.nw=.py}
	register-python-argcomplete ladok > $@

${SCRIPTS}: scripts.nw
	${NOTANGLE.sh}


.PHONY: clean
clean:
	${RM} __init__.py ladok3.py
	${RM} ${LIB:.nw=.tex}
	${RM} ${CLI:.nw=.tex}
	${RM} ${CLI:.nw=.py} ladok.bash
	${RM} scripts.tex ${SCRIPTS}
	${RM} testing.tex

.PHONY: distclean
distclean:
	${RM} -Rf __pycache__



INCLUDE_MAKEFILES=../../makefiles
include ${INCLUDE_MAKEFILES}/noweb.mk
