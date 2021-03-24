.PHONY: all
all: canvas2ladok.py

canvas2ladok.py: canvas2ladok.nw


.PHONY: stats
stats: DD1315.csv DD1310.csv DD1312.csv

DD1315.csv:
	ladok data DD1315 > $@

DD1310.csv:
	ladok data DD1310 > $@

DD1312.csv: statsdata.py
	ladok data DD1312 > $@


.PHONY: clean
clean:
	${RM} canvas2ladok.pdf canvas2ladok.py canvas2ladok.tex

.PHONY: distclean
distclean:
	${RM} DD1315.csv DD1310.csv DD1312.csv
	${RM} -Rf __pycache__



INCLUDE_MAKEFILES=../makefiles
include ${INCLUDE_MAKEFILES}/noweb.mk
