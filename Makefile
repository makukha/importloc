SHELL=/bin/bash -euo pipefail

.PHONY: build
build: dist
dist: src/**/* pyproject.toml README.md uv.lock
	uv lock
	rm -rf $@
	uv build

.PHONY: badges
badges: docs/_static/badge-coverage.svg docs/_static/badge-tests.svg
docs/_static/badge-%.svg: .tmp/%.xml
	uv run genbadge $* --local -i $< -o $@

.PHONY: docs
docs: sphinx readthedocs README.md

.PHONY: sphinx
sphinx: docs/_build
docs/_build: docs/usage.md docs/**/*.* src/**/*.*
	rm -rf $@
	cd docs && uv run sphinx-build -b html . _build

.PHONY: readthedocs
readthedocs: docs/requirements.txt
docs/requirements.txt: pyproject.toml uv.lock
	uv export --only-group docs --no-emit-project > $@

README.md: docs/usage.md FORCE
	uv run docsub sync -i $@

%.md: FORCE
	uv run docsub sync -i $@

FORCE:
