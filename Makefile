# === COLORS ===
RED     := $(shell tput -Txterm setaf 1)
GREEN   := $(shell tput -Txterm setaf 2)
YELLOW  := $(shell tput -Txterm setaf 3)
BLUE    := $(shell tput -Txterm setaf 4)
PURPLE  := $(shell tput -Txterm setaf 5)
CYAN    := $(shell tput -Txterm setaf 6)
WHITE   := $(shell tput -Txterm setaf 7)
BOLD   	:= $(shell tput -Txterm bold)
RESET   := $(shell tput -Txterm sgr0)

# === VARIABLES ===
TEST_OPTS ?=
LINT_OPTS ?=
PIP_OPTS ?=
PIP_ARGS = --quiet --upgrade
PIP_COMPILE_ARGS = --upgrade --no-emit-index-url --no-emit-trusted-host

.PHONY: install update lint test help .update-pip .pip-sync .pip-compile .update-pc

.update-pip:
	@echo "\n${GREEN}Update pip${RESET}"
	python -m pip install ${PIP_ARGS} pip pip-tools

.update-pc:
	@echo "\n${GREEN}Update pre-commit hooks${RESET}"
	@python -m pre_commit --version &> /dev/null || (echo "Installing pre-commit" && python -m pip install ${PIP_ARGS} pre-commit)
	@python -m pre_commit autoupdate

.pip-compile:
	@python -m piptools compile --version &> /dev/null || (echo "Installing pip-tools" && python -m pip install --quiet pip-tools)
	CUSTOM_COMPILE_COMMAND="make update" python -m piptools compile  $(PIP_COMPILE_ARGS) --output-file function/requirements.txt pyproject.toml
	CUSTOM_COMPILE_COMMAND="make update" python -m piptools compile  $(PIP_COMPILE_ARGS) --extra dev --pip-args "--constrain function/requirements.txt" --output-file dev-requirements.txt pyproject.toml

.pip-sync:
	@python -m piptools sync --version &> /dev/null || (echo "Installing pip-tools" && python -m pip install --quiet pip-tools)
	python -m piptools sync function/requirements.txt dev-requirements.txt
	python -m pip install --no-deps --disable-pip-version-check --quiet --editable .
	python -m pip install --no-deps --disable-pip-version-check --quiet --editable ".[dev]"

install: .update-pip .pip-sync ## Install dependencies in current environment

update: .update-pip .pip-compile .pip-sync .update-pc ## Update dependencies in current environment

test: ## Run all unit tests
	@echo "\n${CYAN}Running unit tests${RESET}"
	python -m pytest $(TEST_OPTS)

lint: ## Run linting tools
	@echo ''
	@echo "\n${CYAN}Running ruff${RESET}"
ifeq ($(LINT_OPTS), nofix)
	python -m ruff .
else
	python -m ruff --fix .
endif

	@echo "\n${CYAN}Running black${RESET}"
ifeq ($(LINT_OPTS), nofix)
	python -m black . --check
else
	python -m black .
endif

	@echo "\n${CYAN}Running mypy${RESET}"
	python -m mypy .

help: ## Show this help message
	@egrep -h '\s##\s' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'
