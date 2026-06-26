"""Dependency-free test runner with real line-coverage measurement.

We avoid pytest/coverage (not installed) by:
  * executing the generated test functions directly, and
  * measuring line coverage of the generated module with the stdlib `trace`.

Coverage is computed over executable statements inside function bodies (the
logic that runs when the code is exercised), which is a faithful proxy for
line coverage without any third-party tooling.
"""

from __future__ import annotations

import ast
import importlib.util
import os
import sys
import trace
from typing import Dict, List, Tuple

from .models import TestReport, TestResult


def _executable_lines(source: str) -> set:
    """Return line numbers of statements inside function bodies (excludes
    def headers, imports, module-level code, and docstrings)."""
    tree = ast.parse(source)
    lines = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            body = list(node.body)
            if (
                body
                and isinstance(body[0], ast.Expr)
                and isinstance(getattr(body[0], "value", None), ast.Constant)
                and isinstance(body[0].value.value, str)
            ):
                body = body[1:]  # skip docstring
            for stmt in body:
                for sub in ast.walk(stmt):
                    if isinstance(sub, ast.stmt):
                        lines.add(sub.lineno)
    return lines


def _load_module(path: str):
    spec = importlib.util.spec_from_file_location("solution", path)
    module = importlib.util.module_from_spec(spec)
    sys.modules["solution"] = module
    spec.loader.exec_module(module)
    return module


def run_suite(
    generated_source: str,
    test_source: str,
    run_dir: str,
    criterion_map: Dict[str, str],
) -> TestReport:
    """Write the module + tests to run_dir, execute the tests under coverage
    tracing, and return a TestReport with pass/fail counts and coverage %."""
    os.makedirs(run_dir, exist_ok=True)
    sol_path = os.path.join(run_dir, "solution.py")
    test_path = os.path.join(run_dir, "test_solution.py")
    with open(sol_path, "w") as fh:
        fh.write(generated_source)
    with open(test_path, "w") as fh:
        fh.write(test_source)

    module = _load_module(sol_path)

    namespace = {"solution": module}
    exec(compile(test_source, test_path, "exec"), namespace)
    tests = {
        name: fn
        for name, fn in namespace.items()
        if name.startswith("test_") and callable(fn)
    }

    tracer = trace.Trace(count=1, trace=0, countfuncs=0, countcallers=0)
    results: List[TestResult] = []
    passed = failed = 0
    for name in sorted(tests):
        criterion_id = criterion_map.get(name, name.replace("test_criterion_", ""))
        detail = ""
        try:
            tracer.runfunc(tests[name])
            status = "passed"
            passed += 1
        except Exception as exc:  # noqa: BLE001 - any failure is a test failure
            status = "failed"
            failed += 1
            detail = "%s: %s" % (type(exc).__name__, exc)
        results.append(
            TestResult(criterion_id=criterion_id, name=name, status=status, detail=detail)
        )

    coverage = _measure_coverage(tracer, sol_path, generated_source)
    return TestReport(
        results=tuple(results),
        passed=passed,
        failed=failed,
        coverage_percentage=coverage,
    )


def _measure_coverage(tracer, sol_path: str, source: str) -> float:
    counts = tracer.results().counts  # {(filename, lineno): count}
    target = os.path.abspath(sol_path)
    covered = {
        lineno
        for (filename, lineno), hits in counts.items()
        if hits > 0 and os.path.abspath(filename) == target
    }
    executable = _executable_lines(source)
    if not executable:
        return 100.0
    pct = 100.0 * len(covered & executable) / len(executable)
    return round(pct, 1)
