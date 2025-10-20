"""Utilities for preparing and inspecting YOLO datasets.

These helpers were extracted from the `Train-custom-YOLO-model-personal.ipynb`
notebook so the notebook can stay focused on orchestration and configuration.
The functions here are designed to be importable both inside and outside
Colab environments.
"""

from __future__ import annotations

import math
import os
import random
import shutil
from collections import Counter
from pathlib import Path
from tempfile import mkdtemp
from typing import Dict, Iterable, List, Mapping, Optional, Sequence, Tuple

import yaml

try:  # yolo_tiler is optional; keep imports lazy-friendly.
    from yolo_tiler import TileConfig, TileProgress, YoloTiler
except ImportError:  # pragma: no cover - only triggered when package missing.
    TileConfig = TileProgress = YoloTiler = None  # type: ignore[assignment]


class Data:
    """Container for basic dataset metadata."""

    def __init__(self, location: str, name: str, version: int = 1) -> None:
        self.location = location
        self.version = version
        self.name = name


# --------------------------------------------------------------------------- #
# Label helpers
# --------------------------------------------------------------------------- #

def build_collapse_map(allowed_ids: Iterable[int]) -> Dict[int, int]:
    """
    Create a mapping from original class ids to contiguous indices.

    Parameters
    ----------
    allowed_ids
        Iterable of class ids (from the raw dataset) that you want to keep.
        The smallest id becomes 0, the next smallest becomes 1, etc.

    Notes
    -----
    Use this together with ``new_class_ids`` (name -> new id) so that
    downstream YAML files and YOLO training jobs see a compact set of ids.
    """
    return {old: new for new, old in enumerate(sorted(set(allowed_ids)))}


def filter_labels(pool_dir: str | Path, allowed_ids: set[int]) -> None:
    """Keep only annotations whose class id is in `allowed_ids`."""
    pool_path = Path(pool_dir)
    lbl_dir = pool_path / "labels"
    if not lbl_dir.exists():
        return

    kept_files = dropped_files = 0
    for lp in lbl_dir.glob("*.txt"):
        lines = [ln.strip() for ln in lp.read_text().splitlines() if ln.strip()]
        new_lines = []
        for ln in lines:
            parts = ln.split()
            if not parts:
                continue
            try:
                cid = int(float(parts[0]))
            except Exception:
                continue
            if cid in allowed_ids:
                new_lines.append(ln)
        if new_lines:
            lp.write_text("\n".join(new_lines) + "\n")
            kept_files += 1
        else:
            lp.write_text("")
            dropped_files += 1
    print(f"[filter_labels] files kept(non-empty)={kept_files}, became-empty={dropped_files}")


def simplify_labels(
    dataset_root: str | Path,
    collapse_map: Mapping[int, str],
    new_class_ids: Mapping[str, int],
    drop_others: bool = False,
) -> None:
    """Collapse a YOLO dataset taxonomy to coarser groupings."""
    for subset in ("train", "valid", "test"):
        lbl_dir = Path(dataset_root) / subset / "labels"
        if not lbl_dir.is_dir():
            continue
        for path in lbl_dir.glob("*.txt"):
            out_lines: List[str] = []
            with path.open("r") as src:
                for ln in src:
                    if not ln.strip():
                        continue
                    tok0, *rest = ln.split()
                    if not tok0.replace(".", "", 1).isdigit():
                        if not drop_others:
                            out_lines.append(ln.rstrip())
                        continue
                    try:
                        orig_id = int(float(tok0))
                    except ValueError:
                        if not drop_others:
                            out_lines.append(ln.rstrip())
                        continue
                    if orig_id in collapse_map:
                        new_name = collapse_map[orig_id]
                        if new_name not in new_class_ids:
                            if not drop_others:
                                out_lines.append(ln.rstrip())
                            continue
                        new_id = new_class_ids[new_name]
                        out_lines.append(" ".join([str(new_id), *rest]).strip())
                    elif not drop_others:
                        out_lines.append(ln.rstrip())
            path.write_text("\n".join(out_lines) + ("\n" if out_lines else ""))


