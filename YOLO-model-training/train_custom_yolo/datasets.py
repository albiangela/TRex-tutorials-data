"""Dataset source helpers and simple CLI-style prompts."""

from __future__ import annotations

import asyncio
import importlib
import os
import re
import shutil
import subprocess
import tempfile
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import Literal, Optional, Union
import sys

_DEFAULT_ROOT = Path("/content/datasets")
_EXAMPLE_REPO = "https://github.com/albiangela/TRex-tutorials-data.git"
_EXAMPLE_SUBDIR = Path("YOLO-models/hexbugs-annotation-dataset")
_EXAMPLE_TARGET_NAME = "example_dataset"


@dataclass
class DriveSource:
    """Google Drive ZIP dataset referenced by shareable link or file id."""

    file_id: str
    name_hint: Optional[str] = None
    unzip: bool = True

    kind: Literal["google_drive"] = "google_drive"


@dataclass
class RoboflowSource:
    """Roboflow dataset described by the standard download snippet."""

    api_key: str
    workspace: str
    project: str
    version: int
    data_format: str = "yolov8"

    kind: Literal["roboflow"] = "roboflow"


@dataclass
class ExampleSource:
    """Built-in GitHub example dataset."""

    dataset_name: str = _EXAMPLE_TARGET_NAME

    kind: Literal["example"] = "example"


DatasetSource = Union[DriveSource, RoboflowSource, ExampleSource]


def _detect_dataset_dir(root: Path) -> Path:
    """Pick the newest sub-folder inside root."""
    candidates = [p for p in root.iterdir() if p.is_dir() and not p.name.startswith("__")]
    if not candidates:
        candidates = [p for p in root.iterdir() if p.is_dir()]
    if not candidates:
        contents = [p.name for p in root.iterdir()] if root.exists() else []
        raise RuntimeError(f"No dataset folders found under {root}. Contents: {contents}")
    return max(candidates, key=lambda p: p.stat().st_mtime)


def _ensure_package(module: str, install_name: Optional[str] = None) -> None:
    """Ensure a Python package is available, installing it if necessary."""
    try:
        importlib.import_module(module)
    except ImportError:
        package = install_name or module
        print(f"📦 Installing {package} …")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])


def _extract_drive_file_id(link: str) -> Optional[str]:
    """Extract a Google Drive file id from a shareable link or raw id."""
    link = link.strip()
    if not link:
        return None
    if "/" not in link and len(link) >= 10:
        return link  # looks like a bare id

    patterns = [
        r"id=([0-9A-Za-z_-]{10,})",
        r"/d/([0-9A-Za-z_-]{10,})/",
        r"/file/d/([0-9A-Za-z_-]{10,})",
    ]
    for pat in patterns:
        match = re.search(pat, link)
        if match:
            return match.group(1)
    return None


def _parse_roboflow_snippet(snippet: str) -> dict:
    """Parse the standard Roboflow download snippet into its components."""
    api_key_match = re.search(r"api_key\s*=\s*['\"]([^'\"]+)['\"]", snippet)
    workspace_match = re.search(r"workspace\(['\"]([^'\"]+)['\"]\)", snippet)
    project_match = re.search(r"project\(['\"]([^'\"]+)['\"]\)", snippet)
    version_match = re.search(r"version\((\d+)\)", snippet)
    format_match = re.search(r"download\(['\"]([^'\"]+)['\"]\)", snippet)

    missing = []
    if not api_key_match:
        missing.append("api_key")
    if not workspace_match:
        missing.append("workspace")
    if not project_match:
        missing.append("project")
    if not version_match:
        missing.append("version")
    if not format_match:
        missing.append("download format")

    if missing:
        raise ValueError(
            "Could not parse the Roboflow snippet. Missing: " + ", ".join(missing)
        )

    return {
        "api_key": api_key_match.group(1),
        "workspace": workspace_match.group(1),
        "project": project_match.group(1),
        "version": int(version_match.group(1)),
        "data_format": format_match.group(1),
    }




