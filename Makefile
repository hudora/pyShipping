# setting the PATH seems only to work in GNUmake not in BSDmake
PATH := ./testenv/bin:$(PATH)

default: dependencies check test statistics

check:
	find pyshipping -name '*.py' | xargs /usr/local/hudorakit/bin/hd_pep8
	/usr/local/hudorakit/bin/hd_pylint -f parseable pyshipping | tee pylint.out
	grep "our code has been rated at" < pylint.out|cut -d '/' -f 1|cut -d ' ' -f 7 >> .pylint.score

build:
	python setup.py build

test:
	PYTHONPATH=. python pyshipping/__init__.py # find import errors
	PYTHONPATH=. python pyshipping/shipment.py 
	PYTHONPATH=. python pyshipping/package.py 
	PYTHONPATH=. python pyshipping/fortras/test.py 
	PYTHONPATH=. python pyshipping/carriers/dpd/georoute_test.py

dependencies:
	virtualenv testenv
	pip -q install -E testenv -r requirements.txt

statistics:
	sloccount --wide --details pyshipping | tee sloccount.sc

upload: build doc
	python setup.py sdist bdist_egg
	rsync -rvapP dist/* root@cybernetics.hudora.biz:/usr/local/www/data/nonpublic/eggs/
	rsync -rvapP dist/* root@cybernetics.hudora.biz:/usr/local/www/data/dist/pyShipping/
	rsync -rvapP html root@cybernetics.hudora.biz:/usr/local/www/apache22/data/dist/pyShipping/
	

doc: build
	rm -Rf html
	mkdir -p html
	mkdir -p html/fortras
	mkdir -p html/carriers
	sh -c '(cd html; pydoc -w ../pyshipping/*.py)'
	sh -c '(cd html/fortras; pydoc -w ../../pyshipping/*.py)'
	sh -c '(cd html/carriers; pydoc -w ../../pyshipping/*.py)'

install: build
	sudo python setup.py install

clean:
	rm -Rf testenv build dist html test.db pyShipping.egg-info pylint.out sloccount.sc pip-log.txt
	find . -name '*.pyc' -or -name '*.pyo' -delete

.PHONY: test build clean check upload doc install
