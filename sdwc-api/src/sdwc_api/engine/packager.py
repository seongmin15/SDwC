"""ZIP packaging for rendered SDwC output.

Assembles rendered templates and .sdwc/ server resources into an in-memory ZIP.
"""

from __future__ import annotations

import io
import zipfile
from pathlib import Path

import structlog

from sdwc_api.schemas.intake import IntakeData

logger = structlog.get_logger()


def build_zip(
    rendered: dict[str, str],
    intake: IntakeData,
    template_dir: Path,
) -> io.BytesIO:
    """Build an in-memory ZIP from rendered output.

    Args:
        rendered: Validated output from render_all() — {output_path: content}.
        intake: Original intake data (for project name as root folder).
        template_dir: Path to .sdwc/ server resources on disk.

    Returns:
        BytesIO containing the ZIP file, seeked to position 0.

    The ZIP structure:
        {project.name}/
        ├── CLAUDE.md
        ├── docs/...
        ├── skills/...
        └── .sdwc/... (raw copies from template_dir)
    """
    root = intake.project.name
    buf = io.BytesIO()

    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        for output_path in sorted(rendered):
            arcname = f"{root}/{output_path}"
            zf.writestr(arcname, rendered[output_path])

        _copy_sdwc_resources(zf, root, template_dir)

    buf.seek(0)
    return buf


def _copy_sdwc_resources(
    zf: zipfile.ZipFile,
    root: str,
    template_dir: Path,
) -> None:
    """Copy .sdwc/ server resources into the ZIP without rendering.

    Per E-5: individual file copy failures log a warning and continue.
    """
    if not template_dir.is_dir():
        logger.warning(
            "sdwc_resource_dir_not_found",
            template_dir=str(template_dir),
        )
        return

    for file_path in sorted(template_dir.rglob("*")):
        if not file_path.is_file():
            continue
        try:
            rel = file_path.relative_to(template_dir).as_posix()
            arcname = f"{root}/.sdwc/{rel}"
            zf.write(file_path, arcname)
        except Exception:
            logger.warning(
                "sdwc_resource_copy_failed",
                file=str(file_path),
                exc_info=True,
            )
