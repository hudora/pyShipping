check: clean
	find pyshipping -name '*.py'  -exec pep8 --ignore=E501,W291 --repeat {} \;
	pylint pyshipping

build:
	python setup.py build

test:
	python pyshipping/shipment.py 
	python pyshipping/package.py 
	python pyshipping/carriers/dpd/georoute_test.py
	PYTHONPATH=. python pyshipping/fortras/test.py 

upload: build doc
	python setup.py sdist bdist_egg
	rsync -rvapP dist/* root@cybernetics.hudora.biz:/usr/local/www/data/nonpublic/eggs/
	rsync -rvapP html root@cybernetics.hudora.biz:/usr/local/www/apache22/data/dist/pyShipping

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
	rm -Rf build dist html test.db pyShipping.egg-info
	find . -name '*.pyc' -or -name '*.pyo' -delete

.PHONY: test build clean check upload doc install