def _sanitize_dataset_name(name: str) -> str:
    """Turn dataset name into a filesystem-friendly string."""
    cleaned = re.sub(r'[^\w.-]+', '_', name.strip())
    cleaned = cleaned.strip('._')
    return cleaned or 'dataset'


def _infer_dataset_name_from_zip(zip_path: Path, fallback: str) -> str:
    """Inspect zip contents to guess a dataset folder name."""
    try:
        with zipfile.ZipFile(zip_path, 'r') as archive:
            top_level = set()
            for name in archive.namelist():
                if not name:
                    continue
                parts = Path(name).parts
                if not parts:
                    continue
                top = parts[0].strip("/\\")
                if top and top not in {'.', ''}:
                    top_level.add(top)
            if len(top_level) == 1:
                candidate = top_level.pop()
                if candidate.lower() not in {'train', 'valid', 'test', 'images', 'labels'}:
                    return _sanitize_dataset_name(candidate)
    except Exception:
        pass
    return _sanitize_dataset_name(fallback)

def _resolve_dataset_dir(root: Path, preferred_name: str | None = None) -> Path:
    """Determine dataset root directory, extracting archives when necessary."""
    if not root.exists():
        raise RuntimeError(f"Dataset path {root} does not exist after download.")

    split_dirs = {"train", "valid", "test", "images", "labels"}
    root_entries = {p.name for p in root.iterdir()}
    if split_dirs & root_entries:
        dataset_name = _sanitize_dataset_name(preferred_name or "dataset")
        dataset_dir = root / dataset_name if dataset_name != root.name else root
        if dataset_dir.exists() and not dataset_dir.is_dir():
            raise RuntimeError(f"Target dataset path {dataset_dir} exists and is not a directory.")
        if dataset_dir != root:
            dataset_dir.mkdir(exist_ok=True)
        for entry in list(root.iterdir()):
            if entry == dataset_dir or entry.suffix == ".zip":
                continue
            target_path = dataset_dir / entry.name
            if target_path.exists():
                if target_path.is_dir():
                    shutil.rmtree(target_path)
                else:
                    target_path.unlink()
            shutil.move(str(entry), target_path)
        return dataset_dir

    try:
        return _detect_dataset_dir(root)
    except RuntimeError:
        zip_candidates = sorted(
            [p for p in root.glob("*.zip") if p.is_file()],
            key=lambda p: p.stat().st_mtime,
            reverse=True,
        )
        if zip_candidates:
            zip_path = zip_candidates[0]
            print(f"📦 Extracting archive {zip_path.name} …")
            with zipfile.ZipFile(zip_path, "r") as archive:
                archive.extractall(root)
            try:
                zip_path.unlink(missing_ok=True)
            except Exception:
                pass
            candidates = [p for p in root.iterdir() if p.is_dir()]
            if len(candidates) == 1:
                inner = candidates[0]
                inner_entries = {child.name for child in inner.iterdir()}
                if split_dirs & inner_entries:
                    return inner
            return _resolve_dataset_dir(root, preferred_name=preferred_name)
        contents = [p.name for p in root.iterdir()] if root.exists() else []
        raise RuntimeError(f"No dataset folders found under {root}. Contents: {contents}")
