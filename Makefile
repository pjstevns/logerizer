default: buildout

buildout: bin/buildout
	bin/buildout -Nv

bin/buildout: bin/pip
	bin/pip install zc.buildout

bin/pip: bin/python

bin/python:
	python3.4 -m virtualenv .




