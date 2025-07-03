.DEFAULT_GOAL := help

VERSION_PART ?= $(shell bash -c 'read -p "Version part [major, minor, patch]: " version_part; echo $$version_part')
bump:  ## Bump the project version and create a tag
	uv run bump2version $(VERSION_PART)
.PHONY: bump

help: ## Show this help
	@echo "Specify a command. The choices are:"
	@grep -E '^[0-9a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[0;36m%-12s\033[m %s\n", $$1, $$2}'
	@echo ""
.PHONY: help

setup:  ## Setup the development environment
	@uv sync
	@cp .pre-commit-config.standard.yaml .pre-commit-config.yaml
	@uv run pre-commit install

setup-strict: setup  ## Setup the development environment with strict pre-commit rules
	@echo "Appending strict pre-commit rules..."
	@cat .pre-commit-config.addon.strict.yaml >> .pre-commit-config.yaml

lint:   ## Runs linting on all project files
	@tempfile=$$(mktemp) && \
	trap 'rm -f $$tempfile' EXIT && \
	cat .pre-commit-config.standard.yaml .pre-commit-config.addon.strict.yaml > $$tempfile && \
	uv run pre-commit run --all-files -c $$tempfile
.PHONY: lint

test:  ## Run the project tests
	@uv run tox -r
.PHONY: test

testproject:  ## Test the copier template by creating a new project in temporary directory
	@mkdir -p testprojects
	@tempdir=$$(mktemp -p testprojects -d testproject.XXX) && \
	copier copy --trust --vcs-ref=HEAD . $$tempdir && \
	echo "Created project in $$tempdir"
.PHONY: testproject
