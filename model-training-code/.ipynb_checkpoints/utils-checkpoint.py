import math 
import os
import random
import shutil
import glob

def rebalance_dataset(dataset_path, output_path, split=(0.7, 0.2, 0.1), remove_test=False):
    """
    Rebalance a YOLO dataset by shuffling and splitting into train/valid/test sets.

    Parameters
    ----------
    dataset_path : str
        Path to the original dataset (must contain train/, valid/, and optionally test/).
    output_path : str
        Where to save the rebalanced dataset.
    split : tuple of float
        Proportions for train, valid, and test splits. Must sum to 1.0.
    remove_test : bool
        If True, the test folder will be removed and a 80/20 train/valid split is done.
        If False, the provided split will be used.
    """

    assert math.isclose(sum(split), 1.0, abs_tol=1e-6), "Split proportions must sum to 1.0"
    # assert sum(split) == 1.0, "Split proportions must sum to 1.0"
    if remove_test:
        split = (0.8, 0.2, 0.0)

    # Collect all image-label pairs from available folders
    input_dirs = ['train', 'valid']
    if not remove_test:
        input_dirs.append('test')

    image_label_pairs = []

    for subset in input_dirs:
        img_dir = os.path.join(dataset_path, subset, 'images')
        lbl_dir = os.path.join(dataset_path, subset, 'labels')
        if not os.path.exists(img_dir) or not os.path.exists(lbl_dir):
            continue
        for img_file in os.listdir(img_dir):
            if img_file.lower().endswith(('.jpg', '.jpeg', '.png')):
                label_file = os.path.splitext(img_file)[0] + '.txt'
                image_label_pairs.append((
                    os.path.join(img_dir, img_file),
                    os.path.join(lbl_dir, label_file)
                ))

    # Shuffle randomly
    random.seed(0)
    random.shuffle(image_label_pairs)

    # Compute split counts
    total = len(image_label_pairs)
    num_train = int(total * split[0])
    num_valid = int(total * split[1])
    num_test = total - num_train - num_valid

    train_pairs = image_label_pairs[:num_train]
    valid_pairs = image_label_pairs[num_train:num_train + num_valid]
    test_pairs = image_label_pairs[num_train + num_valid:]

    # Helper to copy files
    def copy_pairs(pairs, subset):
        img_out = os.path.join(output_path, subset, 'images')
        lbl_out = os.path.join(output_path, subset, 'labels')
        os.makedirs(img_out, exist_ok=True)
        os.makedirs(lbl_out, exist_ok=True)
        for img_path, lbl_path in pairs:
            shutil.copy(img_path, os.path.join(img_out, os.path.basename(img_path)))
            shutil.copy(lbl_path, os.path.join(lbl_out, os.path.basename(lbl_path)))

    # Copy files to output dirs
    copy_pairs(train_pairs, 'train')
    copy_pairs(valid_pairs, 'valid')
    if split[2] > 0:
        copy_pairs(test_pairs, 'test')
    elif remove_test:
        test_path = os.path.join(dataset_path, 'test')
        if os.path.exists(test_path):
            shutil.rmtree(test_path)
            print("🗑️ Removed test/ folder from original dataset.")

    print("Rebalanced dataset saved to:", output_path)
    print(f"Train: {len(train_pairs)} | valid: {len(valid_pairs)} | test: {len(test_pairs) if split[2] > 0 else 0}")

def filter_labels(output_path, allowed_ids):
    """
    Go through every label file in the rebalanced dataset and remove lines that
    start with an integer (followed by a space) that is not in allowed_ids.
    """
    # Process both 'train' and 'valid' label directories.
    for subset in ['train', 'valid']:
        label_dir = os.path.join(output_path, subset, 'labels')
        for filename in os.listdir(label_dir):
            if filename.endswith('.txt'):
                file_path = os.path.join(label_dir, filename)
                with open(file_path, 'r') as file:
                    lines = file.readlines()

                filtered_lines = []
                for line in lines:
                    stripped = line.strip()
                    # Skip empty lines
                    if not stripped:
                        continue
                    parts = stripped.split()
                    if parts:
                        try:
                            # Check if the first token is an integer.
                            class_id = int(parts[0])
                            if class_id in allowed_ids:
                                filtered_lines.append(line)
                        except ValueError:
                            # If the first token is not an integer, keep the line.
                            filtered_lines.append(line)
                    else:
                        filtered_lines.append(line)

                with open(file_path, 'w') as file:
                    file.writelines(filtered_lines)

