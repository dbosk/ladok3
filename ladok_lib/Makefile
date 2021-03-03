.PHONY: all
all: ladok3.pdf

LATEXFLAGS+=	-shell-escape

ladok3.pdf: ladok3.tex preamble.tex
ladok3.pdf: abstract.tex ../LICENSE
ladok3.pdf: example_LadokSession.py
ladok3.pdf: example_Student.py
ladok3.pdf: example_Course.py
ladok3.pdf: prgi.tex
ladok3.pdf: stats.tex

ladok3.tex: ladok3.nw


.PHONY:
all: ladok3.py

ladok3.py: ladok3.nw


.PHONY: all
all: prgi.py

prgi.py: prgi.nw


.PHONY: all
all: stats-data.py
all: stats-grade-dist.py

stats-data.py: ladok3.py
stats-data.py stats-grade-dist.py: stats.nw
	${NOTANGLE}


.PHONY: stats
stats: stats-prgi stats-dd1310

DD1315.csv: stats-data.py
	python stats-data.py DD1315 > $@

.PHONY: stats-prgi
stats-prgi: DD1315-all.pgf DD1315-grouped.pgf DD1315-last.pgf

DD1315-all.pgf DD1315-all.tex: DD1315.csv stats-grade-dist.py
	(head -n 1 DD1315.csv; grep LAB3 DD1315.csv) | \
		python stats-grade-dist.py -TnLf DD1315-all.pgf \
			-G 51386 \
			-G 50869 -G 50662 -G 50650 \
			-G 50523 -G 50917 -G 51210 -G 50094 -G 50167 -G 60420 \
				> DD1315-all.tex

DD1315-grouped.pgf DD1315-grouped.tex: DD1315.csv stats-grade-dist.py
	(head -n 1 DD1315.csv; grep LAB3 DD1315.csv) | \
		python stats-grade-dist.py -nL -f DD1315-grouped.pgf \
			-G 51386 \
			-G 50869 50662 50650 50523 \
			-G 50917 51210 50094 50167 60420 \
				> DD1315-grouped.tex

DD1315-last.pgf DD1315-last.tex: DD1315.csv stats-grade-dist.py
	(head -n 1 DD1315.csv; grep LAB3 DD1315.csv) | \
		python stats-grade-dist.py -nL -f DD1315-last.pgf \
			-G 51386 \
			-G 50869 50662 50650 50523 50917 51210 50094 50167 60420 \
				> DD1315-last.tex

ladok3.pdf: $(addsuffix .pgf,DD1315-all DD1315-grouped DD1315-last)
ladok3.pdf: $(addsuffix .tex,DD1315-all DD1315-grouped DD1315-last)

DD1310.csv: stats-data.py
	python stats-data.py DD1310 > $@

.PHONY: stats-dd1310
stats-dd1310: DD1310-all.pgf DD1310-grouped.pgf

DD1310-all.pgf DD1310-all.tex: DD1310.csv stats-grade-dist.py
	(head -n 1 DD1310.csv; grep LAB3 DD1310.csv) | \
		python stats-grade-dist.py -nL -f DD1310-all.pgf \
			-G 50156 \
			-G 50142 \
			-G 50310 \
			-G 50219 \
			-G 50429 -G 50649 -G 50519 -G 50914 -G 50018 \
				> DD1310-all.tex

DD1310-grouped.pgf DD1310-grouped.tex: DD1310.csv stats-grade-dist.py
	(head -n 1 DD1310.csv; grep LAB3 DD1310.csv) | \
		python stats-grade-dist.py -nL -f DD1310-grouped.pgf \
			-G 50156 \
			-G 50142 \
			-G 50310 \
			-G 50219 \
			-G 50429 50649 50519 50914 50018 \
				> DD1310-grouped.tex

ladok3.pdf: $(addsuffix .pgf,DD1310-all DD1310-grouped)
ladok3.pdf: $(addsuffix .tex,DD1310-all DD1310-grouped)

DD1312.csv: stats-data.py
	python stats-data.py DD1312 > $@

DD1312-all.pgf DD1312-all.tex: DD1312.csv
	(head -n 1 DD1312.csv; grep LAB3 DD1312.csv) | \
		python stats-grade-dist.py -nL -f DD1312-all.pgf \
			-G 50730 \
			-G 50864 \
			-G 50661 \
			-G 50943 \
				> DD1312-all.tex

DD1312-grouped.pgf DD1312-grouped.tex: DD1312.csv
	(head -n 1 DD1312.csv; grep LAB3 DD1312.csv) | \
		python stats-grade-dist.py -nL -f DD1312-grouped.pgf \
			-G 50730 \
			-G 50864 50661 50943 \
				> DD1312-grouped.tex

ladok3.pdf: $(addsuffix .pgf,DD1312-all DD1312-grouped)
ladok3.pdf: $(addsuffix .tex,DD1312-all DD1312-grouped)

.PHONY: clean
clean:
	${RM} ladok3 ladok3.py ladok3.pdf ladok3.tex
	${RM} prgi.pdf prgi.py prgi.tex
	${RM} stats.pdf stats.tex
	${RM} stats-data.py stats-grade-dist.py
	${RM} DD1315-*.pgf DD1315-*.tex DD1310-*.pgf DD1310-*.tex

.PHONY: distclean
	${RM} DD1315.csv DD1310.csv


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
