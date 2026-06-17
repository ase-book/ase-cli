"""Unit tests for test-traceability and test-coverage checkers."""

from pathlib import Path

import pytest

from iec_cli.check import Registry, Status
from iec_cli.checkers import test_coverage, test_traceability


def _write_spec(base: Path, name: str, content: str) -> Path:
    spec_file = base / "openspec" / "specs" / name / "spec.md"
    spec_file.parent.mkdir(parents=True, exist_ok=True)
    spec_file.write_text(content)
    return spec_file


def _write_test(base: Path, name: str, content: str) -> Path:
    test_file = base / "tests" / name
    test_file.parent.mkdir(parents=True, exist_ok=True)
    test_file.write_text(content)
    return test_file


# ---------------------------------------------------------------------------
# Marker fixture builders
#
# The traceability checker scans every file under tests/ for marker patterns,
# including this one. Building marker strings dynamically keeps the literal
# pattern (e.g. the pytest mark.ac decorator with a quoted ID) out of this
# file's source, so the FOO-/BAR- fixture IDs do not leak as orphaned markers
# when `iec check` runs against this repo.
# ---------------------------------------------------------------------------


def _pytest_ac(ac_id: str, func: str = "test_it") -> str:
    return f'@pytest.mark.ac("{ac_id}")\ndef {func}(): pass\n'


def _junit_ac(ac_id: str) -> str:
    return f'@Tag("{ac_id}")\nvoid test() {{}}\n'


def _cucumber_ac(ac_id: str) -> str:
    return f"@AC:{ac_id}\nScenario: ...\n"


def _inline_ac(ac_id: str) -> str:
    return f"// AC: {ac_id}\ndef test_it(): pass\n"


# ---------------------------------------------------------------------------
# Spec fixtures
# ---------------------------------------------------------------------------

_SPEC_ONE_AC = """\
#### Scenario: Happy path [FOO-001]

Test-type: Unit

- **WHEN** something
- **THEN** result
"""

_SPEC_MANUAL_AC = """\
#### Scenario: Manual check [FOO-002]

Test-type: Manual

- **WHEN** something
- **THEN** result
"""

_SPEC_TWO_ACS = """\
#### Scenario: First [FOO-001]

Test-type: Unit

- **WHEN** first
- **THEN** result

#### Scenario: Second [FOO-002]

Test-type: Unit

- **WHEN** second
- **THEN** result
"""

_PYTEST_FOO_001 = _pytest_ac("FOO-001")

# ---------------------------------------------------------------------------
# test-traceability
# ---------------------------------------------------------------------------


@pytest.mark.unit
@pytest.mark.ac("TRTC-001")
def test_traceability_no_spec_files(tmp_path: Path) -> None:
    """Covers: TRTC-001"""
    result = test_traceability.TestTraceability().check(tmp_path)
    assert result.status == Status.PASS


@pytest.mark.unit
@pytest.mark.ac("TRTC-002")
def test_traceability_all_covered(tmp_path: Path) -> None:
    """Covers: TRTC-002"""
    _write_spec(tmp_path, "my-spec", _SPEC_ONE_AC)
    _write_test(tmp_path, "test_foo.py", _PYTEST_FOO_001)
    result = test_traceability.TestTraceability().check(tmp_path)
    assert result.status == Status.PASS


@pytest.mark.unit
@pytest.mark.ac("TRTC-003")
def test_traceability_missing_marker(tmp_path: Path) -> None:
    """Covers: TRTC-003"""
    _write_spec(tmp_path, "my-spec", _SPEC_ONE_AC)
    result = test_traceability.TestTraceability().check(tmp_path)
    assert result.status == Status.FAIL
    assert "FOO-001" in result.message


@pytest.mark.unit
@pytest.mark.ac("TRTC-004")
def test_traceability_multiple_missing(tmp_path: Path) -> None:
    """Covers: TRTC-004"""
    _write_spec(tmp_path, "my-spec", _SPEC_TWO_ACS)
    result = test_traceability.TestTraceability().check(tmp_path)
    assert result.status == Status.FAIL
    assert "FOO-001" in result.message
    assert "FOO-002" in result.message


@pytest.mark.unit
def test_traceability_manual_exempt(tmp_path: Path) -> None:
    """Covers: TRTC-005"""
    _write_spec(tmp_path, "my-spec", _SPEC_MANUAL_AC)
    result = test_traceability.TestTraceability().check(tmp_path)
    assert result.status == Status.PASS


@pytest.mark.unit
@pytest.mark.ac("TRTC-006")
def test_traceability_pytest_marker(tmp_path: Path) -> None:
    """Covers: TRTC-006"""
    _write_spec(tmp_path, "my-spec", _SPEC_ONE_AC)
    _write_test(tmp_path, "test_foo.py", _PYTEST_FOO_001)
    result = test_traceability.TestTraceability().check(tmp_path)
    assert result.status == Status.PASS


@pytest.mark.unit
@pytest.mark.ac("TRTC-007")
def test_traceability_junit_tag(tmp_path: Path) -> None:
    """Covers: TRTC-007"""
    _write_spec(tmp_path, "my-spec", _SPEC_ONE_AC)
    _write_test(tmp_path, "FooTest.java", _junit_ac("FOO-001"))
    result = test_traceability.TestTraceability().check(tmp_path)
    assert result.status == Status.PASS


