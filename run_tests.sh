#!/bin/bash
# Test Runner Wrapper Script
# This script automatically uses the virtual environment if available

# Colors for styled output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
BOLD='\033[1m'
NC='\033[0m' # No Color

# Unicode symbols
PYTHON_ICON="🐍"
ROCKET_ICON="🚀"
CHECK_ICON="✅"
CROSS_ICON="❌"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_PYTHON="$SCRIPT_DIR/.venv/bin/python"

# Styled header
echo ""
echo -e "${BOLD}${BLUE}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BOLD}${BLUE}║${WHITE}                🧪 PaymentSystemOOP Test Runner 🧪            ${BLUE}║${NC}"
echo -e "${BOLD}${BLUE}╚══════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Python environment detection
if [ -f "$VENV_PYTHON" ]; then
    echo -e "${GREEN}${PYTHON_ICON} Using virtual environment Python${NC}"
    echo -e "${CYAN}   └─ ${VENV_PYTHON}${NC}"
else
    echo -e "${YELLOW}${PYTHON_ICON} Using system Python${NC}"
    echo -e "${CYAN}   └─ $(which python)${NC}"
fi

echo ""
echo -e "${PURPLE}${ROCKET_ICON} Starting test execution...${NC}"
echo ""

# Run the test runner
if [ -f "$VENV_PYTHON" ]; then
    "$VENV_PYTHON" "$SCRIPT_DIR/test_runner.py" "$@"
    EXIT_CODE=$?
else
    python "$SCRIPT_DIR/test_runner.py" "$@"
    EXIT_CODE=$?
fi

# Final status message
echo ""
if [ $EXIT_CODE -eq 0 ]; then
    echo -e "${GREEN}${CHECK_ICON} Test execution completed successfully!${NC}"
else
    echo -e "${RED}${CROSS_ICON} Test execution failed with exit code ${EXIT_CODE}${NC}"
fi

echo -e "${BOLD}${BLUE}════════════════════════════════════════════════════════════════${NC}"
echo ""

exit $EXIT_CODE
