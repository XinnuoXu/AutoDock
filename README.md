# AutoDock

A web-based protein mutation analysis pipeline for AutoDock structure prediction and molecular docking.

## Overview

This project provides a complete workflow for:
1. **Selecting mutation sites** - Interactive web interface for choosing protein positions to mutate
2. **Generating mutations** - Automated creation of all single-point mutations at selected positions
3. **Preparing for structure prediction** - Converting mutations to FASTA format for AlphaFold/ColabFold
4. **Structure prediction** - Using ColabFold batch notebooks on Google Colab
5. **Molecular docking** - Preparing predicted structures for AutoDock analysis

## Features

- Interactive web interface for mutation site selection
- Automatic generation of all 20 amino acid substitutions at selected positions
- FASTA batch file generation optimized for Google Colab (30 sequences per file)
- Integration with ColabFold for free GPU-accelerated structure prediction
- Organized file management and JSON-based data storage

---

## Quick Start

### 1. Environment Setup

Create and activate a conda environment:

```bash
# Create new conda environment with Python 3.10+
conda create -n autodock python=3.10

# Activate the environment
conda activate autodock
```

### 2. Install Dependencies

```bash
# Install required packages
pip install -r requirements.txt
```

Required packages:
- Flask==3.0.0 (web server)

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

### Step 5: Prepare Structures for AutoDock

After downloading predicted PDB files:

1. **Select best models**: Use `*_rank_001_*.pdb` files (highest confidence)

2. **Quality check**: Review pLDDT scores in JSON files
   - pLDDT > 90: Very high confidence
   - pLDDT 70-90: Good confidence
   - pLDDT < 70: Low confidence (use with caution)

3. **Prepare for docking:**
   - Remove water molecules
   - Add hydrogens
   - Calculate partial charges
   - Define binding sites

4. **Run AutoDock docking** with your ligands of interest

---

## Project Structure

```
AutoDock/
├── README.md                          # This file
├── requirements.txt                   # Python dependencies
├── user_interface/
│   └── app.py                        # Flask web server
├── src/
│   ├── mutation.py                   # Generate mutations
│   ├── mutation_to_FASTA.py          # Convert to FASTA batches
│   └── README_mutation_to_FASTA.md   # FASTA conversion docs
└── protein_squences/
    ├── {protein_name}.json           # Original protein + positions
    ├── {protein_name}_mutations.json # All mutations
    └── {protein_name}_FASTA/         # FASTA batch files
        ├── {protein_name}_batch_001.fasta
        ├── {protein_name}_batch_002.fasta
        └── ...
```

---

## Example: Complete Workflow

```bash
# 1. Start the web server
conda activate autodock
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

# 7. Download PDB files and run AutoDock docking
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
| **Total** | **~1-2 days** | **121 structures** |

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
