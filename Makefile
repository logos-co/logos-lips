.PHONY: install lint build serve

MDBOOK_VERSION ?= 0.4.52

install:
	cargo install mdbook --version $(MDBOOK_VERSION)

serve:
	python scripts/run_runtime_generators.py
	mdbook serve -p 3000 -n 0.0.0.0

build:
	python scripts/run_runtime_generators.py
	mdbook build

lint:
	python scripts/gen_rfc_index.py
	python scripts/gen_summary.py
	python scripts/validate_metadata.py --check
	python scripts/validate_generated_outputs.py
	npx markdownlint-cli2@0.12.1 "docs/**/*.md" --config .markdownlint.yaml
	npm run lint:remark