def fetch_dataset(
    source: DatasetSource,
    *,
    dataset_root: Path | str = _DEFAULT_ROOT,
    clean: bool = True,
) -> Path:
    """Resolve the given dataset source and return the prepared folder."""
    root = Path(dataset_root)
    if clean:
        shutil.rmtree(root, ignore_errors=True)
    root.mkdir(parents=True, exist_ok=True)

    if isinstance(source, DriveSource):
        _ensure_package("gdown")
        import gdown  # type: ignore

        url = f"https://drive.google.com/uc?id={source.file_id}"
        sanitized_hint = _sanitize_dataset_name(source.name_hint) if source.name_hint else None
        zip_basename = sanitized_hint or "dataset"
        output_path = root / f"{zip_basename}.zip"
        download_path_str = gdown.download(url, str(output_path), quiet=False)
        if not download_path_str:
            raise RuntimeError("Failed to download archive from Google Drive.")
        downloaded_path = Path(download_path_str)
        if not downloaded_path.exists():
            raise RuntimeError(f"Downloaded file {downloaded_path} is missing.")
        if downloaded_path.parent != root:
            destination = root / downloaded_path.name
            shutil.move(str(downloaded_path), destination)
            downloaded_path = destination

        if source.unzip:
            temp_zip = downloaded_path
            if temp_zip.suffix.lower() != ".zip":
                raise ValueError("Expected a .zip archive from Google Drive when unzip=True.")
            if sanitized_hint and temp_zip.stem != sanitized_hint:
                desired_zip = temp_zip.with_name(f"{sanitized_hint}{temp_zip.suffix}")
                temp_zip.rename(desired_zip)
                temp_zip = desired_zip
            preferred_name = sanitized_hint or _infer_dataset_name_from_zip(temp_zip, fallback=temp_zip.stem)
            print("📂 Extracting archive …")
            with zipfile.ZipFile(temp_zip, "r") as archive:
                archive.extractall(root)
            temp_zip.unlink(missing_ok=True)
            dataset_dir = _resolve_dataset_dir(root, preferred_name=preferred_name)
        else:
            dataset_dir = downloaded_path
            if sanitized_hint and downloaded_path.stem != sanitized_hint:
                desired = downloaded_path.with_name(f"{sanitized_hint}{downloaded_path.suffix}")
                downloaded_path.rename(desired)
                dataset_dir = desired

    elif isinstance(source, RoboflowSource):
        _ensure_package("roboflow")
        from roboflow import Roboflow  # type: ignore

        print("🤖 Downloading dataset from Roboflow …")
        rf = Roboflow(api_key=source.api_key)
        workspace = rf.workspace(source.workspace)
        project = workspace.project(source.project)
        version = project.version(source.version)
        download_obj = version.download(source.data_format)
        print(f"[roboflow] download result type: {type(download_obj).__name__}")

        candidate = getattr(download_obj, "location", None) or getattr(download_obj, "path", None) or download_obj
        if not isinstance(candidate, (str, os.PathLike)):
            raise RuntimeError("Roboflow download did not return a filesystem path.")
        downloaded_dir = Path(candidate)
        if not downloaded_dir.exists():
            raise RuntimeError(f"Roboflow reported dataset at {downloaded_dir}, but it was not found.")

        target_name = _sanitize_dataset_name(source.project)
        target_dir = root / target_name
        if target_dir.exists():
            shutil.rmtree(target_dir)
        shutil.move(str(downloaded_dir), target_dir)
        dataset_dir = target_dir
    elif isinstance(source, ExampleSource):
        print("📚 Fetching example dataset from GitHub …")
        tmp_dir = Path(tempfile.mkdtemp(prefix="example_repo_"))
        clone_dir = tmp_dir / "repo"
        subprocess.run(["git", "clone", _EXAMPLE_REPO, str(clone_dir)], check=True)
        src_dataset = clone_dir / _EXAMPLE_SUBDIR
        if not src_dataset.exists():
            raise FileNotFoundError(
                f"Expected example dataset at {_EXAMPLE_SUBDIR}, but it was not found."
            )
        target = root / source.dataset_name
        shutil.rmtree(target, ignore_errors=True)
        shutil.copytree(src_dataset, target)
        dataset_dir = target
        shutil.rmtree(tmp_dir, ignore_errors=True)

    else:  # pragma: no cover
        raise ValueError(f"Unsupported dataset source: {source}")

    print(f"✅ Dataset ready at: {dataset_dir}")
    return dataset_dir


