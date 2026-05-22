#!/usr/bin/env python3
"""
Protein Mutation Generator

This script generates single-point mutations for a protein sequence.
For each position marked for mutation, it creates 20 variants with
each of the 20 standard amino acids (excluding the original).

Usage:
    python mutation.py <protein_name>

Example:
    python mutation.py 2_BcLipase
"""

import json
import os
import sys


# All 20 standard amino acids
AMINO_ACIDS = "ARNDCQEGHILKMFPSTWYV"


def load_protein_data(protein_name):
    """
    Load protein data from JSON file.

    Args:
        protein_name: Name of the protein (without .json extension)

    Returns:
        dict: Protein data containing 'original_protein' and 'replace_pos'
    """
    filename = f"protein_squences/{protein_name}.json"

    if not os.path.exists(filename):
        raise FileNotFoundError(f"Protein file not found: {filename}")

    with open(filename, 'r') as f:
        data = json.load(f)

    return data


def generate_mutations(original_sequence, replace_positions):
    """
    Generate all single-point mutations for specified positions.

    Args:
        original_sequence: The original protein sequence
        replace_positions: List of positions to mutate (0-indexed)

    Returns:
        list: List of mutation dictionaries, each containing:
            - position: The mutation position
            - original_aa: Original amino acid
            - mutated_aa: New amino acid
            - mutated_sequence: The full mutated sequence
    """
    mutations = []

    for pos in replace_positions:
        if pos < 0 or pos >= len(original_sequence):
            print(f"Warning: Position {pos} is out of range, skipping...")
            continue

        original_aa = original_sequence[pos]

        # Generate mutation for each of the 20 amino acids
        for aa in AMINO_ACIDS:
            # Create mutated sequence
            mutated_sequence = list(original_sequence)
            mutated_sequence[pos] = aa
            mutated_sequence = ''.join(mutated_sequence)

            mutation = {
                'position': pos,
                'original_aa': original_aa,
                'mutated_aa': aa,
                'mutation_code': f"{original_aa}{pos}{aa}",
                'mutated_sequence': mutated_sequence
            }

            mutations.append(mutation)

    return mutations


def save_mutations(protein_name, original_sequence, replace_positions, mutations):
    """
    Save mutations to JSON file.

    Args:
        protein_name: Name of the protein
        original_sequence: Original protein sequence
        replace_positions: List of mutation positions
        mutations: List of mutation dictionaries
    """
    output_filename = f"protein_squences/{protein_name}_mutations.json"

    output_data = {
        'protein_name': protein_name,
        'original_sequence': original_sequence,
        'mutation_positions': replace_positions,
        'total_mutations': len(mutations),
        'mutations': mutations
    }

    with open(output_filename, 'w') as f:
        json.dump(output_data, f, indent=2)

    return output_filename


def main():
    """Main function to run the mutation generator."""

    if len(sys.argv) != 2:
        print("Usage: python mutation.py <protein_name>")
        print("Example: python mutation.py 2_BcLipase")
        sys.exit(1)

    protein_name = sys.argv[1]

    try:
        # Load protein data
        print(f"Loading protein data for: {protein_name}")
        protein_data = load_protein_data(protein_name)

        original_sequence = protein_data['original_protein']
        replace_positions = protein_data['replace_pos']

        print(f"Original sequence length: {len(original_sequence)}")
        print(f"Positions to mutate: {replace_positions}")
        print(f"Number of positions: {len(replace_positions)}")

        # Generate mutations
        print("\nGenerating mutations...")
        mutations = generate_mutations(original_sequence, replace_positions)

        print(f"Total mutations generated: {len(mutations)}")
        print(f"Expected mutations: {len(replace_positions)} positions × 20 variants = {len(replace_positions) * 20}")

        # Save mutations
        output_file = save_mutations(protein_name, original_sequence, replace_positions, mutations)

        print(f"\nMutations saved to: {output_file}")

        # Print summary
        print("\nMutation Summary:")
        position_counts = {}
        for mutation in mutations:
            pos = mutation['position']
            position_counts[pos] = position_counts.get(pos, 0) + 1

        for pos in sorted(position_counts.keys()):
            original_aa = original_sequence[pos]
            print(f"  Position {pos} ({original_aa}): {position_counts[pos]} mutations")

        print("\nDone!")

    except FileNotFoundError as e:
        print(f"Error: {e}")
        sys.exit(1)
    except KeyError as e:
        print(f"Error: Missing required field in protein data: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