def progress_callback(progress: TileProgress) -> None:
    """Pretty-print progress for `yolo_tiler` operations."""
    if progress.total_tiles > 0:
        print(
            f"🧩 {progress.current_image_name} [{progress.current_set_name}] "
            f"tile {progress.current_tile_idx}/{progress.total_tiles}"
        )
    else:
        print(
            f"📂 Scanning {progress.current_image_name} [{progress.current_set_name}] "
            f"{progress.current_image_idx}/{progress.current_total_images}"
        )


def _materialize_empty_labels(base_path: str | Path) -> None:
    """Ensure every image has a corresponding (possibly empty) label file."""
    base = Path(base_path)
    for split in ("train", "valid", "test"):
        images_dir = base / split / "images"
        labels_dir = base / split / "labels"
        if not images_dir.is_dir():
            continue
        labels_dir.mkdir(parents=True, exist_ok=True)
        image_stems = {p.stem for p in images_dir.iterdir() if p.suffix.lower() in {".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff"}}
        label_stems = {p.stem for p in labels_dir.glob("*.txt")}
        for stem in sorted(image_stems - label_stems):
            (labels_dir / f"{stem}.txt").write_text("")


def _subsample_negative_tiles(
    base_path: str | Path,
    fraction: float,
    seed: int = 0,
    splits: Sequence[str] = ("train", "valid", "test"),
) -> None:
    """Downsample empty-label tiles to approximately `fraction` of all tiles."""
    rng = random.Random(seed)
    base = Path(base_path)
    for split in splits:
        images_dir = base / split / "images"
        labels_dir = base / split / "labels"
        if not (images_dir.is_dir() and labels_dir.is_dir()):
            continue

        positives: List[str] = []
        negatives: List[str] = []
        for img_path in images_dir.iterdir():
            if img_path.suffix.lower() not in {".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff"}:
                continue
            stem = img_path.stem
            lbl_path = labels_dir / f"{stem}.txt"
            if not lbl_path.exists():
                negatives.append(stem)
                continue
            with lbl_path.open("r") as fh:
                has_box = any(line.strip() for line in fh)
            (positives if has_box else negatives).append(stem)

        total = len(positives) + len(negatives)
        if total == 0 or not negatives:
            continue

        target_neg = int(round(fraction * total))
        keep_neg = min(len(negatives), max(0, target_neg))
        remove_count = len(negatives) - keep_neg
        if remove_count <= 0:
            continue

        to_remove = {stem for stem in rng.sample(negatives, remove_count)}
        for stem in to_remove:
            for ext in (".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff"):
                img_candidate = images_dir / f"{stem}{ext}"
                if img_candidate.exists():
                    try:
                        img_candidate.unlink()
                    except OSError:
                        pass
            lbl_candidate = labels_dir / f"{stem}.txt"
            if lbl_candidate.exists():
                try:
                    lbl_candidate.unlink()
                except OSError:
                    pass


def tile_with_yolo_tiler(
    src: str | Path,
    dst: str | Path,
    *,
    input_ext: str = ".jpg",
    slice_wh: Tuple[int, int] = (640, 640),
    overlap_wh: Tuple[float, float] = (0.1, 0.1),
    include_empty: bool = True,
    negative_fraction: Optional[float] = None,
    random_seed: int = 0,
) -> None:
    """Run `yolo_tiler` and post-process to normalize empty tiles."""
    if YoloTiler is None or TileConfig is None:
        raise ImportError("yolo_tiler is not installed; install it before tiling.")

    need_negatives = (negative_fraction or 0.0) > 0.0 if negative_fraction is not None else include_empty
    cfg = TileConfig(
        slice_wh=slice_wh,
        overlap_wh=overlap_wh,
        input_ext=input_ext,
        annotation_type="object_detection",
        include_negative_samples=need_negatives,
        train_ratio=1.0,
        valid_ratio=0.0,
        test_ratio=0.0,
        compression=90,
        copy_source_data=False,
    )
    tiler = YoloTiler(
        source=str(src),
        target=str(dst),
        config=cfg,
        num_viz_samples=5,
        show_processing_status=True,
        progress_callback=progress_callback,
    )
    tiler.run()

    _materialize_empty_labels(dst)

    if negative_fraction is not None:
        if not 0.0 <= negative_fraction <= 1.0:
            raise ValueError("negative_fraction must be in [0, 1].")
        _subsample_negative_tiles(dst, negative_fraction, seed=random_seed)
        _materialize_empty_labels(dst)


