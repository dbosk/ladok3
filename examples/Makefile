.PHONY: all
all: prgi.py

prgi.py: prgi.nw


.PHONY: all
all: statsdata.py

statsdata.py: stats.nw
	${NOTANGLE.py}

stats.tex: stats.nw


.PHONY: stats
stats: DD1315.csv DD1310.csv DD1312.csv

DD1315.csv: statsdata.py
	python statsdata.py DD1315 > $@

DD1310.csv: statsdata.py
	python statsdata.py DD1310 > $@

DD1312.csv: statsdata.py
	python statsdata.py DD1312 > $@


.PHONY: clean
clean:
	${RM} prgi.pdf prgi.py prgi.tex
	${RM} statsdata.py stats.tex
	${RM} statsdata.py

.PHONY: distclean
distclean:
	${RM} DD1315.csv DD1310.csv DD1312.csv
	${RM} -Rf __pycache__



INCLUDE_MAKEFILES=../makefiles
include ${INCLUDE_MAKEFILES}/tex.mk
include ${INCLUDE_MAKEFILES}/noweb.mk
