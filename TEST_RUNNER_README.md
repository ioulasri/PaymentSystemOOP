# Test Runner Documentation

## Overview
The `test_runner.py` script is a comprehensive test execution and result parsing tool for the PaymentSystemOOP project. It runs pytest tests and organizes the results into separate files for easy analysis.

## Features

### ✅ **Automated Test Execution**
- Runs all tests or specific test targets
- Supports pattern matching for selective testing
- Configurable verbosity and coverage options

### 📊 **Result Organization**
All test results are automatically saved to the `test_results/` folder with the following files:
- `success.txt` - All passed tests
- `failed.txt` - All failed tests
- `skipped.txt` - All skipped tests
- `errors.txt` - All tests with errors
- `warnings.txt` - All warnings from the test run
- `summary.txt` - Comprehensive summary with statistics
- `full_output.txt` - Complete test output
- `index.html` - Interactive web dashboard

### 🎯 **Smart Parsing**
- Extracts individual test results with status
- Groups tests by file for better organization
- Calculates statistics and pass rates
- Captures warnings and error details

## Usage Examples

### Run All Tests
```bash
python test_runner.py
```

### Run Specific Test File
```bash
python test_runner.py test_creditcard.py
```

### Run Tests Matching a Pattern
```bash
python test_runner.py validate          # All tests containing "validate"
python test_runner.py TestCrypto        # All tests in TestCrypto class
```

### Run with Coverage Report
```bash
python test_runner.py --coverage
```

### Run in Quiet Mode
```bash
python test_runner.py --quiet
```

### Combined Options
```bash
python test_runner.py test_paypal.py --coverage --quiet
```

## Command Line Options

| Option | Short | Description |
|--------|-------|-------------|
| `--coverage` | `-c` | Generate coverage report |
| `--quiet` | `-q` | Run in quiet mode (less verbose) |
| `--help` | `-h` | Show help message |

## Output File Formats

### Success/Failed/Skipped/Error Files
Each file contains:
- Timestamp header
- Total count
- Tests grouped by file
- Individual test details with status emojis

Example:
```
✅ TestCrypto::test_validate_wallet [32%]
❌ TestPayment::test_invalid_amount [45%]
```

### Warnings File
Contains:
- All warning messages
- Source locations
- Warning descriptions
- Total warning count

### Summary File
Includes:
- Test execution statistics
- Pass/fail rates by file
- Overall test health
- File breakdown

### HTML Dashboard
Interactive web interface with:
- Visual statistics cards
- Quick links to all result files
- Responsive design for easy viewing

## Integration Tips

### Continuous Integration
Add to your CI pipeline:
```yaml
- name: Run Tests
  run: python test_runner.py
- name: Archive Test Results
  uses: actions/upload-artifact@v2
  with:
    name: test-results
    path: test_results/
```

### Development Workflow
1. Make code changes
2. Run specific tests: `python test_runner.py test_mymodule.py`
3. Check `summary.txt` for quick overview
4. Review `failed.txt` for issues
5. Open `index.html` in browser for detailed view

### Pre-commit Hook
```bash
#!/bin/sh
python test_runner.py
if [ $? -ne 0 ]; then
    echo "Tests failed. Check test_results/ for details."
    exit 1
fi
```

## File Structure
```
PaymentSystemOOP/
├── test_runner.py          # Main test runner script
├── test_results/           # Generated results folder
│   ├── success.txt
│   ├── failed.txt
│   ├── skipped.txt
│   ├── errors.txt
│   ├── warnings.txt
│   ├── summary.txt
│   ├── full_output.txt
│   └── index.html
├── tests/                  # Test files
└── src/                    # Source code
```

## Troubleshooting

### Common Issues

**Script not executable:**
```bash
chmod +x test_runner.py
```

**Missing pytest:**
```bash
pip install pytest
```

**Permission errors on test_results folder:**
```bash
mkdir -p test_results
chmod 755 test_results
```

**Coverage not working:**
```bash
pip install pytest-cov
```

### Exit Codes
- `0` - All tests passed
- `1` - Some tests failed or script error

## Advanced Usage

### Custom Test Discovery
The script supports various pytest target formats:
- File: `test_creditcard.py`
- Class: `TestPayment`
- Method: `test_validate_amount`
- Path: `tests/test_crypto.py::TestCrypto::test_wallet`

### Pattern Examples
```bash
python test_runner.py "test_validate"     # Tests with "validate" in name
python test_runner.py "test_credit"       # Credit card related tests
python test_runner.py "Payment"           # All Payment class tests
```

---
