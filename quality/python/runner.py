"""Run repository-owned Python quality rules."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import TYPE_CHECKING
from quality.lib.source import read_python_source
from quality.config.repository.paths import PYTHON_SOURCE_DIRS
from quality.lib.files import git_files, VISIBLE_FILE_ARGUMENTS
from quality.python.rules.records import collect_record_violations
from quality.python.policy import read_import_policy, read_package_policy
from quality.lib.diagnostics import Diagnostic, diagnostic, report_diagnostics
from quality.python.rules.imports import boundary, deferred, exports, graph, layout
from quality.python.rules import (
    logging_use,
    all_at_bottom,
    module_length,
    function_length,
    runtime_singletons,
)

if TYPE_CHECKING:
    from collections.abc import Sequence
    from quality.lib.source import PythonSource


def run_rules(root: Path) -> int:
    """Run all Python rules over one cached source collection."""
    paths = {
        root / name
        for name in git_files(VISIBLE_FILE_ARGUMENTS, root=root, is_existing_required=True)
        if Path(name).suffix in {".py", ".pyi"}
        and any(name == scope or name.startswith(scope + "/") for scope in PYTHON_SOURCE_DIRS)
    }
    sources = tuple(read_python_source(root, path) for path in sorted(paths))
    diagnostics = syntax_diagnostics(sources)
    valid_sources = tuple(source for source in sources if source.tree is not None)
    import_policy = read_import_policy(root)
    package_policy = read_package_policy(root)
    diagnostics.extend(module_length.collect_module_length_violations(valid_sources))
    diagnostics.extend(function_length.collect_function_length_violations(valid_sources))
    diagnostics.extend(collect_record_violations(valid_sources))
    diagnostics.extend(runtime_singletons.collect_singleton_violations(valid_sources))
    diagnostics.extend(deferred.collect_deferred_import_violations(valid_sources))
    diagnostics.extend(all_at_bottom.collect_all_placement_violations(valid_sources))
    diagnostics.extend(logging_use.collect_logging_violations(valid_sources))
    diagnostics.extend(layout.collect_import_layout_diagnostics(valid_sources, import_policy))
    diagnostics.extend(boundary.collect_import_boundary_diagnostics(valid_sources, import_policy, package_policy))
    diagnostics.extend(graph.collect_import_graph_violations(valid_sources))
    diagnostics.extend(exports.collect_package_export_diagnostics(valid_sources, package_policy))
    return report_diagnostics("Python quality violations:", diagnostics)


def syntax_diagnostics(sources: Sequence[PythonSource]) -> list[Diagnostic]:
    """Return one syntax diagnostic for every invalid Python source."""
    errors: list[Diagnostic] = []
    for source in sources:
        error = source.syntax_error
        if error is None:
            continue
        errors.append(
            diagnostic(
                source.relative_path,
                error.lineno or 1,
                "python.syntax",
                error.msg,
            ),
        )
    return errors


def main() -> int:
    """Run Python quality rules."""
    argparse.ArgumentParser().parse_args()
    return run_rules(Path.cwd())


if __name__ == "__main__":
    raise SystemExit(main())
