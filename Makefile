# Makefile for Astro Horoscope project

.PHONY: help test test-unit test-integration test-frontend test-coverage clean run

help:			## Show this help message
	@echo "🌟 Astro Horoscope - Available Commands 🌟"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}'

install:		## Install dependencies
	pip install -r requirements.txt

test:			## Run all tests
	python -m pytest tests/ -v

test-unit:		## Run unit tests only
	python -m unittest tests.test_main.TestUtilityFunctions -v

test-integration:	## Run integration tests
	python -m unittest tests.test_main.TestIntegration -v

test-frontend:		## Run frontend tests
	python -m unittest tests.test_frontend -v

test-coverage:		## Run tests with coverage
	python -m pytest tests/ --cov=main --cov-report=term-missing

run:			## Start the development server
	python run.py

run-gunicorn:		## Start with gunicorn
	gunicorn --bind 0.0.0.0:8080 main:app

clean:			## Clean up temporary files
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	rm -rf htmlcov/
	rm -rf .coverage
	rm -rf .pytest_cache/