@pytest.mark.unit
@pytest.mark.ac("TRTC-008")
def test_traceability_cucumber_tag(tmp_path: Path) -> None:
    """Covers: TRTC-008"""
    _write_spec(tmp_path, "my-spec", _SPEC_ONE_AC)
    _write_test(tmp_path, "foo.feature", _cucumber_ac("FOO-001"))
    result = test_traceability.TestTraceability().check(tmp_path)
    assert result.status == Status.PASS


@pytest.mark.unit
@pytest.mark.ac("TRTC-009")
def test_traceability_inline_comment(tmp_path: Path) -> None:
    """Covers: TRTC-009"""
    _write_spec(tmp_path, "my-spec", _SPEC_ONE_AC)
    _write_test(tmp_path, "test_foo.py", _inline_ac("FOO-001"))
    result = test_traceability.TestTraceability().check(tmp_path)
    assert result.status == Status.PASS


@pytest.mark.unit
@pytest.mark.ac("TRTC-010")
def test_traceability_orphaned_marker(tmp_path: Path) -> None:
    """Covers: TRTC-010"""
    _write_spec(tmp_path, "my-spec", _SPEC_ONE_AC)
    _write_test(
        tmp_path,
        "test_foo.py",
        _pytest_ac("FOO-001") + _pytest_ac("BAR-999", func="test_orphan"),
    )
    result = test_traceability.TestTraceability().check(tmp_path)
    assert result.status == Status.WARN
    assert "BAR-999" in result.message


@pytest.mark.unit
@pytest.mark.ac("TRTC-011")
def test_traceability_registered() -> None:
    """Covers: TRTC-011"""
    reg = Registry()
    reg.register(test_traceability.TestTraceability)
    assert "test-traceability" in [c[0] for c in reg.list_all()]


# ---------------------------------------------------------------------------
# test-coverage
# ---------------------------------------------------------------------------


@pytest.mark.unit
@pytest.mark.ac("TCOV-001")
def test_coverage_no_spec_files(tmp_path: Path) -> None:
    """Covers: TCOV-001"""
    result = test_coverage.TestCoverage().check(tmp_path)
    assert result.status == Status.PASS


@pytest.mark.unit
@pytest.mark.ac("TCOV-002")
def test_coverage_all_have_two_markers(tmp_path: Path) -> None:
    """Covers: TCOV-002"""
    _write_spec(tmp_path, "my-spec", _SPEC_ONE_AC)
    _write_test(tmp_path, "test_positive.py", _PYTEST_FOO_001)
    _write_test(tmp_path, "test_negative.py", _PYTEST_FOO_001)
    result = test_coverage.TestCoverage().check(tmp_path)
    assert result.status == Status.PASS


@pytest.mark.unit
@pytest.mark.ac("TCOV-003")
def test_coverage_single_marker_warns(tmp_path: Path) -> None:
    """Covers: TCOV-003"""
    _write_spec(tmp_path, "my-spec", _SPEC_ONE_AC)
    _write_test(tmp_path, "test_foo.py", _PYTEST_FOO_001)
    result = test_coverage.TestCoverage().check(tmp_path)
    assert result.status == Status.WARN
    assert "FOO-001" in result.message


@pytest.mark.unit
@pytest.mark.ac("TCOV-004")
def test_coverage_multiple_under_covered(tmp_path: Path) -> None:
    """Covers: TCOV-004"""
    _write_spec(tmp_path, "my-spec", _SPEC_TWO_ACS)
    _write_test(
        tmp_path,
        "test_foo.py",
        _pytest_ac("FOO-001", func="test_a") + _pytest_ac("FOO-002", func="test_b"),
    )
    result = test_coverage.TestCoverage().check(tmp_path)
    assert result.status == Status.WARN
    assert "FOO-001" in result.message
    assert "FOO-002" in result.message


@pytest.mark.unit
def test_coverage_manual_exempt(tmp_path: Path) -> None:
    """Covers: TCOV-005"""
    _write_spec(tmp_path, "my-spec", _SPEC_MANUAL_AC)
    result = test_coverage.TestCoverage().check(tmp_path)
    assert result.status == Status.PASS


@pytest.mark.unit
@pytest.mark.ac("TCOV-006")
def test_coverage_zero_markers_warns_with_count(tmp_path: Path) -> None:
    """Covers: TCOV-006 — AC with 0 markers shows (0) in WARN message."""
    _write_spec(tmp_path, "my-spec", _SPEC_ONE_AC)
    result = test_coverage.TestCoverage().check(tmp_path)
    assert result.status == Status.WARN
    assert "FOO-001" in result.message
    assert "(0)" in result.message


@pytest.mark.unit
@pytest.mark.ac("TCOV-007")
def test_coverage_registered() -> None:
    """Covers: TCOV-007"""
    reg = Registry()
    reg.register(test_coverage.TestCoverage)
    assert "test-coverage" in [c[0] for c in reg.list_all()]
