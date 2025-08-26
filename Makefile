.PHONY: help install test run clean lint format

help:
	@echo "GNews MCP Server - Available commands:"
	@echo "  install    Install dependencies"
	@echo "  test       Run tests"
	@echo "  run        Run the server"
	@echo "  clean      Clean up cache files"
	@echo "  lint       Run linting"
	@echo "  format     Format code"
	@echo "  example    Run example usage"

install:
	@echo "Installing dependencies..."
	pip install -r requirements.txt

install-uv:
	@echo "Installing dependencies with uv..."
	uv sync

test:
	@echo "Running tests..."
	python test_server.py

run:
	@echo "Starting GNews MCP Server..."
	@echo "Make sure GNEWS_API_KEY is set!"
	python main.py

example:
	@echo "Running examples..."
	python examples.py

clean:
	@echo "Cleaning up..."
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -name "*.pyc" -delete
	find . -name "*.pyo" -delete
	find . -name "*.pyd" -delete
	find . -name ".coverage" -delete
	find . -name "*.orig" -delete

lint:
	@echo "Running linting..."
	python -m flake8 main.py --max-line-length=100 --ignore=E203,W503 || echo "flake8 not installed"
	python -m mypy main.py --ignore-missing-imports || echo "mypy not installed"

format:
	@echo "Formatting code..."
	python -m black main.py examples.py test_server.py || echo "black not installed"
	python -m isort main.py examples.py test_server.py || echo "isort not installed"

setup-claude:
	@echo "Setting up Claude Desktop integration..."
	@echo "1. Copy your API key:"
	@echo "   export GNEWS_API_KEY='your_api_key_here'"
	@echo ""
	@echo "2. Add to Claude Desktop config (~/.../claude_desktop_config.json):"
	@echo "   {"
	@echo '     "mcpServers": {'
	@echo '       "gnews": {'
	@echo '         "command": "python",'
	@echo '         "args": ["$(PWD)/main.py"],'
	@echo '         "env": {'
	@echo '           "GNEWS_API_KEY": "your_api_key_here"'
	@echo '         }'
	@echo '       }'
	@echo '     }'
	@echo "   }"
	@echo ""
	@echo "3. Restart Claude Desktop"

check-env:
	@echo "Checking environment..."
	@python -c "import os; print('✅ GNEWS_API_KEY is set' if os.getenv('GNEWS_API_KEY') else '❌ GNEWS_API_KEY not set')"
	@python -c "import mcp; print('✅ MCP installed')" 2>/dev/null || echo "❌ MCP not installed"
	@python -c "import httpx; print('✅ HTTPX installed')" 2>/dev/null || echo "❌ HTTPX not installed"
	@python -c "import pydantic; print('✅ Pydantic installed')" 2>/dev/null || echo "❌ Pydantic not installed"