def prompt_for_dataset(config: dict | None = None) -> DatasetSource:
    """Gather dataset source configuration via optional config or CLI prompts."""
    config = config or {}
    choice = config.get("choice")

    if choice is None:
        print("Select dataset source:")
        print("  [1] Paste Roboflow download snippet")
        print("  [2] Paste Google Drive link (.zip)")
        print("  [3] Use example dataset from TRex tutorials repo")

        while True:
            choice = input("Enter choice (1/2/3): ").strip()
            if choice in {"1", "2", "3"}:
                break
            print("⚠️ Please enter 1, 2, or 3.")

    if str(choice).lower() in {"1", "roboflow"}:
        snippet = config.get("roboflow_snippet")
        if not snippet:
            print("Paste your Roboflow snippet (finish with an empty line):")
            lines: list[str] = []
            while True:
                line = input()
                if not line.strip():
                    break
                lines.append(line)
            snippet = "\n".join(lines).strip()
        if not snippet:
            raise ValueError("Roboflow snippet cannot be empty.")
        parsed = _parse_roboflow_snippet(snippet)
        source: DatasetSource = RoboflowSource(**parsed)
    elif str(choice).lower() in {"2", "drive", "google_drive"}:
        link = config.get("drive_link")
        if not link:
            link = input("Paste the Google Drive link or file id: ").strip()
        file_id = _extract_drive_file_id(link or "")
        if not file_id:
            raise ValueError("Could not extract a file id from the provided link.")
        source = DriveSource(file_id=file_id)
    elif str(choice).lower() in {"3", "example"}:
        source = ExampleSource()
    else:
        raise ValueError(f"Unsupported dataset source choice: {choice}")

    print(f"✔️ Using {source.kind} dataset source.")
    return source


def launch_dataset_selector(
    target_globals: dict | None = None,
    *,
    dataset_root: Path | str = _DEFAULT_ROOT,
) -> None:
    """Render an interactive widget to choose and fetch a dataset."""
    try:
        import ipywidgets as widgets  # type: ignore
        from IPython.display import display  # type: ignore
    except ImportError as exc:  # pragma: no cover
        raise ImportError("ipywidgets is required for launch_dataset_selector.") from exc

    target_globals = target_globals if target_globals is not None else {}
    root_path = Path(dataset_root)

    style = {"description_width": "120px"}
    layout_full = widgets.Layout(width="100%")

    source_dropdown = widgets.Dropdown(
        options=(
            ("Roboflow snippet", "roboflow"),
            ("Google Drive link", "drive"),
            ("Example dataset", "example"),
        ),
        value="roboflow",
        description="Source:",
        style=style,
    )

    snippet_area = widgets.Textarea(
        description="Snippet:",
        placeholder="Paste the full Roboflow download snippet here…",
        layout=widgets.Layout(width="100%", height="220px"),
        style=style,
    )

    snippet_help = widgets.HTML(
        "<small>Tip: Paste the lines that include <code>api_key</code>, "
        "<code>workspace()</code>, <code>project()</code>, <code>version()</code>, "
        "and <code>download()</code>.</small>"
    )
    roboflow_box = widgets.VBox([snippet_area, snippet_help])

    drive_input = widgets.Text(
        description="Link:",
        placeholder="https://drive.google.com/file/d/…",
        layout=layout_full,
        style=style,
    )
    drive_name_input = widgets.Text(
        description="Dataset name:",
        placeholder="Optional folder name",
        layout=layout_full,
        style=style,
    )
    drive_help = widgets.HTML(
        "<small>Accepts a full shareable link or just the file id."
        " Leave blank to keep the zip name."
        "</small>"
    )
    drive_box = widgets.VBox([drive_input, drive_name_input, drive_help])

    example_box = widgets.HTML(
        "The example dataset will be downloaded from "
        "<code>albiangela/TREx-tutorials-data</code>."
    )

    forms = {
        "roboflow": roboflow_box,
        "drive": drive_box,
        "example": example_box,
    }

    for box in forms.values():
        box.layout.display = "none"

    action_btn = widgets.Button(
        description="Download dataset",
        button_style="primary",
        icon="download",
    )
    status = widgets.Output()

    def _show_form(kind: str) -> None:
        for key, box in forms.items():
            is_box = isinstance(box, widgets.Box)
            show_display = "flex" if is_box else "block"
            box.layout.display = show_display if key == kind else "none"

    _show_form(source_dropdown.value)

    def _on_source_change(change):
        _show_form(change["new"])
        with status:
            status.clear_output()

    source_dropdown.observe(_on_source_change, names="value")

    def _handle_click(_button):
        with status:
            status.clear_output()
            try:
                if source_dropdown.value == "roboflow":
                    snippet = snippet_area.value.strip()
                    if not snippet:
                        raise ValueError("Paste the Roboflow snippet into the text area.")
                    parsed = _parse_roboflow_snippet(snippet)
                    source = RoboflowSource(**parsed)
                elif source_dropdown.value == "drive":
                    link = drive_input.value.strip()
                    if not link:
                        raise ValueError("Provide the Google Drive link or file id.")
                    file_id = _extract_drive_file_id(link)
                    if not file_id:
                        raise ValueError("Could not extract a file id from the provided link.")
                    dataset_name = drive_name_input.value.strip() or None
                    source = DriveSource(file_id=file_id, name_hint=dataset_name)
                else:
                    source = ExampleSource()

                dataset_path = fetch_dataset(source, dataset_root=root_path)
            except Exception as exc:
                print(f"⚠️ {exc}")
            else:
                if target_globals is not None:
                    target_globals["dataset_path"] = dataset_path
                    target_globals["name"] = dataset_path.name
                    target_globals["DATASET_SOURCE"] = source
                    target_globals["DATASET_ROOT"] = root_path
                print(f"✅ Dataset ready at: {dataset_path}")
                print(f"   Variable `name` set to '{dataset_path.name}'.")

    action_btn.on_click(_handle_click)

    container = widgets.VBox(
        [
            source_dropdown,
            roboflow_box,
            drive_box,
            example_box,
            action_btn,
            status,
        ]
    )

    display(container)