# --------------------------------------------------------------------------- #
# Dataset preparation pipeline
# --------------------------------------------------------------------------- #

def prepare_yolo_dataset(
    dataset_path: str,
    out_dir: str,
    *,
    do_change_labels: bool = True,
    allowed_ids: set[int] | None = None,
    collapse_map: Dict[int, str] | None = None,
    new_class_ids: Dict[str, int] | None = None,
    drop_others: bool = False,
    prune_empty_fraction: float = 1.0,
    do_tile: bool = False,
    input_ext: str = ".jpg",
    slice_wh: Tuple[int, int] = (640, 640),
    overlap_wh: Tuple[float, float] | float = (0.1, 0.1),
    include_empty_tiles: bool = True,
    empty_tile_fraction: Optional[float] = None,
    include_empty_tiles_seed: int = 0,
    do_rebalance: bool = False,
    split: Tuple[float, float, float] = (0.7, 0.2, 0.1),
    remove_test: bool = False,
    seed: int = 0,
    clear_output: bool = True,
) -> None:
    """End-to-end pipeline to prepare a YOLO dataset.

    Parameters
    ----------
    collapse_map
        Mapping from original class id -> group name (e.g. {5: "shark"}).
        Use it when you want to merge multiple raw classes into a smaller set.
        Every id referenced here is automatically added to ``allowed_ids`` so
        that filtering and collapsing stay in sync.
    new_class_ids
        Reverse mapping from group name -> new contiguous id, typically built
        with :func:`build_new_class_ids_from_yaml`.
    allowed_ids
        Optional subset of class ids to keep *before* collapsing. If omitted
        but ``collapse_map`` is provided, the keys of ``collapse_map`` are used.
    """

    # Canonicalise label-mapping parameters up-front.
    collapse_keys = set(collapse_map.keys()) if collapse_map else set()
    effective_allowed_ids: set[int] | None = set(allowed_ids) if allowed_ids is not None else None
    if collapse_keys:
        if effective_allowed_ids is None:
            effective_allowed_ids = set(collapse_keys)
        else:
            missing = collapse_keys - effective_allowed_ids
            if missing:
                print(
                    "⚠️ collapse_map references class ids that are not present in allowed_ids; "
                    "adding them automatically:", sorted(missing)
                )
                effective_allowed_ids |= missing
    if effective_allowed_ids is not None:
        effective_allowed_ids = set(sorted(int(x) for x in effective_allowed_ids))

    def _yolo_label_files(labels_dir: str):
        if not os.path.isdir(labels_dir):
            return []
        return [
            os.path.join(labels_dir, f)
            for f in os.listdir(labels_dir)
            if f.endswith(".txt")
        ]

    def _find_image_for_label(label_path: str, images_dir: str):
        stem = os.path.splitext(os.path.basename(label_path))[0]
        for ext in (".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff", ".webp"):
            candidate = os.path.join(images_dir, stem + ext)
            if os.path.exists(candidate):
                return candidate
        return None

    def _filter_labels(pool_dir: str, allowed: set[int]) -> None:
        labels_dir = os.path.join(pool_dir, "labels")
        kept, dropped, emptied = 0, 0, 0
        for lp in _yolo_label_files(labels_dir) or []:
            with open(lp, "r") as fh:
                lines = [ln.strip() for ln in fh if ln.strip()]
            new_lines = []
            for ln in lines:
                parts = ln.split()
                try:
                    cid = int(float(parts[0]))
                except Exception:
                    continue
                if cid in allowed:
                    new_lines.append(ln)
                else:
                    dropped += 1
            kept += len(new_lines)
            with open(lp, "w") as fh:
                fh.write("\n".join(new_lines) + ("\n" if new_lines else ""))
            if not new_lines:
                emptied += 1
        print(f"   • filter_labels: kept={kept}, dropped={dropped}, emptied_files={emptied}")

    def _simplify_labels(pool_dir: str,
                         collapse_mapping: Dict[int, str],
                         new_ids: Dict[str, int],
                         drop: bool) -> None:
        labels_dir = os.path.join(pool_dir, "labels")
        remapped, kept_as_is, dropped = 0, 0, 0
        missing_names = set()
        for lp in _yolo_label_files(labels_dir) or []:
            with open(lp, "r") as fh:
                lines = [ln.strip() for ln in fh if ln.strip()]
            out_lines: List[str] = []
            for ln in lines:
                parts = ln.split()
                try:
                    old_id = int(float(parts[0]))
                except Exception:
                    continue
                if old_id in collapse_mapping:
                    new_name = collapse_mapping[old_id]
                    if new_name not in new_ids:
                        missing_names.add(new_name)
                        if not drop:
                            out_lines.append(ln)
                            kept_as_is += 1
                        else:
                            dropped += 1
                        continue
                    new_id = new_ids[new_name]
                    parts[0] = str(int(new_id))
                    out_lines.append(" ".join(parts))
                    remapped += 1
                else:
                    if drop:
                        dropped += 1
                    else:
                        out_lines.append(ln)
                        kept_as_is += 1
            with open(lp, "w") as fh:
                fh.write("\n".join(out_lines) + ("\n" if out_lines else ""))
        if missing_names:
            print(f"[warn] Missing names in new_class_ids: {sorted(missing_names)}")
        print(f"   • simplify_labels: remapped={remapped} kept_as_is={kept_as_is} dropped={dropped}")

    def prune_empty_labels(pool_dir: str, fraction: float = 1.0, seed_: int = 0) -> None:
        rng = random.Random(seed_)
        labels_dir = os.path.join(pool_dir, "labels")
        images_dir = os.path.join(pool_dir, "images")
        empties = []
        for lp in _yolo_label_files(labels_dir) or []:
            try:
                size = os.path.getsize(lp)
            except FileNotFoundError:
                size = 0
            if size == 0:
                empties.append(lp)
        n_drop = int(len(empties) * max(0.0, min(1.0, fraction)))
        rng.shuffle(empties)
        for lp in empties[:n_drop]:
            try:
                os.remove(lp)
            except FileNotFoundError:
                pass
            img = _find_image_for_label(lp, images_dir)
            if img:
                try:
                    os.remove(img)
                except FileNotFoundError:
                    pass
        print(f"   • prune_empty_labels: removed {n_drop} empty label/image pairs")

    def rebalance_dataset(
        dataset_root: str,
        output_path: str,
        split_: Tuple[float, float, float],
        remove_test_: bool,
        seed_: int,
    ) -> None:
        assert math.isclose(sum(split_), 1.0, abs_tol=1e-6), "split must sum to 1.0"
        rng = random.Random(seed_)
        all_images = []
        for subset in ("train", "valid", "test"):
            img_dir = os.path.join(dataset_root, subset, "images")
            lbl_dir = os.path.join(dataset_root, subset, "labels")
            if not os.path.isdir(img_dir) or not os.path.isdir(lbl_dir):
                continue
            for fname in os.listdir(img_dir):
                stem, ext = os.path.splitext(fname)
                label = os.path.join(lbl_dir, stem + ".txt")
                if os.path.exists(label):
                    all_images.append((os.path.join(img_dir, fname), label))

        if remove_test_:
            split_ = (split_[0], split_[1], 0.0)

        rng.shuffle(all_images)
        total = len(all_images)
        if total == 0:
            raise RuntimeError(f"No paired image/label files found under {dataset_root}")

        n_train = int(total * split_[0])
        n_valid = int(total * split_[1])
        n_test = total - n_train - n_valid

        train_pairs = all_images[:n_train]
        valid_pairs = all_images[n_train:n_train + n_valid]
        test_pairs = all_images[n_train + n_valid:]

        def _copy(batch: Sequence[Tuple[str, str]], subset: str):
            img_out = os.path.join(output_path, subset, "images")
            lbl_out = os.path.join(output_path, subset, "labels")
            os.makedirs(img_out, exist_ok=True)
            os.makedirs(lbl_out, exist_ok=True)
            for src_img, src_lbl in batch:
                shutil.copy2(src_img, os.path.join(img_out, os.path.basename(src_img)))
                shutil.copy2(src_lbl, os.path.join(lbl_out, os.path.basename(src_lbl)))

        _copy(train_pairs, "train")
        _copy(valid_pairs, "valid")
        if split_[2] > 0:
            _copy(test_pairs, "test")

        print(
            "   • split counts: "
            f"train={len(train_pairs)} valid={len(valid_pairs)}"
            + (f" test={len(test_pairs)}" if split_[2] > 0 else "")
        )
        print(f"   → wrote splits to: {output_path}")

    dataset_abs = os.path.abspath(dataset_path)
    if not os.path.isdir(dataset_abs):
        raise FileNotFoundError(f"Dataset path not found: {dataset_path}")

    working_root = mkdtemp(prefix="yolo_prep_")
    shutil.copytree(dataset_abs, working_root, dirs_exist_ok=True)
    working = working_root
    print(f"📝 Working directory: {working}")

    merged_images = os.path.join(working, "train", "images")
    merged_labels = os.path.join(working, "train", "labels")
    os.makedirs(merged_images, exist_ok=True)
    os.makedirs(merged_labels, exist_ok=True)

    for subset in ("train", "valid", "test"):
        src_img = os.path.join(working, subset, "images")
        src_lbl = os.path.join(working, subset, "labels")
        if not os.path.isdir(src_img):
            continue
        for f in os.listdir(src_img):
            shutil.move(os.path.join(src_img, f), os.path.join(merged_images, f))
        for f in os.listdir(src_lbl):
            shutil.move(os.path.join(src_lbl, f), os.path.join(merged_labels, f))
        if subset != "train":
            shutil.rmtree(os.path.join(working, subset), ignore_errors=True)

    pool_dir = os.path.join(working, "train")

    if do_change_labels:
        if effective_allowed_ids is not None:
            print("🔍 Filtering labels …")
            _filter_labels(pool_dir, effective_allowed_ids)
        if collapse_map and new_class_ids:
            print("📑 Collapsing class taxonomy …")
            _simplify_labels(pool_dir, collapse_map, new_class_ids, drop_others)
    elif any([allowed_ids, collapse_map, new_class_ids]):
        print("ℹ️ do_change_labels=False → ignoring allowed_ids/collapse_map/new_class_ids")

    prune_empty_labels(pool_dir, fraction=prune_empty_fraction, seed_=seed)

    if do_tile:
        print("🧩 Tiling dataset …")
        tiled_tmp = mkdtemp(prefix="yolo_tiled_")
        os.makedirs(tiled_tmp, exist_ok=True)

        for subset in ("valid", "test"):
            os.makedirs(os.path.join(working, subset, "images"), exist_ok=True)
            os.makedirs(os.path.join(working, subset, "labels"), exist_ok=True)

        tile_with_yolo_tiler(
            src=working,
            dst=tiled_tmp,
            input_ext=input_ext,
            slice_wh=slice_wh,
            overlap_wh=overlap_wh if isinstance(overlap_wh, tuple) else (overlap_wh, overlap_wh),
            include_empty=(include_empty_tiles if empty_tile_fraction is None else True),
            negative_fraction=empty_tile_fraction,
            random_seed=include_empty_tiles_seed,
        )
        pool_dir = os.path.join(tiled_tmp, "train")
        prune_empty_labels(pool_dir, fraction=prune_empty_fraction, seed_=seed)

    if clear_output:
        shutil.rmtree(out_dir, ignore_errors=True)
    os.makedirs(out_dir, exist_ok=True)

    if do_rebalance:
        print("🔀 Rebalancing (splitting) into final out_dir …")
        dataset_root_for_split = os.path.dirname(pool_dir)
        rebalance_dataset(
            dataset_root=dataset_root_for_split,
            output_path=out_dir,
            split_=split,
            remove_test_=remove_test,
            seed_=seed,
        )
    else:
        print("📦 No rebalance — exporting single unsplit pool to out_dir")
        shutil.copytree(os.path.join(pool_dir, "images"), os.path.join(out_dir, "images"))
        shutil.copytree(os.path.join(pool_dir, "labels"), os.path.join(out_dir, "labels"))

    print(f"✅ Final dataset written to: {out_dir}")


