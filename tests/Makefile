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

#PYTESTFLAGS+=--pdb
PYTESTFLAGS+=

TESTS=	$(shell ${find_tests})

$(foreach files,${TESTS},$(eval $(call def_target, ${files})))

.PHONY: all
all: $(foreach files,${TESTS},$(shell echo ${files} | cut -d: -f1))
	poetry run pytest ${PYTESTFLAGS}

.PHONY: clean
clean:
	${RM} $(foreach files,${TESTS},$(shell echo ${files} | cut -d: -f1))
	${RM} -Rf __pycache__

.PHONY: distclean
distclean:



INCLUDE_MAKEFILES=../makefiles
include ${INCLUDE_MAKEFILES}/noweb.mk
