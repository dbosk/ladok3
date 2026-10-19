# The $(eval $(call def_target, ...)) loop below registers the per-file
# tangling rules at parse time, which makes the first generated rule
# (test_api.py) the default goal unless we pin it explicitly.
.DEFAULT_GOAL := all

define find_tests
find ../src -type f | xargs grep "<<test \[\[[^.]*\.py\]\]>>" | \
	sed -En "s/^(.*):.*<<test \[\[([^.]*)\.py\]\]>>.*/test_\2.py:\1/p" | sort -u
endef

define def_target
$(shell echo $1 | cut -d: -f1): $(shell echo $1 | cut -d: -f2)
	notangle ${NOTANGLEFLAGS.py} "-Rtest [[$$(shell echo $$@ | sed 's/^test_//')]]" $$^ > $$@
endef

# notangle exits 2 on an undefined chunk, but its redirected output stays
# behind and is newer than the source, so the next run would take the
# incomplete test file as up to date.  .DELETE_ON_ERROR removes it.
.DELETE_ON_ERROR:

#PYTESTFLAGS+=--pdb
PYTESTFLAGS+=

TESTS=	$(shell ${find_tests})

$(foreach files,${TESTS},$(eval $(call def_target, ${files})))

.PHONY: all
all: conftest.py
all: $(foreach files,${TESTS},$(shell echo ${files} | cut -d: -f1))
	poetry run pytest ${PYTESTFLAGS}

conftest.py: ../src/ladok3/testing.nw
	notangle ${NOTANGLEFLAGS.py} "-R[[conftest.py]]" $^ > $@

.PHONY: clean
clean:
	${RM} conftest.py
	${RM} $(foreach files,${TESTS},$(shell echo ${files} | cut -d: -f1))
	${RM} -Rf __pycache__

.PHONY: distclean
distclean:



INCLUDE_MAKEFILES=../makefiles
include ${INCLUDE_MAKEFILES}/noweb.mk
