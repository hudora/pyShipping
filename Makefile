check: clean
	find pyshipping -name '*.py'  -exec pep8 --ignore=E501,W291 --repeat {} \;
	pylint pyshipping

build:
	python setup.py build

test:
	sh -c '(cd tests; python ./runtests.py -v 1 --settings=testsettings)'
	python eap/api.py

upload: build
	python setup.py sdist bdist_egg
	rsync -rvapP dist/* root@cybernetics.hudora.biz:/usr/local/www/data/nonpublic/eggs/

# publish:
# 	# remove development tag
# 	perl -npe 's/^tag_build = .dev/# tag_build = .dev/' -i setup.cfg
# 	svn commit
# 	python setup.py build sdist bdist_egg upload
# 	# add development tag
# 	perl -npe 's/^\# tag_build = .dev/tag_build = .dev/' -i setup.cfg
# 	rsync dist/* root@cybernetics.hudora.biz:/usr/local/www/apache22/data/dist/huDjango/
# 	echo "now bump version number in setup.py and commit"

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
	rm -Rf build dist html test.db
	find . -name '*.pyc' -or -name '*.pyo' -delete

.PHONY: test build
