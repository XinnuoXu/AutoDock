#!/bin/zsh
# Batch docking script for AutoDock Vina
# Docks DiPU ligand against all protein mutant structures in a specified folder

# Check if folder name argument is provided
if [ $# -eq 0 ]; then
    echo "Usage: $0 <folder_name>"
    echo ""
    echo "Example: $0 Fold_batch_001_pdbqt"
    echo ""
    echo "Available folders:"
    ls -d protein_folds/*_pdbqt 2>/dev/null | xargs -n 1 basename
    exit 1
fi

FOLDER_NAME="$1"
RECEPTOR_DIR="protein_folds/$FOLDER_NAME"

# Check if the specified folder exists
if [ ! -d "$RECEPTOR_DIR" ]; then
    echo "Error: Directory not found: $RECEPTOR_DIR"
    echo ""
    echo "Available folders:"
    ls -d protein_folds/*_pdbqt 2>/dev/null | xargs -n 1 basename
    exit 1
fi

# Set path to conda autodock environment
CONDA_ENV="$HOME/miniconda3/envs/autodock"
VINA="$CONDA_ENV/bin/vina"

# Check if vina is available
if [ ! -f "$VINA" ]; then
    echo "Error: vina not found at $VINA"
    echo "Please check your conda autodock environment."
    exit 1
fi

# Configuration
LIGAND="ligands/DiPU.pdbqt"
CENTER_X=-0.05
CENTER_Y=-0.82
CENTER_Z=-3.58
SIZE_X=20
SIZE_Y=20
SIZE_Z=20
EXHAUSTIVENESS=16

# Create output directory
mkdir -p docking_results

# Check if ligand exists
if [ ! -f "$LIGAND" ]; then
    echo "Error: Ligand file not found: $LIGAND"
    exit 1
fi

echo "======================================================================="
echo "AutoDock Vina Batch Docking"
echo "======================================================================="
echo "Receptor directory: $RECEPTOR_DIR"
echo "Ligand: $LIGAND"
echo "Binding site center: ($CENTER_X, $CENTER_Y, $CENTER_Z)"
echo "Binding site size: ${SIZE_X}x${SIZE_Y}x${SIZE_Z} Å"
echo "Exhaustiveness: $EXHAUSTIVENESS"
echo "======================================================================="
echo ""

# Counter for progress tracking
total_receptors=$(find "$RECEPTOR_DIR" -name "*.pdbqt" 2>/dev/null | wc -l | tr -d ' ')
current=0

if [ "$total_receptors" -eq 0 ]; then
    echo "Error: No PDBQT receptor files found in $RECEPTOR_DIR"
    echo "Please run: python src/convert_pdb_to_pdbqt.py first"
    exit 1
fi

echo "Found $total_receptors receptor(s) to dock"
echo ""

# Loop through all PDBQT files in the specified folder
for receptor in "$RECEPTOR_DIR"/*.pdbqt; do
    if [ ! -f "$receptor" ]; then
        continue
    fi

    # Extract basename without extension
    basename=$(basename "$receptor" .pdbqt)

    # Update progress
    current=$((current + 1))

    echo "[$current/$total_receptors] Docking: $basename"
    echo "  Receptor: $receptor"
    echo "  Progress:"

    # Run vina docking (show progress, save to log)
    "$VINA" \
        --receptor "$receptor" \
        --ligand "$LIGAND" \
        --center_x $CENTER_X \
        --center_y $CENTER_Y \
        --center_z $CENTER_Z \
        --size_x $SIZE_X \
        --size_y $SIZE_Y \
        --size_z $SIZE_Z \
        --exhaustiveness $EXHAUSTIVENESS \
        --out "docking_results/${basename}_docked.pdbqt" \
        2>&1 | tee "docking_results/${basename}_log.txt"

    # Check if vina succeeded by checking if output file was created
    if [ -f "docking_results/${basename}_docked.pdbqt" ] && [ -s "docking_results/${basename}_docked.pdbqt" ]; then
        # Extract and display best binding affinity from log
        best_affinity=$(grep "^   1 " "docking_results/${basename}_log.txt" | awk '{print $2}')
        if [ -n "$best_affinity" ]; then
            echo "  ✓ Success: Best affinity = $best_affinity kcal/mol"
        else
            echo "  ✓ Success: docking_results/${basename}_docked.pdbqt"
        fi
    else
        echo "  ✗ Failed: Check docking_results/${basename}_log.txt for errors"
    fi
    echo ""
done

echo "======================================================================="
echo "Docking Complete"
echo "======================================================================="
echo "Total docked: $total_receptors receptors"
echo "Results saved to: docking_results/"
echo ""
echo "To view best binding affinities:"
echo "  grep '^   1 ' docking_results/*_log.txt | sort -k2 -n"
echo ""
