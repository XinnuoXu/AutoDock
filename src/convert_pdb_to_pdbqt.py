#!/usr/bin/env python3
"""
Convert PDB files to PDBQT format for AutoDock Vina docking.

This script processes AlphaFold/ColabFold output folders, finds all PDB files,
and converts them to PDBQT format using OpenBabel.

Usage:
    python src/convert_pdb_to_pdbqt.py
    python src/convert_pdb_to_pdbqt.py protein_folds/
    python src/convert_pdb_to_pdbqt.py protein_folds/Fold_batch_001/

Author: AutoDock Pipeline
Date: May 23, 2026
"""

import os
import sys
import subprocess
from pathlib import Path
from typing import List, Tuple


def find_pdb_files(folder: Path) -> List[Path]:
    """
    Find all PDB files in a folder, selecting only rank_001 models.

    For ColabFold/AlphaFold outputs with multiple ranked models (rank_001 to rank_005),
    only select rank_001 files as they have the highest confidence (best pLDDT scores).

    Args:
        folder: Path to folder containing PDB files

    Returns:
        List of Path objects for PDB files (only rank_001 models)
    """
    pdb_files = []

    # Find all .pdb files recursively
    for pdb_file in folder.rglob("*.pdb"):
        # Skip cleaned/temporary files we might have created
        if "_clean" in pdb_file.name:
            continue

        # Only include rank_001 files (highest confidence models)
        # This skips rank_002, rank_003, rank_004, rank_005
        if "rank_000" in pdb_file.name and pdb_file.is_file():
            pdb_files.append(pdb_file)
        # Also include files without rank in the name (e.g., single model predictions)
        elif "rank_" not in pdb_file.name and pdb_file.is_file():
            pdb_files.append(pdb_file)

    return sorted(pdb_files)


def convert_pdb_to_pdbqt(pdb_file: Path, output_file: Path) -> Tuple[bool, str]:
    """
    Convert a PDB file to PDBQT format using OpenBabel.

    Args:
        pdb_file: Input PDB file path
        output_file: Output PDBQT file path

    Returns:
        Tuple of (success: bool, message: str)
    """
    # Create output directory if it doesn't exist
    output_file.parent.mkdir(parents=True, exist_ok=True)

    # Build obabel command
    cmd = [
        "obabel",
        "-ipdb", str(pdb_file),
        "-opdbqt",
        "-O", str(output_file),
        "-xr"  # Rigid receptor
    ]

    try:
        # Run obabel
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=60  # 60 second timeout per file
        )

        # Check if conversion was successful
        if result.returncode == 0 and output_file.exists():
            # Check for common warnings (they're OK)
            if "Failed to kekulize" in result.stderr:
                return True, "OK (kekulize warning - safe to ignore)"
            return True, "OK"
        else:
            error_msg = result.stderr if result.stderr else "Unknown error"
            return False, f"Failed: {error_msg[:100]}"

    except subprocess.TimeoutExpired:
        return False, "Timeout (>60s)"
    except FileNotFoundError:
        return False, "obabel not found - install with: conda install -c conda-forge openbabel"
    except Exception as e:
        return False, f"Error: {str(e)[:100]}"


def process_folder(folder_path: Path, base_dir: Path) -> dict:
    """
    Process all PDB files in a folder and convert to PDBQT.

    Args:
        folder_path: Path to folder containing PDB files
        base_dir: Base directory (protein_folds/)

    Returns:
        Dictionary with conversion statistics
    """
    # Create output folder name (e.g., Fold_batch_001_pdbqt)
    output_folder_name = f"{folder_path.name}_pdbqt"
    output_folder = base_dir / output_folder_name

    print(f"\n{'='*70}")
    print(f"Processing: {folder_path.name}")
    print(f"Output to: {output_folder_name}")
    print(f"{'='*70}")

    # Find all PDB files
    pdb_files = find_pdb_files(folder_path)

    if not pdb_files:
        print(f"  ⚠️  No PDB files found in {folder_path.name}")
        return {"total": 0, "success": 0, "failed": 0}

    print(f"Found {len(pdb_files)} PDB file(s)")
    print()

    # Convert each PDB file
    stats = {"total": len(pdb_files), "success": 0, "failed": 0, "files": []}

    for i, pdb_file in enumerate(pdb_files, 1):
        # Create output filename (same name, different extension)
        output_file = output_folder / pdb_file.with_suffix(".pdbqt").name

        # Convert
        success, message = convert_pdb_to_pdbqt(pdb_file, output_file)

        # Update statistics
        if success:
            stats["success"] += 1
            status = "✓"
        else:
            stats["failed"] += 1
            status = "✗"

        stats["files"].append({
            "input": pdb_file.name,
            "output": output_file.name,
            "success": success,
            "message": message
        })

        # Print progress
        print(f"  [{i:3d}/{len(pdb_files)}] {status} {pdb_file.name}")
        if not success or "warning" in message.lower():
            print(f"           → {message}")

    return stats