# --------------------------------------------------------------------------- #
# Dataset inspection helpers
# --------------------------------------------------------------------------- #

def _iter_label_files(root: str, splits: Sequence[str] = ("train", "valid", "test")):
    """Yield all label file paths from split or single-pool layouts."""
    root_path = Path(root)
    found_any = False
    for split in splits:
        lbl_dir = root_path / split / "labels"
        if lbl_dir.is_dir():
            found_any = True
            yield from (str(p) for p in lbl_dir.glob("*.txt"))
    if not found_any:
        single_pool = root_path / "labels"
        if single_pool.is_dir():
            yield from (str(p) for p in single_pool.glob("*.txt"))


def summarize_classes(dataset_root: str):
    """Summarize class distribution across a dataset root."""
    instance_counts = Counter()
    file_counts = Counter()
    total_label_files = 0
    empty_files = 0

    for label_path in _iter_label_files(dataset_root):
        total_label_files += 1
        seen_in_file = set()
        try:
            with open(label_path, "r") as fh:
                lines = [ln.strip() for ln in fh if ln.strip()]
        except Exception:
            continue
        if not lines:
            empty_files += 1
            continue
        for ln in lines:
            parts = ln.split()
            if not parts:
                continue
            try:
                cid = int(float(parts[0]))
            except Exception:
                continue
            instance_counts[cid] += 1
            seen_in_file.add(cid)
        for cid in seen_in_file:
            file_counts[cid] += 1

    return instance_counts, file_counts, total_label_files, empty_files


