
PKG_NAME := cryptoprice
PKG_NAME_U := cryptoprice
# PKG_VER := $(shell python -c "from __future__ import print_function; import $(PKG_NAME_U); print($(PKG_NAME_U).__version__)")

.PHONY: test cheese clean

.DEFAULT:
dist: clean
	python ./setup.py sdist

test:
	@echo "Write some tests YO!"

cheese: clean test dist
	python ./setup.py sdist upload

clean:
	rm -fr dist
	rm -fr *.egg-info
	$(MAKE) --directory=docs clean

uninstall:
	-yes y | pip uninstall --exists-action=w $(PKG_NAME)

install: clean test dist
	pip install --pre --exists-action=w ./

dinstall: uninstall install

doc: docs
	$(MAKE) --directory=docs
