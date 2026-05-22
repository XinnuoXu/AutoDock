#!/usr/bin/env python3
"""
Convert mutation JSON files to FASTA format for AlphaFold/ColabFold batch prediction.

This script reads mutation JSON files and generates FASTA files with a maximum of
30 sequences per file. The output files are organized by protein name in separate
directories.

Usage:
    python mutation_to_FASTA.py <mutation_json_file>
    python mutation_to_FASTA.py protein_sequences/test_protein_mutations.json

    Or process all mutation files in a directory:
    python mutation_to_FASTA.py protein_sequences/
"""

import json
import os
import sys
from pathlib import Path
from typing import Dict, List


def load_mutation_file(json_file: str) -> Dict:
    """
    Load mutation data from JSON file.

    Args:
        json_file: Path to the mutation JSON file

    Returns:
        Dictionary containing mutation data
    """
    with open(json_file, 'r') as f:
        data = json.load(f)
    return data


def create_fasta_batches(mutation_data: Dict, output_dir: Path, batch_size: int = 30) -> List[str]:
    """
    Create FASTA files from mutation data, splitting into batches.

    Args:
        mutation_data: Dictionary containing mutation information
        output_dir: Directory to save FASTA files
        batch_size: Maximum number of sequences per FASTA file (default: 30)

    Returns:
        List of created FASTA file paths
    """
    protein_name = mutation_data.get("protein_name", "unknown_protein")
    original_sequence = mutation_data.get("original_sequence", "")
    mutations = mutation_data.get("mutations", [])

    if not mutations:
        print(f"Warning: No mutations found for {protein_name}")
        return []

    # Create output directory
    output_dir.mkdir(parents=True, exist_ok=True)

    # Calculate number of batches needed
    total_sequences = len(mutations) + 1  # +1 for original sequence
    num_batches = (total_sequences - 1) // batch_size + 1

    created_files = []

    # Process each batch
    for batch_num in range(num_batches):
        batch_file = output_dir / f"{protein_name}_batch_{batch_num + 1:03d}.fasta"

        with open(batch_file, 'w') as f:
            # Add original sequence to first batch
            if batch_num == 0:
                f.write(f">{protein_name}_original\n")
                f.write(f"{original_sequence}\n\n")

            # Calculate sequence range for this batch
            if batch_num == 0:
                start_idx = 0
                end_idx = min(batch_size - 1, len(mutations))  # -1 because original takes one slot
            else:
                start_idx = (batch_num * batch_size) - 1  # -1 to account for original in first batch
                end_idx = min(start_idx + batch_size, len(mutations))

            # Write mutations for this batch
            for idx in range(start_idx, end_idx):
                mutation = mutations[idx]
                mutation_code = mutation.get("mutation_code", f"mut_{idx}")
                mutated_sequence = mutation.get("mutated_sequence", "")

                if mutated_sequence:
                    f.write(f">{protein_name}_{mutation_code}\n")
                    f.write(f"{mutated_sequence}\n\n")

        created_files.append(str(batch_file))
        print(f"Created: {batch_file} ({end_idx - start_idx + (1 if batch_num == 0 else 0)} sequences)")

    return created_files


def process_mutation_file(json_file: str, base_output_dir: str = "protein_squences",
                         batch_size: int = 30) -> List[str]:
    """
    Process a single mutation JSON file and create FASTA batches.

    Args:
        json_file: Path to the mutation JSON file
        base_output_dir: Base directory for output (default: "protein_squences")
        batch_size: Maximum sequences per FASTA file (default: 30)

    Returns:
        List of created FASTA file paths
    """
    print(f"\nProcessing: {json_file}")

    # Load mutation data
    try:
        mutation_data = load_mutation_file(json_file)
    except Exception as e:
        print(f"Error loading {json_file}: {e}")
        return []

    # Get protein name and create output directory
    protein_name = mutation_data.get("protein_name", "unknown_protein")
    output_dir = Path(base_output_dir) / f"{protein_name}_FASTA"

    # Print summary
    total_mutations = mutation_data.get("total_mutations", len(mutation_data.get("mutations", [])))
    mutation_positions = mutation_data.get("mutation_positions", [])

    print(f"Protein: {protein_name}")
    print(f"Total mutations: {total_mutations}")
    print(f"Mutation positions: {mutation_positions}")
    print(f"Output directory: {output_dir}")

    # Create FASTA batches
    created_files = create_fasta_batches(mutation_data, output_dir, batch_size)

    print(f"✓ Created {len(created_files)} FASTA batch file(s)")

    return created_files


def process_directory(directory: str, base_output_dir: str = "protein_squences",
                     batch_size: int = 30) -> Dict[str, List[str]]:
    """
    Process all mutation JSON files in a directory.

    Args:
        directory: Directory containing mutation JSON files
        base_output_dir: Base directory for output
        batch_size: Maximum sequences per FASTA file

    Returns:
        Dictionary mapping input files to created FASTA files
    """
    directory_path = Path(directory)

    # Find all mutation JSON files
    mutation_files = list(directory_path.glob("*_mutations.json"))

    if not mutation_files:
        print(f"No mutation files found in {directory}")
        return {}

    print(f"Found {len(mutation_files)} mutation file(s)")

    results = {}
    for json_file in mutation_files:
        created_files = process_mutation_file(str(json_file), base_output_dir, batch_size)
        results[str(json_file)] = created_files

    return results


def main():
    """Main entry point for the script."""
    if len(sys.argv) < 2:
        print("Usage: python mutation_to_FASTA.py <mutation_json_file_or_directory>")
        print("\nExamples:")
        print("  python mutation_to_FASTA.py protein_squences/test_protein_mutations.json")
        print("  python mutation_to_FASTA.py protein_squences/")
        sys.exit(1)

    input_path = sys.argv[1]
    batch_size = 30  # Default batch size

    # Optional: allow custom batch size
    if len(sys.argv) > 2:
        try:
            batch_size = int(sys.argv[2])
            print(f"Using custom batch size: {batch_size}")
        except ValueError:
            print(f"Invalid batch size: {sys.argv[2]}, using default: 30")

    # Check if input is a file or directory
    if os.path.isfile(input_path):
        # Process single file
        if not input_path.endswith("_mutations.json"):
            print(f"Warning: File should end with '_mutations.json': {input_path}")

        created_files = process_mutation_file(input_path, batch_size=batch_size)

        print(f"\n{'='*60}")
        print(f"Summary: Created {len(created_files)} FASTA file(s)")
        print(f"{'='*60}")

    elif os.path.isdir(input_path):
        # Process all files in directory
        results = process_directory(input_path, batch_size=batch_size)

        total_files = sum(len(files) for files in results.values())
        print(f"\n{'='*60}")
        print(f"Summary: Processed {len(results)} protein(s)")
        print(f"         Created {total_files} FASTA file(s) total")
        print(f"{'='*60}")

    else:
        print(f"Error: '{input_path}' is not a valid file or directory")
        sys.exit(1)


if __name__ == "__main__":
    main()