def auto_select_allowed_ids(
    dataset_root: str,
    *,
    min_instances: int | None = 50,
    min_files: int | None = None,
    ensure_ids: Iterable[int] | None = None,
):
    """Suggest `allowed_ids` based on occurrence thresholds.

    Parameters
    ----------
    dataset_root
        Root directory containing YOLO-style splits.
    min_instances
        Keep classes that appear at least this many times. Pass ``None`` to disable
        the instance threshold (useful when you plan to collapse labels).
    min_files
        Optional threshold on number of label files a class must appear in.
    ensure_ids
        Iterable of class ids that must be included in the output (e.g. the keys
        of your ``collapse_map``).
    """
    inst, files, total_files, empty = summarize_classes(dataset_root)

    print(f"Dataset scanned: {dataset_root}")
    print(f"Label files: {total_files}  (empty: {empty})")
    if not inst:
        print("No annotations found.")
        return set(), inst, files

    print("\nPer-class summary:")
    print("class_id | instances | files_present_in")
    for cid in sorted(inst):
        print(f"{cid:7d} | {inst[cid]:9d} | {files.get(cid, 0):15d}")

    min_inst_threshold = min_instances if min_instances is not None else 0
    allowed = {
        cid
        for cid in inst
        if inst[cid] >= min_inst_threshold and (min_files is None or files.get(cid, 0) >= min_files)
    }

    if ensure_ids:
        ensure_ids_set = {int(x) for x in ensure_ids}
        missing = ensure_ids_set - allowed
        if missing:
            print(f"Including {sorted(missing)} to honour ensure_ids parameter.")
        allowed |= ensure_ids_set

    kept = sorted(allowed)
    dropped = sorted(set(inst.keys()) - allowed)
    threshold_desc = "min_instances disabled" if min_instances is None else f"min_instances >= {min_instances}"
    print("\nSelection thresholds:",
          threshold_desc,
          (f"and min_files >= {min_files}" if min_files is not None else "(no file-prevalence threshold)"))
    print(f"→ allowed_ids = {kept if kept else '∅'}")
    if dropped:
        print(f"→ dropped_ids  = {dropped}")

    return allowed, inst, files


