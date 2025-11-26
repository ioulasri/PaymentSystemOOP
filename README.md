# 💳 Payment System OOP

[![CI/CD Pipeline](https://github.com/ioulasri/PaymentSystemOOP/actions/workflows/ci-cd.yml/badge.svg)](https://github.com/ioulasri/PaymentSystemOOP/actions/workflows/ci-cd.yml)
[![Code Quality](https://github.com/ioulasri/PaymentSystemOOP/actions/workflows/code-quality.yml/badge.svg)](https://github.com/ioulasri/PaymentSystemOOP/actions/workflows/code-quality.yml)
[![Coverage](https://codecov.io/gh/ioulasri/PaymentSystemOOP/branch/main/graph/badge.svg)](https://codecov.io/gh/ioulasri/PaymentSystemOOP)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A comprehensive **Object-Oriented Payment System** implemented in Python with enterprise-level testing infrastructure, automated CI/CD pipelines, and professional development workflows.

## 🌟 Features

### 💰 Payment Processing
- **Multiple Payment Strategies**: Credit Card, PayPal, Cryptocurrency
- **Secure Transactions**: Input validation and error handling
- **Extensible Architecture**: Easy to add new payment methods

### 👥 User Management
- **Role-Based Access**: Admin and Customer user types
- **User Authentication**: Secure user creation and management
- **Permission System**: Granular access control

### 📦 Order Management
- **Complete Order Processing**: Item management and order tracking
- **Flexible Item System**: Support for various product types
- **Order Validation**: Comprehensive order verification

### 🧪 Professional Testing
- **200+ Comprehensive Tests**: Unit, integration, and end-to-end testing
- **Custom Test Runner**: Styled output with professional formatting
- **Coverage Reporting**: Detailed code coverage analysis
- **Parallel Execution**: Fast test runs with pytest-xdist

### 🚀 DevOps & CI/CD
- **GitHub Actions**: Automated testing and deployment
- **Code Quality**: Pre-commit hooks, linting, type checking
- **Security Scanning**: Vulnerability detection and dependency updates
- **Professional Workflows**: Branch protection and review requirements

## 🚀 Quick Start

### Prerequisites
- Python 3.9 or higher
- Git

### Database Setup (PostgreSQL + SQLAlchemy)

1. **Install PostgreSQL** (if not already installed):
    - macOS: `brew install postgresql`
    - Ubuntu: `sudo apt-get install postgresql`

2. **Create a database and user:**
    ```sh
    createuser payment_user --pwprompt
    createdb payment_db --owner=payment_user
    # Use password: payment_pass (or set your own and update .env)
    ```

3. **Configure environment variables (optional):**
    - By default, the following are used:
      - `PAYMENT_DB_USER=payment_user`
      - `PAYMENT_DB_PASSWORD=payment_pass`
      - `PAYMENT_DB_HOST=localhost`
      - `PAYMENT_DB_PORT=5432`
      - `PAYMENT_DB_NAME=payment_db`
    - You can override these in your shell or with a `.env` file.

4. **Initialize the database tables:**
    ```sh
    PYTHONPATH=. .venv/bin/python src/utils/init_db.py
    ```

5. **Test DB connection and CRUD:**
    ```sh
    PYTHONPATH=. .venv/bin/python src/utils/test_db_crud.py
    ```

6. **Use SQLAlchemy models and services:**
    - See `src/models/sqlalchemy_models.py` for ORM models.
    - See `src/services/db_order_service.py` for example CRUD service integration.

---

### Installation

```bash
# Clone the repository
git clone https://github.com/ioulasri/PaymentSystemOOP.git
cd PaymentSystemOOP

# Install dependencies
make install-dev

# Set up pre-commit hooks
make pre-commit

# Run tests to verify setup
make test
```

### Basic Usage

```python
from src.payment.credit_card import CreditCardPayment
from src.payment.paypal import PayPalPayment
from src.order.order import Order
from src.order.item import Item
from src.user.customer import Customer

# Create a customer
customer = Customer("John Doe", "john@example.com")

# Create an order with items
item1 = Item("Laptop", 999.99, 1)
item2 = Item("Mouse", 29.99, 2)
order = Order(customer)
order.add_item(item1)
order.add_item(item2)

# Process payment
credit_card = CreditCardPayment("1234-5678-9012-3456", "12/25", "123")
payment_result = credit_card.process_payment(order.total)

if payment_result:
    print(f"Payment successful! Total: ${order.total:.2f}")
else:
    print("Payment failed!")
```

## 🧪 Testing

### Run All Tests

```bash
# Using our custom test runner (recommended)
make test

# With coverage report
make test-cov

# Fast parallel execution
make test-fast
```

### Test Categories

```bash
# Unit tests only
python test_runner.py --pattern "test_unit_*"

# Payment system tests
python test_runner.py --pattern "*payment*"

# User management tests
python test_runner.py --pattern "*user*"

# Order processing tests
python test_runner.py --pattern "*order*"
```

### Test Results

The test runner generates multiple output formats:
- **Terminal**: Styled output with colors and progress indicators
- **Text Files**: `success.txt` and `failed.txt` for CI/CD integration
- **JSON Report**: `test_results.json` for programmatic analysis
- **HTML Dashboard**: `index.html` with dark theme interface
- **Coverage Report**: `htmlcov/index.html` for coverage analysis

## 🏗️ Architecture

### Project Structure

```
PaymentSystemOOP/
├── src/                      # Source code
│   ├── payment/             # Payment strategies
│   │   ├── payment_strategy.py    # Base payment interface
│   │   ├── credit_card.py         # Credit card implementation
│   │   ├── paypal.py             # PayPal implementation
│   │   ├── crypto.py             # Cryptocurrency implementation
│   │   └── exceptions.py         # Payment exceptions
│   ├── user/                # User management
│   │   ├── user.py              # Base user class
│   │   ├── customer.py          # Customer implementation
│   │   └── admin.py             # Admin implementation
│   ├── order/               # Order processing
│   │   ├── item.py              # Item class
│   │   └── order.py             # Order management
│   └── utils/               # Utilities
│       └── logger.py            # Logging configuration
├── tests/                   # Test suite
├── .github/                 # GitHub Actions workflows
├── test_runner.py          # Custom test runner
├── run_tests.sh           # Styled test script
└── index.html             # Test results dashboard
```

### Design Patterns

- **Strategy Pattern**: Payment processing strategies
- **Factory Pattern**: User creation
- **Observer Pattern**: Order status updates
- **Singleton Pattern**: Logger utility
- **Composite Pattern**: Order item management

## 🔧 Development

### Code Quality Standards

```bash
# Format code
make format

# Type checking
make type-check

# Security scanning
make security

# Run all quality checks
make ci-test
```

### Pre-commit Hooks

Automatically run on every commit:
- **Black**: Code formatting (88-character line length)
- **isort**: Import sorting
- **flake8**: Linting and style checking
- **mypy**: Static type checking
- **bandit**: Security vulnerability scanning

### Contributing

1. **Fork** the repository
2. **Create** a feature branch: `git checkout -b feature/amazing-feature`
3. **Make** your changes and add tests
4. **Run** quality checks: `make ci-test`
5. **Commit** your changes: `git commit -m 'feat: add amazing feature'`
6. **Push** to the branch: `git push origin feature/amazing-feature`
7. **Submit** a Pull Request

## 🚀 CI/CD Pipeline

### GitHub Actions Workflows

- **🔄 CI/CD Pipeline**: Comprehensive testing across Python versions
- **🔍 Code Quality**: Advanced linting and security scanning
- **📦 Dependency Updates**: Automated dependency management
- **🚀 Deployment**: Automated releases and deployments

### Quality Gates

- ✅ All tests must pass
- ✅ Code coverage > 90%
- ✅ No linting errors
- ✅ Type checking passes
- ✅ Security scan clean
- ✅ Documentation updated

## 📊 Project Metrics

| Metric | Value |
|--------|-------|
| **Total Tests** | 200+ |
| **Code Coverage** | >90% |
| **Test Execution Time** | <30 seconds |
| **Supported Python Versions** | 3.9, 3.10, 3.11, 3.12 |
| **Security Score** | A+ |
| **Documentation Coverage** | 100% |

## 🛠️ Available Commands

| Command | Description |
|---------|-------------|
| `make test` | Run all tests |
| `make test-cov` | Run tests with coverage |
| `make test-fast` | Run tests in parallel |
| `make lint` | Run linting checks |
| `make format` | Format code |
| `make type-check` | Run type checking |
| `make security` | Run security scan |
| `make clean` | Clean build artifacts |
| `make docs` | Generate documentation |
| `make build` | Build package |
| `make ci-test` | Run all CI checks |

## 🔧 Configuration Files

- **`pyproject.toml`**: Modern Python packaging and tool configuration
- **`setup.cfg`**: Legacy Python packaging configuration
- **`.pre-commit-config.yaml`**: Pre-commit hooks configuration
- **`Makefile`**: Development workflow automation
- **`.github/workflows/`**: CI/CD pipeline definitions

## 📚 Documentation

- **[Developer Guide](DEVELOPER_GUIDE.md)**: Comprehensive development documentation
- **[Test Runner Guide](TEST_RUNNER_README.md)**: Detailed test runner documentation
- **[API Documentation](docs/api.md)**: Code API reference
- **[Architecture Guide](docs/architecture.md)**: System architecture overview

## 🐛 Troubleshooting

### Common Issues

**Tests not running?**
```bash
# Check Python path
export PYTHONPATH="${PYTHONPATH}:$(pwd)/src"

# Reinstall dependencies
make install-dev
```

**Pre-commit hooks failing?**
```bash
# Clean and reinstall
pre-commit clean
pre-commit install
make format
```

**Coverage reports missing?**
```bash
# Clean and regenerate
make clean
make test-cov
```

## 📄 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

## 🤝 Support

- **Issues**: [GitHub Issues](https://github.com/ioulasri/PaymentSystemOOP/issues)
- **Discussions**: [GitHub Discussions](https://github.com/ioulasri/PaymentSystemOOP/discussions)
- **Documentation**: [Developer Guide](DEVELOPER_GUIDE.md)

## 🙏 Acknowledgments

- Python community for excellent testing tools
- GitHub Actions for CI/CD infrastructure
- Open source contributors for inspiration

---

**Made with ❤️ by [ioulasri](https://github.com/ioulasri) & [hamzaouadia](https://github.com/hamzaouadia)**

*A collaborative project bringing together expertise in payment systems and DevOps automation.*
