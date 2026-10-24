MODULES=src/gollyx_maps tests

CB := $(shell git branch --show-current)

test:
	PYTHONPATH=src python3 -m pytest -v

lint:
	flake8 $(MODULES)

clean:
	rm -fr build dist __pycache__ *.egg-info/

release_mainx:
	@echo "Releasing current branch $(CB) to mainx"
	scripts/release.sh $(CB) mainx
