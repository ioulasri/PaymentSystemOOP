# 🔍 Professional Logging System - Implementation Guide

## 📚 **Table of Contents**
1. [Why Logging Matters](#why-logging-matters)
2. [Logging Fundamentals](#logging-fundamentals)
3. [Implementation Steps](#implementation-steps)
4. [Testing Your Logger](#testing-your-logger)
5. [Best Practices](#best-practices)
6. [Interview Talking Points](#interview-talking-points)

---

## 🎯 **Why Logging Matters**

### **For Your Interview:**
When asked "How would you debug a payment processing issue in production?", you can say:

> "I implement structured logging with different severity levels. For payment systems, I log:
> - Transaction IDs for traceability
> - Payment method validation attempts
> - Success/failure states with error details
> - Processing times for performance monitoring
>
> This creates an audit trail and helps quickly identify issues without impacting users."

### **Real-World Scenarios:**

**Scenario 1: Payment Failed**
```
Without logging:
❌ User reports "payment didn't work"
❌ No trace of what happened
❌ Can't reproduce the issue

With logging:
✅ Search logs for transaction ID
✅ See: "Invalid CVV: 12 (expected 3-4 digits)"
✅ Fix user's CVV input
✅ Resolve in 5 minutes
```

**Scenario 2: Performance Issues**
```
Without logging:
❌ "System is slow"
❌ Don't know which payment method
❌ Can't measure improvement

With logging:
✅ See: PayPal taking 3.2s (Credit card: 0.8s)
✅ Identify API timeout issue
✅ Optimize external API calls
✅ Measure 60% improvement
```

---

## 📖 **Logging Fundamentals**

### **1. Log Levels (Severity Hierarchy)**

```python
DEBUG    → Detailed diagnostic info (development only)
INFO     → General informational messages
WARNING  → Something unexpected but system continues
ERROR    → Serious problem, feature fails
CRITICAL → System crash or data corruption
```

**When to use each level:**

```python
# DEBUG - For developers during development
logger.debug(f"Validating card number: {card[-4:]}...")  # Last 4 digits only!

# INFO - For tracking normal operations
logger.info(f"Payment processed successfully for order {order_id}")

# WARNING - For recoverable issues
logger.warning(f"Payment method validation failed, retrying...")

# ERROR - For failures that need attention
logger.error(f"Payment declined: {error_message}")

# CRITICAL - For system failures
logger.critical(f"Database connection lost, payments halted")
```

### **2. Structured Logging**

**Bad (String-based):**
```python
logger.info("Payment of $100.50 processed for user john@example.com")
# Hard to search, parse, or analyze
```

**Good (Structured):**
```python
logger.info(
    "Payment processed",
    extra={
        "amount": 100.50,
        "currency": "USD",
        "user_email": "john@example.com",
        "transaction_id": "TXN123",
        "payment_method": "credit_card"
    }
)
# Easy to search: "find all payments > $100"
# Easy to analyze: "average payment amount by method"
```

### **3. Log Rotation**

**Problem:** Log files grow infinitely → disk full → system crash

**Solution:** Rotate logs by time or size

```python
logs/
├── payment_system.log              ← Current log (today)
├── payment_system.log.2025-11-21   ← Yesterday's log
├── payment_system.log.2025-11-20   ← 2 days ago
└── payment_system.log.2025-11-19   ← 3 days ago (delete after 30 days)
```

### **4. Sensitive Data Protection**

**❌ NEVER LOG:**
- Full credit card numbers
- CVV codes
- Passwords
- API keys
- Social security numbers

**✅ SAFE TO LOG:**
- Last 4 digits of card
- Masked email (j***@example.com)
- Transaction IDs
- Error codes
- Timestamps

---

## 🛠️ **Implementation Steps**

### **Step 1: Basic Logger Setup (15 minutes)**

**Goal:** Create a working logger with file and console output

**What to implement in `src/utils/logger.py`:**

```python
"""
Professional logging system for the payment processing application.

TODO: Add your implementation here
"""

import logging
import logging.handlers
from pathlib import Path

# Configuration constants
LOG_LEVEL = logging.DEBUG  # What level should production use?
LOG_DIR = Path("logs")
LOG_FORMAT = "%(asctime)s | %(name)s | %(levelname)s | %(message)s"

def setup_logging() -> None:
    """
    Configure the root logger.

    TODO: Implement this function to:
    1. Create logs directory if it doesn't exist
    2. Get the root logger
    3. Clear any existing handlers
    4. Add a file handler with rotation
    5. Add a console handler for development

    Hints:
    - Use LOG_DIR.mkdir(exist_ok=True)
    - Use logging.getLogger() for root logger
    - Use logging.handlers.TimedRotatingFileHandler for rotation
    - Use logging.StreamHandler for console
    """
    # YOUR CODE HERE
    pass

def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance for a specific module.

    TODO: Implement this function

    Hints:
    - Use logging.getLogger(name)
    - This should be simple - just one line!
    """
    # YOUR CODE HERE
    pass

# Initialize logging when module is imported
setup_logging()
```

**Questions to think about:**
- Why do we clear existing handlers?
- When should logs rotate? (midnight, size limit, hourly?)
- What's the difference between root logger and named loggers?

---

### **Step 2: Sensitive Data Masking (20 minutes)**

**Goal:** Protect sensitive information in logs

**Add this function to `logger.py`:**

```python
import re
from typing import Any

def mask_sensitive_data(data: Any) -> Any:
    """
    Recursively mask sensitive information.

    TODO: Implement masking for:
    1. Credit card numbers (show last 4 digits)
    2. CVV codes (completely hide)
    3. Email addresses (partial masking)
    4. Passwords (completely hide)

    Hints:
    - Use isinstance(data, dict) to check type
    - Look for keywords in dictionary keys (case-insensitive)
    - Use recursion for nested structures
    - Use regex for patterns in strings: re.sub(r'\b\d{13,16}\b', ...)

    Example:
        >>> mask_sensitive_data({"card_number": "1234567890123456"})
        {"card_number": "************3456"}
    """
    if isinstance(data, dict):
        masked = {}
        for key, value in data.items():
            key_lower = key.lower()

            # TODO: Check for 'card' and 'number' in key
            # TODO: Check for 'cvv' or 'cvc' in key
            # TODO: Check for 'email' in key
            # TODO: Check for 'password' or 'secret' in key
            # TODO: Recursively process other values

            pass
        return masked

    elif isinstance(data, list):
        # TODO: Process each item in list
        pass

    elif isinstance(data, str):
        # TODO: Use regex to mask card patterns
        pass

    else:
        return data
```

**Test your function:**
```python
# Test cases you should try:
test_data = {
    "card_number": "4111111111111111",
    "cvv": "123",
    "email": "john@example.com",
    "password": "secret123"
}

result = mask_sensitive_data(test_data)
print(result)
# Expected: card shows ************1111, cvv shows ***, etc.
```

---

### **Step 3: JSON Formatter (25 minutes)**

**Goal:** Output logs as JSON for better parsing

**Add this class:**

```python
import json
from datetime import datetime

class JSONFormatter(logging.Formatter):
    """
    Format logs as JSON.

    TODO: Implement the format() method to create JSON logs

    Output should look like:
    {
        "timestamp": "2025-11-21T10:30:45.123456",
        "level": "INFO",
        "logger": "payment_processor",
        "message": "Payment processed",
        "module": "payment_processor",
        "function": "process_payment",
        "line": 42
    }
    """

    def format(self, record: logging.LogRecord) -> str:
        """
        Format log record as JSON.

        TODO: Create a dictionary with:
        - timestamp (from record.created using datetime.fromtimestamp)
        - level (record.levelname)
        - logger (record.name)
        - message (record.getMessage())
        - module (record.module)
        - function (record.funcName)
        - line (record.lineno)
        - exception info if present (record.exc_info)
        - any extra fields

        Hints:
        - datetime.fromtimestamp(record.created).isoformat()
        - Use json.dumps(log_data, default=str)
        - Check hasattr(record, 'extra_fields') for extra data
        """
        log_data = {
            # YOUR CODE HERE
        }

        # TODO: Add exception info if present
        # TODO: Add extra fields if present
        # TODO: Return JSON string

        return json.dumps(log_data, default=str)
```

---

### **Step 4: Extra Fields Filter (15 minutes)**

**Goal:** Capture extra fields from logger calls

**Add this class:**

```python
class ExtraFieldsFilter(logging.Filter):
    """
    Capture 'extra' keyword arguments.

    This enables: logger.info("message", extra={"key": "value"})
    """

    def filter(self, record: logging.LogRecord) -> bool:
        """
        Extract extra fields from log record.

        TODO:
        1. Define standard LogRecord attributes to exclude
        2. Loop through record.__dict__
        3. Store non-standard attributes in record.extra_fields
        4. Return True (always allow log through)

        Hints:
        - Standard attributes: 'name', 'msg', 'args', 'created',
          'filename', 'funcName', 'levelname', 'levelno', 'lineno',
          'module', 'msecs', 'message', 'pathname', etc.
        """
        standard_attrs = {
            # TODO: Add all standard attributes
        }

        extra_fields = {}
        # TODO: Loop through record.__dict__ and extract extra fields

        if extra_fields:
            record.extra_fields = extra_fields

        return True
```

---

### **Step 5: Complete setup_logging() (20 minutes)**

**Now finish the setup function:**

```python
def setup_logging() -> None:
    """
    Configure logging with rotation and formatting.
    """
    # Create logs directory
    LOG_DIR.mkdir(exist_ok=True)

    # Get root logger and set level
    root_logger = logging.getLogger()
    root_logger.setLevel(LOG_LEVEL)
    root_logger.handlers.clear()

    # TODO: Create file handler
    # Hints:
    # file_handler = logging.handlers.TimedRotatingFileHandler(
    #     filename=LOG_DIR / "payment_system.log",
    #     when='midnight',      # Rotate at midnight
    #     interval=1,           # Every 1 day
    #     backupCount=30,       # Keep 30 days
    #     encoding='utf-8'
    # )

    # TODO: Set formatter (use JSONFormatter)
    # TODO: Add filter (use ExtraFieldsFilter)
    # TODO: Add handler to root logger

    # TODO: Create console handler for development
    # Hints:
    # console_handler = logging.StreamHandler()
    # Use simpler format for console (human-readable)

    # YOUR CODE HERE
```

---

### **Step 6: Convenience Functions (15 minutes)**

**Add helper functions for common logging patterns:**

```python
def log_payment_attempt(
    logger: logging.Logger,
    payment_method: str,
    amount: float,
    currency: str = "USD",
    **kwargs
) -> None:
    """
    Log a payment attempt.

    TODO: Call logger.info() with structured extra fields

    Include in extra:
    - event: "payment_attempt"
    - payment_method
    - amount
    - currency
    - any kwargs
    """
    # YOUR CODE HERE
    pass

def log_payment_success(
    logger: logging.Logger,
    transaction_id: str,
    amount: float,
    payment_method: str,
    **kwargs
) -> None:
    """
    Log successful payment.

    TODO: Similar to above but with event: "payment_success"
    """
    # YOUR CODE HERE
    pass

def log_payment_failure(
    logger: logging.Logger,
    transaction_id: str,
    error_message: str,
    payment_method: str,
    **kwargs
) -> None:
    """
    Log payment failure.

    TODO: Use logger.error() with event: "payment_failure"
    """
    # YOUR CODE HERE
    pass

def log_validation_error(
    logger: logging.Logger,
    field_name: str,
    error_message: str,
    **kwargs
) -> None:
    """
    Log validation error.

    TODO: Use logger.warning() with event: "validation_error"
    """
    # YOUR CODE HERE
    pass
```

---

## ✅ **Testing Your Logger**

### **Create `tests/unit/test_logger.py`:**

```python
"""
Tests for logging system.
"""

import pytest
import logging
from pathlib import Path
from src.utils.logger import (
    get_logger,
    mask_sensitive_data,
    log_payment_attempt,
)

class TestSensitiveDataMasking:
    """Test sensitive data masking."""

    def test_mask_credit_card_number(self):
        """Card numbers should show only last 4 digits."""
        data = {"card_number": "1234567890123456"}
        masked = mask_sensitive_data(data)

        assert masked["card_number"] == "************3456"
        assert "1234567890" not in masked["card_number"]

    def test_mask_cvv_completely(self):
        """CVV should be completely masked."""
        # TODO: Write this test
        pass

    def test_mask_email_partially(self):
        """Email should show first letter and domain."""
        # TODO: Write this test
        pass

    def test_mask_nested_dict(self):
        """Should recursively mask nested structures."""
        # TODO: Write this test
        pass

class TestLoggerCreation:
    """Test logger creation."""

    def test_get_logger_returns_logger(self):
        """Should return a Logger instance."""
        logger = get_logger("test_module")

        assert isinstance(logger, logging.Logger)
        assert logger.name == "test_module"

    def test_log_file_created(self):
        """Log file should be created."""
        # TODO: Write this test
        # Hint: Check Path("logs/payment_system.log").exists()
        pass

class TestConvenienceFunctions:
    """Test convenience functions."""

    def test_log_payment_attempt(self):
        """Should log payment attempt without errors."""
        logger = get_logger("test")

        # Should not raise
        log_payment_attempt(
            logger,
            payment_method="credit_card",
            amount=100.50,
            transaction_id="TXN123"
        )
```

**Run your tests:**
```bash
cd "/Users/imadoulasri/Oracle_preparation/OOP/Payment system edition"
source .venv/bin/activate
python -m pytest tests/unit/test_logger.py -v
```

---

## 🎯 **Best Practices**

### **1. Log at Entry/Exit Points**

```python
def process_payment(self, order, payment_method):
    self.logger.info("ENTER: process_payment", extra={"order_id": order.id})

    try:
        # ... processing ...
        self.logger.info("EXIT: process_payment - SUCCESS")
        return result
    except Exception as e:
        self.logger.error("EXIT: process_payment - FAILED", exc_info=True)
        raise
```

### **2. Include Context**

```python
# Bad
logger.error("Payment failed")

# Good
logger.error(
    "Payment failed",
    extra={
        "order_id": order.id,
        "amount": order.total,
        "payment_method": "credit_card",
        "error_code": "INSUFFICIENT_FUNDS"
    }
)
```

### **3. Don't Over-Log**

```python
# Bad - Too verbose
for item in order.items:
    logger.debug(f"Processing item {item.id}")  # 1000 logs!

# Good - Summary
logger.debug(f"Processing {len(order.items)} items")
```

### **4. Handle Exceptions Properly**

```python
try:
    payment_method.execute_payment(amount)
except InsufficientFundsError as e:
    # Log with full traceback
    logger.exception("Payment failed due to insufficient funds")
```

---

## 💼 **Interview Talking Points**

### **Question: "How do you handle logging in production?"**

**Your Answer:**
> "I implement structured logging with several key components:
>
> 1. **Log Levels**: I use appropriate severity - DEBUG for development, INFO for operations, WARNING for anomalies, ERROR for failures.
>
> 2. **Structured Logging**: JSON format with key-value pairs makes logs searchable and analyzable.
>
> 3. **Sensitive Data Protection**: I automatically mask credit cards (show last 4 digits), CVVs, and PII.
>
> 4. **Log Rotation**: Daily rotation with 30-day retention prevents disk issues.
>
> 5. **Contextual Information**: Every log includes transaction IDs and metadata for traceability."

---

### **Question: "How would you debug a production payment failure?"**

**Your Answer:**
> "I follow a systematic approach:
>
> 1. Get the transaction ID from the user/error
> 2. Search logs: `grep TXN123 logs/payment_system.log`
> 3. Trace the flow: entry → validation → execution → exit
> 4. Check error details and masked payment data
> 5. Analyze timestamps for timeout issues
>
> My structured logs include all context needed to reproduce and fix issues quickly."

---

## 📝 **Implementation Checklist**

Track your progress:

**Core Implementation:**
- [ ] Create `src/utils/logger.py`
- [ ] Implement `setup_logging()` function
- [ ] Implement `get_logger()` function
- [ ] Implement `mask_sensitive_data()` function
- [ ] Implement `JSONFormatter` class
- [ ] Implement `ExtraFieldsFilter` class
- [ ] Implement convenience functions

**Testing:**
- [ ] Create `tests/unit/test_logger.py`
- [ ] Write tests for masking
- [ ] Write tests for logger creation
- [ ] Write tests for convenience functions
- [ ] Run tests: `pytest tests/unit/test_logger.py -v`

**Verification:**
- [ ] Check logs directory created
- [ ] Verify JSON format in logs
- [ ] Verify sensitive data masked
- [ ] Test with different log levels

**Integration:**
- [ ] Add logging to `PaymentProcessor`
- [ ] Add logging to payment method validations
- [ ] Run full test suite

---

## 🎓 **Key Learning Points**

As you implement, understand:

✅ **Python logging module** - Standard library usage
✅ **Log handlers** - File vs Console vs Syslog
✅ **Log formatters** - JSON vs text format
✅ **Log filters** - Intercepting log records
✅ **Log rotation** - Preventing disk issues
✅ **Security** - PII/sensitive data protection
✅ **Structured logging** - Machine-readable logs
✅ **Production practices** - What works in real systems

---

## 🚀 **Next Steps**

After completing logging:

1. **Commit your code:**
   ```bash
   git add src/utils/logger.py tests/unit/test_logger.py
   git commit -m "feat: implement professional logging system"
   ```

2. **Integrate into existing code:**
   - Add to PaymentProcessor
   - Add to payment methods
   - Test end-to-end

3. **Prepare for Database:**
   - You now have debugging tools
   - Logs will help with database integration
   - Next: PostgreSQL + SQLAlchemy

---

**Questions to ask yourself while coding:**

- Why use `logging.getLogger()` instead of `print()`?
- What's the difference between `logger.error()` and `logger.exception()`?
- Why rotate logs instead of one big file?
- How does JSON format help in production?
- Why mask sensitive data automatically?

**Good luck! Take your time, understand each part, and build it yourself!** 💪