def count_labels(label_dir: str):
    """Count labels per class inside `label_dir`."""
    class_counts = Counter()
    empty_count = 0
    total_files = 0
    for path in Path(label_dir).glob("*.txt"):
        total_files += 1
        with path.open("r") as fh:
            lines = [ln.strip() for ln in fh if ln.strip()]
        if not lines:
            empty_count += 1
            continue
        for ln in lines:
            parts = ln.split()
            if not parts:
                continue
            try:
                class_id = int(float(parts[0]))
            except ValueError:
                continue
            class_counts[class_id] += 1
    return dict(sorted(class_counts.items())), empty_count, total_files


def check_dataset(out_dir: str, splits: Sequence[str] = ("train", "valid", "test")):
    """Print a summary of class counts for a prepared dataset."""
    out_path = Path(out_dir).resolve()
    print(f"Checking split dataset at: {out_path}")

    found_any_split = False
    for split in splits:
        label_path = out_path / split / "labels"
        if label_path.is_dir():
            found_any_split = True
            counts, empty_count, total_files = count_labels(str(label_path))
            print(f"\n[{split}] labels: {label_path}")
            print("Class counts:", counts)
            print(f"Empty labels: {empty_count} / {total_files}")
        else:
            print(f"[warn] Missing expected folder: {label_path}")

    if not found_any_split:
        single_labels = out_path / "labels"
        if single_labels.is_dir():
            print("\n[info] No split folders found; falling back to single pool:")
            counts, empty_count, total_files = count_labels(str(single_labels))
            print(f"labels: {single_labels}")
            print("Class counts:", counts)
            print(f"Empty labels: {empty_count} / {total_files}")
        else:
            print("\n❌ No labels found in split or single-pool layout.")


