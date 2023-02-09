.PHONY: all
all: ladok3.pdf

LATEXFLAGS+=	-shell-escape
TEX_PYTHONTEX=	yes
PYTHONTEXFLAGS=	--interpreter "python:poetry run python3"

ladok3.pdf: ../src/ladok3

../src/ladok3::
	${MAKE} -C $@ all

ladok3.pdf: ../src/ladok3/ladok3.tex
ladok3.pdf: ../src/ladok3/api.tex
ladok3.pdf: ../src/ladok3/undoc.tex

ladok3.pdf: ../src/ladok3/cli.tex
ladok3.pdf: ../src/ladok3/data.tex
ladok3.pdf: ../src/ladok3/report.tex
ladok3.pdf: ../src/ladok3/student.tex

ladok3.pdf: preamble.tex abstract.tex ../LICENSE
ladok3.pdf: ../examples/example_LadokSession.py
ladok3.pdf: ../examples/example_Student.py
ladok3.pdf: ../examples/example_Course.py
ladok3.pdf: ../examples/canvas2ladok.tex

../%::
	${MAKE} -C $(dir $@) $(notdir $@)


.PHONY: clean
clean:
	${RM} ladok3.pdf
	${RM} DD1315.csv

.PHONY: distclean
distclean:
	${RM} -Rf __pycache__
	${MAKE} -C ../examples clean distclean
	${MAKE} -C ../src/ladok3 clean distclean



INCLUDE_MAKEFILES=../makefiles
include ${INCLUDE_MAKEFILES}/tex.mk
