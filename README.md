# AutoDock

A web-based protein mutation analysis pipeline for AutoDock structure prediction and molecular docking.

## Overview

This project provides a complete workflow for:
1. **Selecting mutation sites** - Interactive web interface for choosing protein positions to mutate
2. **Generating mutations** - Automated creation of all single-point mutations at selected positions
3. **Preparing for structure prediction** - Converting mutations to FASTA format for AlphaFold/ColabFold
4. **Structure prediction** - Using ColabFold batch notebooks on Google Colab
5. **Converting to PDBQT** - Automated batch conversion of predicted PDB structures to PDBQT format
6. **Molecular docking** - Running AutoDock Vina docking with prepared structures

## Features

- Interactive web interface for mutation site selection
- Automatic generation of all 20 amino acid substitutions at selected positions
- FASTA batch file generation optimized for Google Colab (30 sequences per file)
- Integration with ColabFold for free GPU-accelerated structure prediction
- Automated batch conversion of PDB structures to PDBQT format using OpenBabel
- Organized file management and JSON-based data storage

---

## Quick Start

### 1. Environment Setup

**For Apple Silicon Macs (M1/M2/M3):**

```bash
# Install Rosetta 2 if not already installed
softwareupdate --install-rosetta

# Create x86_64 environment (required for AutoDock Vina)
CONDA_SUBDIR=osx-64 conda env create -f environment.yml
conda activate autodock
```

**For Intel Macs / Linux:**

```bash
# Create environment from YAML file
conda env create -f environment.yml
conda activate autodock
```

**OR install manually:**

```bash
# Create environment
conda create -n autodock python=3.12
conda activate autodock

# For Apple Silicon, force x86_64 architecture
conda config --env --set subdir osx-64  # Apple Silicon only

# Add channels
conda config --add channels conda-forge
conda config --add channels bioconda

# Install dependencies
conda install -c conda-forge boost-cpp swig
conda install -c bioconda autodock-vina
pip install -r requirements.txt
```

See [SETUP.md](SETUP.md) for detailed installation instructions and troubleshooting.

### 2. Verify Installation

```bash
# Check AutoDock Vina command-line tool
vina --version
# Expected output: AutoDock Vina v1.2.5-mod

# Check Python packages
python -c "import vina, rdkit, meeko; print('All packages installed successfully')"
```

**Important Note for Apple Silicon Users:**

The AutoDock Vina command-line tool (`vina`) needs to be built from source because the bioconda package contains an outdated binary (i386/PowerPC) that doesn't work on modern Macs.