def simplify_labels(output_path, collapse_map, new_class_ids, drop_others=False):
    """
    Collapse original class IDs into new, coarser classes.

    Parameters
    ----------
    output_path : str
        Root of your rebalanced dataset (contains 'train/labels' and 'valid/labels').
    collapse_map : dict[int, str]
        Maps original class ID → new group name. E.g. {1: 'shark', 6: 'shark', 7: 'shark', 0: 'seaturtle'}.
    new_class_ids : dict[str, int]
        Maps group name → new numeric class ID. E.g. {'shark': 0, 'seaturtle': 1}.
    drop_others : bool, optional
        If True, any line whose original class ID is *not* in collapse_map will be removed.
        If False, those lines are left untouched.
    """
    for subset in ('train', 'valid'):
        label_dir = os.path.join(output_path, subset, 'labels')
        for fname in os.listdir(label_dir):
            if not fname.endswith('.txt'):
                continue

            in_path = os.path.join(label_dir, fname)
            with open(in_path, 'r') as f:
                lines = f.readlines()

            out_lines = []
            for line in lines:
                stripped = line.strip()
                if not stripped:
                    continue

                parts = stripped.split()
                # try to parse the class ID
                try:
                    orig_id = int(parts[0])
                except ValueError:
                    # non‑numeric first token: keep or drop?
                    if not drop_others:
                        out_lines.append(line)
                    continue

                if orig_id in collapse_map:
                    group = collapse_map[orig_id]
                    new_id = new_class_ids[group]
                    parts[0] = str(new_id)
                    out_lines.append(" ".join(parts) + "\n")
                else:
                    # orig_id not in collapse_map
                    if not drop_others:
                        out_lines.append(line)

            # overwrite
            with open(in_path, 'w') as f:
                f.writelines(out_lines)

def prepare_yolo_dataset(
    dataset_path,
    output_path,
    split=(0.75, 0.25, 0.0),  # default: 75% train, 25% valid, 0% test
    remove_test=False,
    allowed_ids=None,
    collapse_map=None,
    new_class_ids=None,
    drop_others=False
):
    """
    Prepare a YOLO-style dataset with rebalanced splits, optional filtering, and label simplification.

    Parameters
    ----------
    dataset_path : str
        Path to the original dataset (must contain 'train' and 'valid').
    output_path : str
        Where to save the processed dataset.
    split : tuple
        Proportions for (train, valid, test). Must sum to 1.0.
    remove_test : bool
        If True, deletes the original test/ folder and uses a 2-way split.
    allowed_ids : set[int], optional
        If given, keeps only labels with class IDs in this set.
    collapse_map : dict[int, str], optional
        Maps original class ID to a simplified group name.
    new_class_ids : dict[str, int], optional
        Maps simplified group name to new numeric ID.
    drop_others : bool
        Whether to discard classes not in collapse_map.
    """

    # Step 1: Rebalance the dataset
    rebalance_dataset(
        dataset_path=dataset_path,
        output_path=output_path,
        split=split,
        remove_test=remove_test
    )

    # Step 2: Filter labels
    if allowed_ids is not None:
        filter_labels(output_path, allowed_ids)

    # Step 3: Simplify taxonomy
    if collapse_map and new_class_ids:
        simplify_labels(output_path, collapse_map, new_class_ids, drop_others)

    print("Dataset prepared successfully.")


def count_labels(label_dir):
    class_counts = Counter()
    for fname in os.listdir(label_dir):
        if not fname.endswith('.txt'):
            continue
        with open(os.path.join(label_dir, fname)) as f:
            for line in f:
                parts = line.strip().split()
                if parts:
                    try:
                        class_id = int(parts[0])
                        class_counts[class_id] += 1
                    except ValueError:
                        continue
    return class_counts