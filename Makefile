
all:
	@ echo "Usage: make build " ; \
	echo "       make check" ; \
	echo "       make clean" ; \
	echo "       make clean-all" ; \
	echo "       make dist" ; \
	echo "       make install" ; \
	echo "       make install-dev" ; \
	echo "       make lint" ; \
	echo "       make sdist (alias for dist)" ; \
	echo "       make test[s] (alias for check)" ; \
	echo "       make uninstall-dev" ; \
	echo "       make vbump" ; \

build::
	@ python3 setup.py build

check:
	@ ( cd tests && make $@ )

clean:
	@ rm -f MANIFEST `find . -name "*.pyc" -o -name "*~" -o -name "*.lint"`
	@ rm -rf build kargparse.egg-info `find . -name __pycache__ -type d`

clean-all: clean

dist sdist::
	@ python3 setup.py sdist

install: build
	@ python3 setup.py install

install-dev:
	@ python3 setup.py --quiet develop --user

lint:
	@ for file in `find . -name "*.py" | egrep -v '(__init__|setup)[.]py'` ; do echo "$${file} --> $${file}.lint" ; pylint --rcfile=pylint.rc --exit-zero $${file} > $${file}.lint ; done

test tests: check

uninstall-dev:
	@ python3 setup.py --quiet develop --uninstall --user > /dev/null 2>&1

vbump:
	@ version_helper_git_pep440 -b + -f kargparse/__init__.py