def process_all_folders(base_dir: Path = Path("protein_folds")) -> None:
    """
    Process all ColabFold output folders in the base directory.

    Args:
        base_dir: Base directory containing fold folders (default: protein_folds/)
    """
    print(f"\n{'#'*70}")
    print(f"# PDB to PDBQT Batch Converter")
    print(f"# Base directory: {base_dir.absolute()}")
    print(f"{'#'*70}")

    # Find all folders (exclude _pdbqt folders)
    folders = []
    for item in base_dir.iterdir():
        if item.is_dir() and not item.name.endswith("_pdbqt"):
            folders.append(item)

    if not folders:
        print(f"\n⚠️  No folders found in {base_dir}")
        print(f"Expected folder structure:")
        print(f"  {base_dir}/")
        print(f"  ├── Fold_batch_001/")
        print(f"  │   ├── protein1_rank_001.pdb")
        print(f"  │   └── protein2_rank_001.pdb")
        print(f"  └── Fold_batch_002/")
        return

    folders.sort()
    print(f"\nFound {len(folders)} folder(s) to process:")
    for folder in folders:
        print(f"  - {folder.name}")

    # Process each folder
    all_stats = []
    for folder in folders:
        stats = process_folder(folder, base_dir)
        all_stats.append(stats)

    # Print summary
    print(f"\n{'='*70}")
    print(f"SUMMARY")
    print(f"{'='*70}")

    total_files = sum(s["total"] for s in all_stats)
    total_success = sum(s["success"] for s in all_stats)
    total_failed = sum(s["failed"] for s in all_stats)

    print(f"Folders processed: {len(folders)}")
    print(f"Total PDB files:   {total_files}")
    print(f"✓ Converted:       {total_success}")
    print(f"✗ Failed:          {total_failed}")

    if total_success > 0:
        success_rate = (total_success / total_files) * 100
        print(f"Success rate:      {success_rate:.1f}%")

    print(f"\n{'='*70}")

    if total_failed > 0:
        print("\n⚠️  Some conversions failed. Check the output above for details.")
    else:
        print("\n✅ All conversions completed successfully!")

    print(f"\nOutput location: {base_dir.absolute()}")
    print(f"PDBQT files are ready for AutoDock Vina docking.")
    print()


def main():
    """Main entry point."""
    # Parse command line arguments
    if len(sys.argv) > 1:
        base_dir = Path(sys.argv[1])
    else:
        base_dir = Path("protein_folds")

    # Check if base directory exists
    if not base_dir.exists():
        print(f"Error: Directory '{base_dir}' does not exist")
        sys.exit(1)

    # Check if this is an output folder (_pdbqt suffix)
    if "_pdbqt" in base_dir.name:
        print(f"Error: '{base_dir.name}' appears to be an output folder (_pdbqt)")
        sys.exit(1)

    # Determine if this is a specific folder to process or a base directory
    # Check if this folder contains PDB files directly (at any depth)
    pdb_files = find_pdb_files(base_dir)

    # Check if there are subdirectories that look like fold folders
    has_fold_subdirs = any(
        item.is_dir() and not item.name.endswith("_pdbqt") and not item.name.startswith(".")
        for item in base_dir.iterdir()
        if item.is_dir()
    )

    # If the folder contains PDB files and user explicitly specified it,
    # OR it has a name pattern like "Fold_batch_*" or similar,
    # process it as a single folder
    is_specific_folder = (
        len(sys.argv) > 1 and pdb_files and
        (base_dir.name.startswith("Fold_") or
         base_dir.name.startswith("batch_") or
         not has_fold_subdirs)
    )

    if is_specific_folder:
        # Process this specific folder
        parent_dir = base_dir.parent
        stats = process_folder(base_dir, parent_dir)

        print(f"\n{'='*70}")
        print(f"Processed {stats['total']} file(s)")
        print(f"✓ Success: {stats['success']}")
        print(f"✗ Failed:  {stats['failed']}")
        print(f"{'='*70}\n")
    else:
        # Process all folders in the base directory
        process_all_folders(base_dir)


if __name__ == "__main__":
    main()