# --------------------------------------------------------------------------- #
# YAML helpers
# --------------------------------------------------------------------------- #

def _load_yaml_names(src_yaml: str) -> List[str] | None:
    """Extract names array from a YOLO data.yaml file."""
    if not os.path.exists(src_yaml):
        return None
    with open(src_yaml, "r") as stream:
        data = yaml.safe_load(stream) or {}
    names = data.get("names")
    if names is None:
        return None
    if isinstance(names, dict):
        max_id = max(int(k) for k in names)
        out: List[Optional[str]] = [None] * (max_id + 1)
        for k, v in names.items():
            out[int(k)] = str(v)
        for idx, val in enumerate(out):
            if val is None:
                out[idx] = f"class_{idx}"
        return [str(name) for name in out]
    if isinstance(names, list):
        return [str(n) for n in names]
    return None


def _detect_has_test(dataset_root: str | Path) -> bool:
    """Check whether dataset root contains a test split."""
    return (Path(dataset_root) / "test" / "images").exists()


def build_new_class_ids_from_yaml(
    src_yaml: str,
    allowed_ids: Iterable[int],
    collapse_map: Mapping[int, int],
) -> Dict[str, int]:
    """Create name -> new_id mapping from an existing data.yaml file."""
    allowed_ids = sorted(set(int(a) for a in allowed_ids))
    orig_names = _load_yaml_names(src_yaml)
    new_map: Dict[str, int] = {}
    if orig_names is None:
        for old in allowed_ids:
            new_id = collapse_map[old]
            new_map[f"class_{new_id}"] = new_id
        return new_map

    for old in allowed_ids:
        new_id = collapse_map[old]
        cname = orig_names[old] if old < len(orig_names) else f"class_{old}"
        new_map[cname] = new_id
    return new_map


def make_data_yaml(
    dataset_root: str | Path,
    new_class_ids: Mapping[str, int],
    yaml_name: str = "data.yaml",
    has_test: bool | None = None,
) -> str:
    """Write a YOLO-style data.yaml file with contiguous class ids."""
    max_id = max(new_class_ids.values())
    names: List[Optional[str]] = [None] * (max_id + 1)
    for name, idx in new_class_ids.items():
        names[idx] = name
    if any(n is None for n in names):
        raise ValueError("new_class_ids must cover a contiguous 0..N range without gaps.")

    if has_test is None:
        has_test = _detect_has_test(dataset_root)

    data = {
        "path": os.path.abspath(dataset_root),
        "train": "train/images",
        "val": "valid/images",
        "nc": len(names),
        "names": names,
    }
    if has_test:
        data["test"] = "test/images"

    out_path = Path(dataset_root) / yaml_name
    with out_path.open("w") as stream:
        yaml.safe_dump(data, stream, sort_keys=False, allow_unicode=True)
    return str(out_path)


__all__ = [
    "Data",
    "auto_select_allowed_ids",
    "build_collapse_map",
    "build_new_class_ids_from_yaml",
    "check_dataset",
    "count_labels",
    "filter_labels",
    "make_data_yaml",
    "prepare_yolo_dataset",
    "simplify_labels",
    "summarize_classes",
    "tile_with_yolo_tiler",
]