class DatasetSelector:
    """Async ipywidgets helper that gathers dataset source configuration."""

    _VALID_DEFAULTS = {"roboflow", "drive", "example"}

    def __init__(
        self,
        *,
        default_source: str = "roboflow",
        dataset_root: Path | str = _DEFAULT_ROOT,
    ) -> None:
        try:
            import ipywidgets as widgets  # type: ignore
            from IPython.display import display  # type: ignore
        except ImportError as exc:  # pragma: no cover
            raise ImportError("ipywidgets is required for DatasetSelector.") from exc

        self._widgets = widgets
        self._display = display
        self.dataset_root = Path(dataset_root)
        self._default_source = default_source if default_source in self._VALID_DEFAULTS else "roboflow"
        self._future: asyncio.Future[DatasetSource] | None = None
        self.last_source: DatasetSource | None = None
        self._build_ui()

    async def interact(self) -> DatasetSource:
        """Render the widget and wait for the user to choose a source."""
        if self._future and not self._future.done():
            raise RuntimeError("An interaction is already in progress.")

        loop = asyncio.get_running_loop()
        self._future = loop.create_future()

        self._reset_status()
        self._enable_controls()
        self._display(self._container)
        return await self._future

    # ------------------------------------------------------------------ #
    # Private helpers
    # ------------------------------------------------------------------ #
    def _build_ui(self) -> None:
        widgets = self._widgets

        style = {"description_width": "120px"}
        layout_full = widgets.Layout(width="100%")

        self._source_dropdown = widgets.Dropdown(
            options=(
                ("Roboflow snippet", "roboflow"),
                ("Google Drive link", "drive"),
                ("Example dataset", "example"),
            ),
            value=self._default_source,
            description="Source:",
            style=style,
        )

        self._snippet_area = widgets.Textarea(
            description="Snippet:",
            placeholder="Paste the full Roboflow download snippet here…",
            layout=widgets.Layout(width="100%", height="220px"),
            style=style,
        )
        snippet_help = widgets.HTML(
            "<small>Tip: Paste the lines that include <code>api_key</code>, "
            "<code>workspace()</code>, <code>project()</code>, <code>version()</code>, "
            "and <code>download()</code>.</small>"
        )
        roboflow_box = widgets.VBox([self._snippet_area, snippet_help])

        self._drive_input = widgets.Text(
            description="Link:",
            placeholder="https://drive.google.com/file/d/…",
            layout=layout_full,
            style=style,
        )
        self._drive_name_input = widgets.Text(
            description="Dataset name:",
            placeholder="Optional folder name",
            layout=layout_full,
            style=style,
        )
        drive_help = widgets.HTML(
            "<small>Accepts a full shareable link or just the file id."
            " Leave blank to keep the zip name."
            "</small>"
        )
        drive_box = widgets.VBox([self._drive_input, self._drive_name_input, drive_help])

        example_box = widgets.HTML(
            "The example dataset will be downloaded from "
            "<code>albiangela/TREx-tutorials-data</code>."
        )

        self._forms: dict[str, widgets.Widget] = {
            "roboflow": roboflow_box,
            "drive": drive_box,
            "example": example_box,
        }

        for box in self._forms.values():
            box.layout.display = "none"

        self._action_btn = widgets.Button(
            description="Use this source",
            button_style="success",
            icon="check",
        )
        self._status = widgets.Output()

        self._source_dropdown.observe(self._on_source_change, names="value")
        self._action_btn.on_click(self._handle_click)

        self._container = widgets.VBox(
            [
                widgets.HTML("Select a dataset source and click <b>Use this source</b> to continue."),
                self._source_dropdown,
                roboflow_box,
                drive_box,
                example_box,
                self._action_btn,
                self._status,
            ]
        )

        # Show default form
        self._show_form(self._source_dropdown.value)

    def _on_source_change(self, change) -> None:
        self._show_form(change["new"])
        self._reset_status()

    def _show_form(self, kind: str) -> None:
        for key, box in self._forms.items():
            is_box = isinstance(box, self._widgets.Box)
            show_display = "flex" if is_box else "block"
            box.layout.display = show_display if key == kind else "none"

    def _reset_status(self) -> None:
        with self._status:
            self._status.clear_output()

    def _enable_controls(self) -> None:
        self._action_btn.disabled = False
        self._source_dropdown.disabled = False

    def _handle_click(self, _button) -> None:
        if not self._future or self._future.done():
            return

        with self._status:
            self._status.clear_output()
            try:
                source = self._parse_current_source()
            except Exception as exc:  # noqa: BLE001
                print(f"⚠️ {exc}")
                return

            self.last_source = source
            if not self._future.done():
                self._future.set_result(source)
            print(f"✔️ {source.kind.capitalize()} source selected.")
            self._action_btn.disabled = True
            self._source_dropdown.disabled = True

    def _parse_current_source(self) -> DatasetSource:
        choice = self._source_dropdown.value
        if choice == "roboflow":
            snippet = self._snippet_area.value.strip()
            if not snippet:
                raise ValueError("Paste the Roboflow snippet into the text area.")
            parsed = _parse_roboflow_snippet(snippet)
            return RoboflowSource(**parsed)
        if choice == "drive":
            link = self._drive_input.value.strip()
            if not link:
                raise ValueError("Provide the Google Drive link or file id.")
            file_id = _extract_drive_file_id(link)
            if not file_id:
                raise ValueError("Could not extract a file id from the provided link.")
            name_hint = self._drive_name_input.value.strip() or None
            return DriveSource(file_id=file_id, name_hint=name_hint)
        return ExampleSource()


__all__ = [
    "DatasetSource",
    "DatasetSelector",
    "DriveSource",
    "ExampleSource",
    "RoboflowSource",
    "fetch_dataset",
    "prompt_for_dataset",
    "launch_dataset_selector",
]
