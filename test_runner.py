#!/usr/bin/env python3
"""
Test Runner Script for PaymentSystemOOP
==========================================

This script runs pytest tests and organizes the results into separate files:
- success.txt: All passed tests
- failed.txt: All failed tests
- skipped.txt: All skipped tests
- errors.txt: All tests with errors
- warnings.txt: All warnings
- summary.txt: Test run summary
- full_output.txt: Complete test output

Usage:
    python test_runner.py                    # Run all tests
    python test_runner.py test_creditcard    # Run specific test file
    python test_runner.py TestCrypto         # Run specific test class
    python test_runner.py test_validate      # Run tests matching pattern

Author: GitHub Copilot Assistant
Date: November 2025
"""

import argparse
import os
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path


class TestResultParser:
    """Parser for pytest output to extract and categorize test results."""

    def __init__(self):
        self.passed_tests = []
        self.failed_tests = []
        self.skipped_tests = []
        self.error_tests = []
        self.warnings = []
        self.summary_info = {}
        self.full_output = ""

    def parse_output(self, output: str):
        """Parse pytest output and categorize results."""
        self.full_output = output
        lines = output.split("\n")

        # Parse individual test results
        test_result_pattern = (
            r"^(.*?)::(.*?)::(.*?)\s+(PASSED|FAILED|SKIPPED|ERROR)\s*(\[.*?\])?"
        )

        for line in lines:
            match = re.match(test_result_pattern, line)
            if match:
                file_path = match.group(1)
                test_class = match.group(2)
                test_method = match.group(3)
                status = match.group(4)
                percentage = match.group(5) if match.group(5) else ""

                test_info = {
                    "file": file_path,
                    "class": test_class,
                    "method": test_method,
                    "full_name": f"{file_path}::{test_class}::{test_method}",
                    "status": status,
                    "percentage": percentage,
                }

                if status == "PASSED":
                    self.passed_tests.append(test_info)
                elif status == "FAILED":
                    self.failed_tests.append(test_info)
                elif status == "SKIPPED":
                    self.skipped_tests.append(test_info)
                elif status == "ERROR":
                    self.error_tests.append(test_info)

        # Parse warnings
        warning_section = False
        for line in lines:
            if "== warnings summary ==" in line:
                warning_section = True
                continue
            elif warning_section and line.startswith("="):
                warning_section = False
            elif warning_section and line.strip():
                self.warnings.append(line.strip())

        # Parse summary
        self._parse_summary(lines)

    def _parse_summary(self, lines):
        """Extract summary information from pytest output."""
        for line in lines:
            # Look for summary line pattern
            if "passed" in line and (
                "failed" in line
                or "error" in line
                or "skipped" in line
                or "warnings" in line
            ):
                # Extract numbers using regex
                passed_match = re.search(r"(\d+)\s+passed", line)
                failed_match = re.search(r"(\d+)\s+failed", line)
                skipped_match = re.search(r"(\d+)\s+skipped", line)
                error_match = re.search(r"(\d+)\s+error", line)
                warning_match = re.search(r"(\d+)\s+warning", line)

                self.summary_info = {
                    "passed": (
                        int(passed_match.group(1))
                        if passed_match
                        else len(self.passed_tests)
                    ),
                    "failed": (
                        int(failed_match.group(1))
                        if failed_match
                        else len(self.failed_tests)
                    ),
                    "skipped": (
                        int(skipped_match.group(1))
                        if skipped_match
                        else len(self.skipped_tests)
                    ),
                    "errors": (
                        int(error_match.group(1))
                        if error_match
                        else len(self.error_tests)
                    ),
                    "warnings": (
                        int(warning_match.group(1))
                        if warning_match
                        else len(self.warnings)
                    ),
                    "total": 0,
                }
                break

        # Calculate total if not found in summary
        if self.summary_info:
            self.summary_info["total"] = (
                self.summary_info["passed"]
                + self.summary_info["failed"]
                + self.summary_info["skipped"]
                + self.summary_info["errors"]
            )


