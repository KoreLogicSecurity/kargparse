
all:
	@ echo "Usage: make check"

check:
	python3 unit/testerrors.py --verbose
	python3 unit/testparser.py --verbose
	python3 unit/testkargparse.py --verbose

tests: check

