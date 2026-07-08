.PHONY: install help clean play play-mock list-ports

help:
	@echo "Available commands:"
	@echo "  make install      - Install Python requirements"
	@echo "  make clean        - Remove __pycache__ and .pyc files"
	@echo "  make list-ports   - List available serial ports"
	@echo "  make play PORT=COMx - Run the game (e.g., make play PORT=COM5)"
	@echo "  make play-mock    - Run the game in mock mode (no serial port needed)"

install:
	pip install -r requirements.txt

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find src -type d -name build -exec rm -rf {} + 2>/dev/null || true
	@echo "Cleaned up cache and build files"

list-ports:
	python3 -m serial.tools.list_ports

play:
	@if [ -z "$(PORT)" ]; then \
		echo "Error: PORT not specified"; \
		echo "Usage: make play PORT=COM5"; \
		exit 1; \
	fi
	PYTHONPATH=src python3 src/pc/main.py $(PORT)

play-mock:
	PYTHONPATH=src python3 src/pc/main.py --mock