class TestRunner:
    """Main test runner class."""

    def __init__(self):
        self.project_root = Path(__file__).parent.absolute()
        self.results_dir = self.project_root / "test_results"
        self.results_dir.mkdir(exist_ok=True)
        self.parser = TestResultParser()

    def run_tests(self, test_target=None, verbose=True, coverage=False):
        """
        Run pytest with specified parameters.

        Args:
            test_target (str): Specific test file, class, or pattern to run
            verbose (bool): Run with verbose output
            coverage (bool): Run with coverage report

        Returns:
            tuple: (returncode, stdout, stderr)
        """
        # Build pytest command
        # Use virtual environment python if available
        venv_python = self.project_root / ".venv" / "bin" / "python"
        if venv_python.exists():
            cmd = [str(venv_python), "-m", "pytest"]
        else:
            cmd = ["python", "-m", "pytest"]

        if test_target:
            # Handle different types of test targets
            if test_target.endswith(".py"):
                cmd.append(f"tests/{test_target}")
            elif "::" in test_target:
                cmd.append(test_target)
            else:
                # Pattern matching
                cmd.extend(["-k", test_target])
        else:
            cmd.append("tests/")

        if verbose:
            cmd.append("-v")

        if coverage:
            try:
                import pytest_cov

                cmd.extend(["--cov=src", "--cov-report=term-missing"])
            except ImportError:
                print(
                    "⚠️  Warning: pytest-cov not installed. Running without coverage."
                )
                print("   Install with: pip install pytest-cov")

        # Add additional useful flags
        cmd.extend(["--tb=short"])

        # Styled command display
        self._print_command_info(cmd, test_target, coverage)

        try:
            result = subprocess.run(
                cmd,
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=300,  # 5 minute timeout
            )
            return result.returncode, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            return 1, "", "Test execution timed out after 5 minutes"
        except Exception as e:
            return 1, "", f"Error running tests: {str(e)}"

    def save_results(self):
        """Save parsed results to organized files."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Save successful tests
        self._save_test_list(
            self.parser.passed_tests,
            "success.txt",
            f"SUCCESSFUL TESTS - {timestamp}\n" + "=" * 60 + "\n\n",
        )

        # Save failed tests
        self._save_test_list(
            self.parser.failed_tests,
            "failed.txt",
            f"FAILED TESTS - {timestamp}\n" + "=" * 60 + "\n\n",
        )

        # Save skipped tests
        self._save_test_list(
            self.parser.skipped_tests,
            "skipped.txt",
            f"SKIPPED TESTS - {timestamp}\n" + "=" * 60 + "\n\n",
        )

        # Save error tests
        self._save_test_list(
            self.parser.error_tests,
            "errors.txt",
            f"TESTS WITH ERRORS - {timestamp}\n" + "=" * 60 + "\n\n",
        )

        # Save warnings
        if self.parser.warnings:
            warnings_content = f"WARNINGS - {timestamp}\n" + "=" * 60 + "\n\n"
            warnings_content += "\n".join(self.parser.warnings)
            warnings_content += f"\n\nTotal warnings: {len(self.parser.warnings)}\n"
        else:
            warnings_content = (
                f"WARNINGS - {timestamp}\n" + "=" * 60 + "\n\nNo warnings found.\n"
            )

        self._save_file("warnings.txt", warnings_content)

        # Save summary
        summary_content = self._generate_summary(timestamp)
        self._save_file("summary.txt", summary_content)

        # Save full output
        full_output_content = f"FULL TEST OUTPUT - {timestamp}\n" + "=" * 60 + "\n\n"
        full_output_content += self.parser.full_output
        self._save_file("full_output.txt", full_output_content)

        # Create index file
        self._create_index_file(timestamp)

    def _save_test_list(self, test_list, filename, header):
        """Save a list of tests to a file with proper formatting."""
        if not test_list:
            content = header + "No tests found in this category.\n"
        else:
            content = header
            content += f"Total count: {len(test_list)}\n\n"

            # Group by file for better organization
            by_file = {}
            for test in test_list:
                file_name = test["file"].split("/")[-1]  # Get just filename
                if file_name not in by_file:
                    by_file[file_name] = []
                by_file[file_name].append(test)

            for file_name, tests in sorted(by_file.items()):
                content += f"📁 {file_name}\n"
                content += "-" * 40 + "\n"
                for test in tests:
                    status_emoji = (
                        "✅"
                        if test["status"] == "PASSED"
                        else (
                            "❌"
                            if test["status"] == "FAILED"
                            else "⏭️"
                            if test["status"] == "SKIPPED"
                            else "💥"
                        )
                    )
                    content += f"{status_emoji} {test['class']}::{test['method']} {test['percentage']}\n"
                content += "\n"

        self._save_file(filename, content)

    def _generate_summary(self, timestamp):
        """Generate a comprehensive summary of test results."""
        summary = f"📅 {timestamp}\n\n"

        if self.parser.summary_info:
            total = self.parser.summary_info["total"]
            passed = self.parser.summary_info["passed"]
            failed = self.parser.summary_info["failed"]
            skipped = self.parser.summary_info["skipped"]
            errors = self.parser.summary_info["errors"]
            warnings = self.parser.summary_info["warnings"]

            # Calculate percentages
            pass_rate = (passed / total * 100) if total > 0 else 0

            # Statistics box
            summary += "┌─ 📊 Test Statistics ─────────────────────────────────────┐\n"
            summary += (
                f"│ Total Tests:     {total:<8} │ Pass Rate: {pass_rate:>6.1f}%     │\n"
            )
            summary += f"│ ✅ Passed:       {passed:<8} │ ❌ Failed:      {failed:<8} │\n"
            summary += (
                f"│ ⏭️ Skipped:      {skipped:<8} │ 💥 Errors:      {errors:<8} │\n"
            )
            summary += f"│ ⚠️ Warnings:     {warnings:<8} │                        │\n"
            summary += (
                "└───────────────────────────────────────────────────────────┘\n\n"
            )

            # Test status with visual indicator
            if failed == 0 and errors == 0:
                summary += "🎉 SUCCESS: All tests passed! 🎉\n\n"
            else:
                summary += f"⚠️  ATTENTION: {failed + errors} tests need review\n\n"

        # File breakdown
        summary += "📁 Results by File:\n"
        summary += "┌─────────────────────────────────────────────────────────────┐\n"

        all_files = set()
        for test_list in [
            self.parser.passed_tests,
            self.parser.failed_tests,
            self.parser.skipped_tests,
            self.parser.error_tests,
        ]:
            for test in test_list:
                all_files.add(test["file"].split("/")[-1])

        if all_files:
            for file_name in sorted(all_files):
                file_passed = len(
                    [
                        t
                        for t in self.parser.passed_tests
                        if t["file"].endswith(file_name)
                    ]
                )
                file_failed = len(
                    [
                        t
                        for t in self.parser.failed_tests
                        if t["file"].endswith(file_name)
                    ]
                )
                file_skipped = len(
                    [
                        t
                        for t in self.parser.skipped_tests
                        if t["file"].endswith(file_name)
                    ]
                )
                file_errors = len(
                    [
                        t
                        for t in self.parser.error_tests
                        if t["file"].endswith(file_name)
                    ]
                )
                file_total = file_passed + file_failed + file_skipped + file_errors

                if file_total > 0:
                    file_pass_rate = file_passed / file_total * 100
                    status_icon = "✅" if file_failed + file_errors == 0 else "❌"

                    # Format filename to fit in box
                    display_name = (
                        file_name[:25] + "..." if len(file_name) > 28 else file_name
                    )
                    summary += f"│ {status_icon} {display_name:<30} {file_passed:>3}/{file_total:<3} ({file_pass_rate:>5.1f}%) │\n"
        else:
            summary += (
                "│ No test files found                                         │\n"
            )

        summary += "└─────────────────────────────────────────────────────────────┘\n\n"

        # Generated files info
        summary += "📄 Generated Files:\n"
        files_info = [
            ("success.txt", "All passed tests"),
            ("failed.txt", "All failed tests"),
            ("skipped.txt", "All skipped tests"),
            ("errors.txt", "Tests with errors"),
            ("warnings.txt", "All warnings"),
            ("summary.txt", "Complete summary"),
            ("full_output.txt", "Raw test output"),
            ("index.html", "Web dashboard"),
        ]

        for filename, description in files_info:
            icon = self._get_file_icon(filename)
            summary += f"  {icon} {filename:<16} - {description}\n"

        summary += f"\n📍 Location: {self.results_dir}\n"

        return summary

    def _create_index_file(self, timestamp):
        """Create an HTML index file for easy viewing of results."""
        html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Test Results Dashboard - {timestamp}</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 20px;
            background-color: #1a1a1a;
            color: #e0e0e0;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background-color: #2d2d2d;
            padding: 20px;
            border-radius: 8px;
            border: 2px solid #555555;
            box-shadow: 0 4px 8px rgba(0,0,0,0.3);
        }}
        .header {{
            text-align: center;
            margin-bottom: 30px;
            border-bottom: 1px solid #555555;
            padding-bottom: 20px;
        }}
        .header h1 {{
            color: #ffffff;
            margin-bottom: 10px;
        }}
        .stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 15px;
            margin-bottom: 30px;
        }}
        .stat-card {{
            background: #3a3a3a;
            padding: 15px;
            border-radius: 5px;
            text-align: center;
            border: 1px solid #555555;
            border-left: 4px solid #007bff;
            transition: transform 0.2s, box-shadow 0.2s;
        }}
        .stat-card:hover {{
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.4);
        }}
        .stat-card h3 {{
            margin: 0 0 10px 0;
            color: #ffffff;
        }}
        .stat-card p {{
            margin: 0;
            font-size: 1.5em;
            font-weight: bold;
            color: #e0e0e0;
        }}
        .stat-card.passed {{ border-left-color: #28a745; }}
        .stat-card.failed {{ border-left-color: #dc3545; }}
        .stat-card.skipped {{ border-left-color: #ffc107; }}
        .stat-card.errors {{ border-left-color: #fd7e14; }}
        .stat-card.warnings {{ border-left-color: #6c757d; }}
        .files {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 10px;
            margin-bottom: 30px;
        }}
        .file-link {{
            display: block;
            padding: 12px;
            background: #3a3a3a;
            text-decoration: none;
            color: #e0e0e0;
            border-radius: 4px;
            border: 1px solid #555555;
            transition: all 0.2s ease;
            font-weight: 500;
        }}
        .file-link:hover {{
            background: #4a4a4a;
            border-color: #777777;
            transform: translateY(-1px);
            box-shadow: 0 2px 8px rgba(0,0,0,0.3);
        }}
        .timestamp {{
            color: #aaaaaa;
            font-size: 0.9em;
        }}
        h2 {{
            color: #ffffff;
            border-bottom: 1px solid #555555;
            padding-bottom: 10px;
            margin-bottom: 20px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🧪 Test Results Dashboard</h1>
            <p class="timestamp">Generated on {timestamp}</p>
        </div>

        <div class="stats">
            <div class="stat-card passed">
                <h3>✅ Passed</h3>
                <p>{len(self.parser.passed_tests)}</p>
            </div>
            <div class="stat-card failed">
                <h3>❌ Failed</h3>
                <p>{len(self.parser.failed_tests)}</p>
            </div>
            <div class="stat-card skipped">
                <h3>⏭️ Skipped</h3>
                <p>{len(self.parser.skipped_tests)}</p>
            </div>
            <div class="stat-card errors">
                <h3>💥 Errors</h3>
                <p>{len(self.parser.error_tests)}</p>
            </div>
            <div class="stat-card warnings">
                <h3>⚠️ Warnings</h3>
                <p>{len(self.parser.warnings)}</p>
            </div>
        </div>

        <h2>📁 Result Files</h2>
        <div class="files">
            <a href="success.txt" class="file-link">✅ success.txt</a>
            <a href="failed.txt" class="file-link">❌ failed.txt</a>
            <a href="skipped.txt" class="file-link">⏭️ skipped.txt</a>
            <a href="errors.txt" class="file-link">💥 errors.txt</a>
            <a href="warnings.txt" class="file-link">⚠️ warnings.txt</a>
            <a href="summary.txt" class="file-link">📊 summary.txt</a>
            <a href="full_output.txt" class="file-link">📄 full_output.txt</a>
        </div>
    </div>
</body>
</html>
"""
        self._save_file("index.html", html_content)

    def _save_file(self, filename, content):
        """Save content to a file in the results directory."""
        filepath = self.results_dir / filename
        try:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(content)

            # Styled file save confirmation
            file_icon = self._get_file_icon(filename)
            print(f"  {file_icon} {filename:<20} → {filepath}")
        except Exception as e:
            print(f"  ❌ {filename:<20} → Error: {e}")

    def run_and_parse(self, test_target=None, verbose=True, coverage=False):
        """Run tests and parse results."""
        # Header with styled output
        self._print_styled_header()

        # Run tests
        returncode, stdout, stderr = self.run_tests(test_target, verbose, coverage)

        # Combine stdout and stderr for parsing
        full_output = stdout
        if stderr:
            full_output += f"\n\nSTDERR:\n{stderr}"

        print(full_output)

        # Parse results
        self.parser.parse_output(full_output)

        # Save results
        self._print_section_header("💾 Saving Results", "CYAN")
        self.save_results()

        # Print summary
        self._print_section_header("📊 Execution Summary", "PURPLE")
        summary = self._generate_summary(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        print(summary)

        return returncode == 0

    def _print_styled_header(self):
        """Print a styled header for the test runner."""
        print("\n" + "╔" + "═" * 58 + "╗")
        print("║" + " " * 18 + "🧪 TEST RUNNER" + " " * 18 + "║")
        print("╚" + "═" * 58 + "╝")

    def _print_section_header(self, title, color="WHITE"):
        """Print a styled section header."""
        print(f"\n{'─' * 60}")
        print(f"🔸 {title}")
        print("─" * 60)

    def _get_file_icon(self, filename):
        """Get appropriate icon for file type."""
        icons = {
            "success.txt": "✅",
            "failed.txt": "❌",
            "skipped.txt": "⏭️",
            "errors.txt": "💥",
            "warnings.txt": "⚠️",
            "summary.txt": "📊",
            "full_output.txt": "📄",
            "index.html": "🌐",
        }
        return icons.get(filename, "📁")

    def _print_command_info(self, cmd, test_target, coverage):
        """Print styled command information."""
        print("\n🔧 Test Configuration:")
        print("┌" + "─" * 58 + "┐")

        # Target info
        if test_target:
            if test_target.endswith(".py"):
                print(f"│ 📄 Target File: {test_target:<42} │")
            elif "::" in test_target:
                print(f"│ 🎯 Target Test: {test_target:<42} │")
            else:
                print(f"│ 🔍 Pattern: {test_target:<46} │")
        else:
            print(f"│ 🌐 Target: All tests{' ' * 38} │")

        # Coverage info
        if coverage:
            print(f"│ 📊 Coverage: Enabled{' ' * 40} │")

        # Command info
        cmd_str = " ".join(cmd)
        if len(cmd_str) > 54:
            cmd_str = cmd_str[:51] + "..."
        print(f"│ ⚙️  Command: {cmd_str:<45} │")

        print("└" + "─" * 58 + "┘")
        print("\n🚀 Executing tests...\n")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Run tests and organize results into separate files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python test_runner.py                      # Run all tests
  python test_runner.py test_creditcard.py   # Run specific test file
  python test_runner.py TestCrypto           # Run specific test class
  python test_runner.py test_validate        # Run tests matching pattern
  python test_runner.py --coverage           # Run with coverage report
        """,
    )

    parser.add_argument(
        "test_target",
        nargs="?",
        help="Specific test file, class, or pattern to run (optional)",
    )

    parser.add_argument(
        "--coverage", "-c", action="store_true", help="Run tests with coverage report"
    )

    parser.add_argument(
        "--quiet",
        "-q",
        action="store_true",
        help="Run tests in quiet mode (less verbose)",
    )

    args = parser.parse_args()

    # Create and run test runner
    runner = TestRunner()
    success = runner.run_and_parse(
        test_target=args.test_target, verbose=not args.quiet, coverage=args.coverage
    )

    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