If `vina --version` fails with "bad CPU type in executable", follow the build instructions in [SETUP.md](SETUP.md#bad-cpu-type-in-executable-vina-apple-silicon).

### 3. Run the Web Server

```bash
# Start the Flask server
python user_interface/app.py
```

The server will start on `http://localhost:5001`

### 4. Access the Web Interface

Open your browser and navigate to:
```
http://localhost:5001
```

You should see the protein mutation site selection interface.

---

## Complete Workflow

### Step 1: Select Mutation Sites (Web Interface)

1. **Open the web interface** at `http://localhost:5001`

2. **Enter protein information:**
   - Protein name (e.g., "2_BcLipase")
   - Paste or type the protein sequence (amino acid single-letter codes)

3. **Load and visualize:**
   - Click "Load Sequence" to display the interactive sequence
   - Each amino acid is displayed with its position number

4. **Select mutation positions:**
   - Click on individual amino acids to mark them for mutation
   - Selected positions will be highlighted
   - Click again to deselect

5. **Save protein data:**
   - Click "Save Protein Data" to generate the JSON file
   - File saved to: `protein_squences/{protein_name}.json`

**Output format:**
```json
{
  "original_protein": "MADNYAATRYPIIL...",
  "replace_pos": [126, 127, 128, 129, 216, 217]
}
```

---

### Step 2: Generate Mutations

Generate all single-point mutations at the selected positions:

```bash
python3 src/mutation.py <protein_name>
```

**Example:**
```bash
python3 src/mutation.py 2_BcLipase
```

**What this does:**
- Reads `protein_squences/2_BcLipase.json`
- For each selected position, creates mutations with all 20 amino acids
- Saves to `protein_squences/2_BcLipase_mutations.json`

**Calculation:** For N selected positions, you'll get approximately **N × 19 mutations** (20 amino acids minus the original at each position).

**Mutation file structure:**
```json
{
  "protein_name": "2_BcLipase",
  "original_sequence": "MADNYAATRYPIIL...",
  "mutation_positions": [126, 127, 128, 129, 216, 217],
  "total_mutations": 120,
  "mutations": [
    {
      "position": 126,
      "original_aa": "V",
      "mutated_aa": "A",
      "mutation_code": "V126A",
      "mutated_sequence": "MADNYAATRYP...A...YDPTGLSS..."
    },
    {
      "position": 126,
      "original_aa": "V",
      "mutated_aa": "R",
      "mutation_code": "V126R",
      "mutated_sequence": "MADNYAATRYP...R...YDPTGLSS..."
    },
    ...
  ]
}
```

---

### Step 3: Convert to FASTA Format for ColabFold

Convert mutation files to FASTA format, automatically split into batches of 30 sequences:

```bash
# Process single protein
python src/mutation_to_FASTA.py protein_squences/2_BcLipase_mutations.json

# Process all mutation files in directory
python src/mutation_to_FASTA.py protein_squences/
```

**What this does:**
- Reads mutation JSON files
- Creates FASTA files with 30 sequences each (optimal for Google Colab)
- Includes original sequence in first batch
- Organizes output by protein name

**Output structure:**
```
protein_squences/
├── 2_BcLipase_FASTA/
│   ├── 2_BcLipase_batch_001.fasta  (30 sequences: 1 original + 29 mutations)
│   ├── 2_BcLipase_batch_002.fasta  (30 sequences)
│   ├── 2_BcLipase_batch_003.fasta  (30 sequences)
│   ├── 2_BcLipase_batch_004.fasta  (30 sequences)
│   └── 2_BcLipase_batch_005.fasta  (1 sequence)
```

**FASTA format example:**
```fasta
>2_BcLipase_original
MADNYAATRYPIILVHGLTGTDKYAGVLEYWYGIQEDLQQRGATVYVANLSGFQSDDGPN...

>2_BcLipase_V126A
MADNYAATRYPIILVHGLTGTDKYAGVLEYWYGIQEDLQQRGATVYVANLSGFQSDDGPN...

>2_BcLipase_V126R
MADNYRATRYPIILVHGLTGTDKYAGVLEYWYGIQEDLQQRGATVYVANLSGFQSDDGPN...
```

---

### Step 4: Protein Structure Prediction with ColabFold (Google Colab)

Now you're ready to predict 3D structures using ColabFold on Google Colab (free GPU access):

#### 4.1 Upload FASTA Files to Google Drive

1. **Create folder structure in Google Drive:**
   ```
   MyDrive/
   └── ColabFold/
       ├── 2_BcLipase_batch_001.fasta
       ├── 2_BcLipase_batch_002.fasta
       └── ...
   ```

2. **Upload your batch files** from `protein_squences/{protein_name}_FASTA/`

#### 4.2 Open ColabFold Batch Notebook

**Notebook URL:**
```
https://colab.research.google.com/github/sokrypton/ColabFold/blob/main/batch/AlphaFold2_batch.ipynb
```

#### 4.3 Configure the Notebook

In the notebook, modify these parameters:

```python
# Mount Google Drive
from google.colab import drive
drive.mount('/content/drive')

# Configure job
query_sequence = "/content/drive/MyDrive/ColabFold/2_BcLipase_batch_001.fasta"
jobname = "2_BcLipase_batch_001"

# Prediction settings
num_models = 5        # Number of models per protein (1-5)
num_recycle = 3       # Recycling iterations (1-3)
use_amber = True      # AMBER relaxation (recommended)
```

#### 4.4 Run Predictions

1. **Click**: Runtime → Run all
2. **Wait**: ~3-6 hours for 30 proteins (~200 residues each)
3. **Monitor**: Check progress in the output cells

#### 4.5 Download Results

Results are saved to: `/content/drive/MyDrive/ColabFold/{jobname}/`

**Output files per protein:**
```
2_BcLipase_batch_001/
├── 2_BcLipase_V126A_unrelaxed_rank_001_*.pdb    # Best predicted structure
├── 2_BcLipase_V126A_scores_rank_001_*.json      # Confidence scores
├── 2_BcLipase_V126A_pae_rank_001_*.png          # Error prediction plot
└── ... (5 models per protein)
```

**Important files for AutoDock:**
- **`*_rank_001_*.pdb`** - Highest confidence structure (use this)
- **`*_scores_*.json`** - pLDDT confidence metrics

#### 4.6 Repeat for All Batches

Process each batch file sequentially:
- `2_BcLipase_batch_001.fasta` → Session 1
- `2_BcLipase_batch_002.fasta` → Session 2
- `2_BcLipase_batch_003.fasta` → Session 3
- etc.

**Tips:**
- Each Colab session has a **12-hour runtime limit**
- Save results frequently to Google Drive
- For faster processing, reduce `num_models` to 1-3

---

### Step 5: Convert PDB Structures to PDBQT Format

After downloading ColabFold results from Google Drive, convert all PDB files to PDBQT format for AutoDock Vina:

#### 5.1 Organize Downloaded Files

Create folder structure in your project:

```bash
mkdir -p protein_folds
```

Copy downloaded ColabFold output folders to `protein_folds/`:

```
protein_folds/
├── Fold_batch_001/
│   ├── 2_BcLipase_original_unrelaxed_rank_001_*.pdb
│   ├── 2_BcLipase_V126A_unrelaxed_rank_001_*.pdb
│   ├── 2_BcLipase_V126R_unrelaxed_rank_001_*.pdb
│   └── ... (30 PDB files)
├── Fold_batch_002/
│   └── ... (30 PDB files)
└── ...
```

#### 5.2 Run Batch Conversion

Convert all PDB files to PDBQT format using OpenBabel:

```bash
# Process all folders in protein_folds/
python src/convert_pdb_to_pdbqt.py

# Or process specific folder
python src/convert_pdb_to_pdbqt.py protein_folds/Fold_batch_001/
```

**What this does:**
- Finds all `.pdb` files recursively in ColabFold output folders
- Converts each to PDBQT format using OpenBabel with rigid receptor flag (`-xr`)
- Saves to `{folder_name}_pdbqt/` directories (e.g., `Fold_batch_001_pdbqt/`)
- Provides progress tracking and statistics
- Handles errors and timeouts gracefully (60s per file)

#### 5.3 Output Structure

```
protein_folds/
├── Fold_batch_001/                  # Original PDB files
│   ├── 2_BcLipase_V126A_*.pdb
│   └── ...
├── Fold_batch_001_pdbqt/            # Converted PDBQT files ← NEW
│   ├── 2_BcLipase_V126A_*.pdbqt
│   └── ...
├── Fold_batch_002/
│   └── ...
├── Fold_batch_002_pdbqt/            # Converted PDBQT files ← NEW
│   └── ...
└── ...
```

#### 5.4 Verify Conversion

The script will output:
```
======================================================================
Processing: Fold_batch_001
Output to: Fold_batch_001_pdbqt
======================================================================
Found 30 PDB file(s)

  [  1/30] ✓ 2_BcLipase_original_unrelaxed_rank_001.pdb
  [  2/30] ✓ 2_BcLipase_V126A_unrelaxed_rank_001.pdb
  [  3/30] ✓ 2_BcLipase_V126R_unrelaxed_rank_001.pdb
  ...
  [ 30/30] ✓ 2_BcLipase_T217Y_unrelaxed_rank_001.pdb

======================================================================
SUMMARY
======================================================================
Folders processed: 1
Total PDB files:   30
✓ Converted:       30
✗ Failed:          0
Success rate:      100.0%

✅ All conversions completed successfully!

Output location: /Users/xinnuo/Desktop/AutoDock/protein_folds
PDBQT files are ready for AutoDock Vina docking.
```

**Note:** You may see kekulization warnings like:
```
*** Open Babel Warning in PerceiveBondOrders
Failed to kekulize aromatic bonds
```
This is **normal and safe to ignore** for protein receptors. AutoDock Vina doesn't use bond orders for receptors, only atom types (which are correctly assigned).

#### 5.5 Quality Check (Optional)

Before docking, review pLDDT confidence scores from ColabFold JSON files:

- **pLDDT > 90**: Very high confidence
- **pLDDT 70-90**: Good confidence
- **pLDDT < 70**: Low confidence (use with caution)

Select `*_rank_001_*.pdb` files as they have the highest confidence.

---

### Step 6: Run AutoDock Vina Docking

Now you're ready to run molecular docking with your prepared PDBQT structures:

#### 6.1 Prepare Ligand

Convert your ligand to PDBQT format using meeko:

```bash
# From MOL2 file
mk_prepare_ligand.py -i ligand.mol2 -o ligand.pdbqt

# From SDF file
mk_prepare_ligand.py -i ligand.sdf -o ligand.pdbqt

# From SMILES
mk_prepare_ligand.py -i ligand.smi -o ligand.pdbqt
```

#### 6.2 Run Docking

Run AutoDock Vina for each receptor:

```bash
vina --receptor protein_folds/Fold_batch_001_pdbqt/2_BcLipase_V126A_*.pdbqt \
     --ligand ligand.pdbqt \
     --center_x 25.0 --center_y 30.0 --center_z 10.0 \
     --size_x 20.0 --size_y 20.0 --size_z 20.0 \
     --out docking_results/2_BcLipase_V126A_docked.pdbqt \
     --log docking_results/2_BcLipase_V126A_log.txt
```

**Define binding site coordinates** (`--center_x/y/z` and `--size_x/y/z`):
- Use known binding site from literature/structure
- Or use AutoDock Tools to visualize and define the box
- Box size typically 20-30 Å per dimension

#### 6.3 Batch Docking Script (Optional)

For docking all mutations, create a shell script:

```bash
#!/bin/bash
# batch_docking.sh

LIGAND="ligand.pdbqt"
CENTER_X=25.0
CENTER_Y=30.0
CENTER_Z=10.0
SIZE_X=20.0
SIZE_Y=20.0
SIZE_Z=20.0

mkdir -p docking_results

for receptor in protein_folds/*_pdbqt/*.pdbqt; do
    basename=$(basename "$receptor" .pdbqt)
    echo "Docking: $basename"

    vina --receptor "$receptor" \
         --ligand "$LIGAND" \
         --center_x $CENTER_X --center_y $CENTER_Y --center_z $CENTER_Z \
         --size_x $SIZE_X --size_y $SIZE_Y --size_z $SIZE_Z \
         --out "docking_results/${basename}_docked.pdbqt" \
         --log "docking_results/${basename}_log.txt"
done
```

Run with: `bash batch_docking.sh`

---

## Project Structure

```
AutoDock/
├── README.md                          # Main documentation
├── SETUP.md                           # Detailed setup guide
├── requirements.txt                   # Python packages (pip)
├── environment.yml                    # Complete environment (conda + pip)
├── user_interface/
│   └── app.py                        # Flask web server
├── src/
│   ├── mutation.py                   # Generate mutations
│   ├── mutation_to_FASTA.py          # Convert to FASTA batches
│   ├── convert_pdb_to_pdbqt.py       # Batch PDB to PDBQT conversion
│   └── README_mutation_to_FASTA.md   # FASTA conversion docs
├── protein_squences/
│   ├── {protein_name}.json           # Original protein + positions
│   ├── {protein_name}_mutations.json # All mutations
│   └── {protein_name}_FASTA/         # FASTA batch files
│       ├── {protein_name}_batch_001.fasta
│       ├── {protein_name}_batch_002.fasta
│       └── ...
└── protein_folds/                     # ColabFold outputs and PDBQT files
    ├── Fold_batch_001/               # ColabFold PDB outputs
    │   └── *.pdb
    ├── Fold_batch_001_pdbqt/         # Converted PDBQT files
    │   └── *.pdbqt
    └── ...
```

## Installed Packages

### Molecular Docking & Structure Analysis
- **AutoDock Vina** (v1.2.5) - Molecular docking command-line tool
  - ⚠️ **Built from source** (bioconda package is broken on macOS)
  - See [SETUP.md](SETUP.md) for build instructions
- **vina** (1.2.7) - Python bindings for AutoDock Vina (pip package)
- **OpenBabel** - Chemical file format converter (install via conda: `conda install -c conda-forge openbabel`)
  - Used for PDB to PDBQT conversion in `convert_pdb_to_pdbqt.py`
- **meeko** (0.7.1) - Molecule preparation for ligands
- **rdkit** (2025.9.3) - Cheminformatics and molecular modeling
- **prody** (2.6.1) - Protein structure analysis
- **biopython** (1.87) - Biological computation tools
- **gemmi** (0.7.5) - Crystallography and structural biology

### Web Interface
- **Flask** (3.0.0) - Web framework for mutation selection interface

### Scientific Computing
- **numpy** (2.4.6) - Numerical computing
- **scipy** (1.17.1) - Scientific algorithms

### Build Dependencies (conda)
- **boost-cpp** (1.78.0) - C++ Boost libraries
- **boost** (1.78.0) - Boost with headers (required for vina build)
- **swig** (4.2.0) - Interface compiler

See [requirements.txt](requirements.txt), [environment.yml](environment.yml), and [backup_requirements.txt](backup_requirements.txt) for complete package lists.

---

## Example: Complete Workflow

```bash
# 0. Setup environment (first time only)
CONDA_SUBDIR=osx-64 conda env create -f environment.yml
conda activate autodock

# If vina binary needs to be built (Apple Silicon), see SETUP.md
# This is a one-time setup step

# 1. Start the web server
python user_interface/app.py

# 2. Use web interface (http://localhost:5001)
# - Enter protein name: "2_BcLipase"
# - Paste sequence
# - Select positions: 126, 127, 128, 129, 216, 217
# - Save protein data

# 3. Generate mutations
python src/mutation.py 2_BcLipase
# Output: 120 mutations created

# 4. Convert to FASTA batches
python src/mutation_to_FASTA.py protein_squences/2_BcLipase_mutations.json
# Output: 5 FASTA files (30 sequences each)

# 5. Upload FASTA files to Google Drive

# 6. Run ColabFold notebook for each batch
# - batch_001.fasta → 30 PDB structures
# - batch_002.fasta → 30 PDB structures
# - ... (repeat for all batches)

# 7. Download PDB files from Google Drive to protein_folds/
# Copy Fold_batch_001/, Fold_batch_002/, etc. to protein_folds/

# 8. Convert PDB structures to PDBQT format
python src/convert_pdb_to_pdbqt.py
# Output: protein_folds/Fold_batch_001_pdbqt/, Fold_batch_002_pdbqt/, etc.

# 9. Prepare ligand for docking
mk_prepare_ligand.py -i ligand.mol2 -o ligand.pdbqt

# 10. Run AutoDock Vina docking
vina --receptor protein_folds/Fold_batch_001_pdbqt/2_BcLipase_V126A_*.pdbqt \
     --ligand ligand.pdbqt \
     --center_x 25.0 --center_y 30.0 --center_z 10.0 \
     --size_x 20.0 --size_y 20.0 --size_z 20.0 \
     --out docking_results/2_BcLipase_V126A_docked.pdbqt
```

---

## Batch Processing Timeline

For 6 mutation positions (120 mutations total):

| Step | Time | Output |
|------|------|--------|
| Select positions (web) | 5 minutes | `.json` file |
| Generate mutations | < 1 minute | `_mutations.json` |
| Convert to FASTA | < 1 minute | 5 FASTA files |
| Upload to Drive | 5 minutes | - |
| ColabFold batch 1 | 3-6 hours | 30 PDB files |
| ColabFold batch 2 | 3-6 hours | 30 PDB files |
| ColabFold batch 3 | 3-6 hours | 30 PDB files |
| ColabFold batch 4 | 3-6 hours | 30 PDB files |
| ColabFold batch 5 | 1-2 hours | 1 PDB file |
| Download from Drive | 10 minutes | 121 PDB files |
| Convert to PDBQT | 2-5 minutes | 121 PDBQT files |
| **Total** | **~1-2 days** | **121 docking-ready structures** |

---

## Tips & Best Practices

### Mutation Site Selection
- Focus on active sites, binding pockets, or functional domains
- Limit to 3-10 positions for manageable dataset sizes
- Review protein structure/literature before selecting positions

### FASTA Batch Size
- Default: 30 sequences (optimal for Colab's 12-hour limit)
- For faster processing: Reduce to 20 sequences
- For longer proteins (>500 residues): Reduce to 10-15 sequences

### ColabFold Settings
- **Fast but good quality**: `num_models=3, num_recycle=2, use_amber=False`
- **Balanced**: `num_models=5, num_recycle=3, use_amber=True` (default)
- **Maximum quality**: `num_models=5, num_recycle=5, use_amber=True`

### Avoiding Colab Timeouts
- Keep browser tab open
- Don't let session idle for >90 minutes
- Save results to Google Drive frequently
- Consider Colab Pro ($10/month) for longer runtimes

---

## Troubleshooting

### Web server won't start
```bash
# Check if port 5001 is already in use
lsof -i :5001

# Kill existing process or change port in app.py
```

### Mutation script fails
```bash
# Verify JSON file exists
ls protein_squences/{protein_name}.json

# Check JSON format is valid
python -m json.tool protein_squences/{protein_name}.json
```

### FASTA conversion issues
```bash
# Ensure mutation file has been generated
ls protein_squences/{protein_name}_mutations.json

# Check file permissions
chmod +w protein_squences/
```

### Colab runtime disconnects
- Colab free tier has dynamic limits
- Wait a few hours and try again
- Consider using Colab Pro for guaranteed access

---

## References

- **ColabFold**: https://github.com/sokrypton/ColabFold
- **AlphaFold**: https://github.com/google-deepmind/alphafold
- **AutoDock**: http://autodock.scripps.edu/
- **ColabFold Paper**: https://www.nature.com/articles/s41592-022-01488-1

---

## License

[Add your license information here]

## Contact

[Add your contact information here]
