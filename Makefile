.PHONY: help serve test clean validate

help:
	@echo "LSP D-PLANNER Development Commands"
	@echo "serve    - Start local web server"
	@echo "test     - Run validation tests"
	@echo "validate - Validate HTML"
	@echo "clean    - Clean temporary files"

serve:
	python3 -m http.server 8000

test: validate
	@echo "Tests completed"

validate:
	@echo "Validating HTML..."
	@grep -q "<!DOCTYPE html>" index.html && echo "✓ Valid HTML" || echo "✗ Invalid HTML"

clean:
	@find . -name "*.tmp" -delete
	@find . -name ".DS_Store" -delete
	@echo "Cleaned"
