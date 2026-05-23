# AutoDock Project - Complete Session Summary
**Date:** May 23, 2026
**Session Duration:** ~4 hours
**Location:** /Users/xinnuo/Desktop/AutoDock

---

## Overview

This session involved setting up a complete protein mutation analysis and molecular docking pipeline, including:
- AlphaFold structure prediction research
- Python script development for FASTA batch generation
- Complete environment documentation
- Fixing AutoDock Vina installation on Apple Silicon
- Resolving numpy/scipy dependency conflicts
- PDB to PDBQT file conversion

---

## Part 1: AlphaFold API Research (Initial Investigation)

### Question: Does AlphaFold have an API for structure prediction?

**Answer:** Yes, but with important distinctions:

### AlphaFold Database API (For Pre-computed Predictions)
- **URL:** https://alphafold.ebi.ac.uk/api/prediction/{uniprot_id}
- **Purpose:** Retrieve pre-computed structures from 200+ million proteins
- **Access:** Free, REST API
- **Output:** PDB files, confidence scores (pLDDT, PAE)

**Example:**
```python
import requests

uniprot_id = "P14618"
api_url = f"https://alphafold.ebi.ac.uk/api/prediction/{uniprot_id}"
response = requests.get(api_url)
data = response.json()
pdb_url = data[0]["pdbUrl"]
```

### AlphaFold Server (For Novel Predictions)
- **URL:** https://alphafoldserver.com/
- **Type:** Web interface only (no REST API for automated submissions)
- **Features:** AlphaFold 3, supports proteins + DNA/RNA/ligands
- **Limitations:** JSON upload for batch jobs, but still requires manual submission

### Recommended Solution: ColabFold
Since your proteins are NOT in the database, use **ColabFold**:
- **Free:** Google Colab provides free GPU access
- **Fast:** 40-60x faster than AlphaFold for MSA generation
- **Scriptable:** Command-line and Python API available
- **Batch processing:** Handles multiple sequences efficiently

---

## Part 2: Local AlphaFold vs ColabFold Analysis

### AlphaFold 2 Local Installation Requirements

**Hardware:**
- **GPU:** Minimum 32GB VRAM (RTX 6000), Recommended 80GB (A100) = $10,000-20,000
- **RAM:** Minimum 64GB, Recommended 128GB+
- **Storage:** 2.2-2.6 TB for full databases
  - BFD database: 1.7-1.8 TB
  - PDB mmCIF: 206 GB
  - MGnify: 64 GB
  - Others: ~100 GB

**Time Investment:**
- Database download: 8-12 hours
- Setup: 4-8 hours
- Testing: 2-4 hours
- **Total: 1-2 days**

### ColabFold (Recommended Alternative)

**Hardware:**
- **GPU:** Any modern NVIDIA (8GB+), or use free Google Colab
- **Storage:** Only 20-30 GB (no massive database needed!)
- **RAM:** 16-32GB sufficient

**Time Investment:**
- Setup: 30 minutes - 2 hours
- **Total: Half day**

**Key Advantage:** Outsources MSA generation to remote servers (MMseqs2)

---

## Part 3: Google Colab Batch Notebook

### Input Format: FASTA

**Single Protein:**
```fasta
>protein1
MKWVTFISLLFLFSSAYSRGVFRRDAHKSEVAHRFKDLGE

>protein2
PIAQIHILEGRSDEQKETLIREVSEAISRSLDAPLTSVRVI
```

**Protein Complex (use `:` separator):**
```fasta
>complex1
FIRSTPROTEIN:SECONDPROTEIN
```

**With Ligands (AlphaFold3-compatible):**
```fasta
>protein_with_ATP
MKFLKFSLLTAVLLSVVFAFSSCGDDDDTISSSNY:ccd|ATP

>protein_DNA_complex
PROTEIN_SEQUENCE:dna|ATCGATCG
```

### Batch Limitations

**Google Colab Free Tier:**
- **Maximum runtime:** 12 hours
- **Idle timeout:** ~90 minutes
- **No hard sequence limit** in FASTA, but practical limits based on time

**Recommended batch size:** 20-30 sequences per session
- Small proteins (<200 residues): 30-50 per session
- Medium proteins (200-400 residues): 15-30 per session
- Large proteins (>400 residues): 5-15 per session

**ColabFold Batch Notebook:**
https://colab.research.google.com/github/sokrypton/ColabFold/blob/main/batch/AlphaFold2_batch.ipynb

---

## Part 4: Created mutation_to_FASTA.py Script

### Purpose
Convert mutation JSON files to FASTA format, automatically split into batches of 30 sequences (optimal for Google Colab).

### Location
`src/mutation_to_FASTA.py`

### Features
- Reads mutation JSON files
- Creates FASTA files with 30 sequences each
- Includes original sequence in first batch
- Organizes output by protein name in `protein_squences/{protein_name}_FASTA/`

### Usage

**Process single file:**
```bash
python src/mutation_to_FASTA.py protein_squences/2_BcLipase_mutations.json
```

**Process all mutation files:**
```bash
python src/mutation_to_FASTA.py protein_squences/
```

**Custom batch size:**
```bash
python src/mutation_to_FASTA.py protein_squences/test_protein_mutations.json 50
```

### Input Format (Mutation JSON)
```json
{
  "protein_name": "2_BcLipase",
  "original_sequence": "MADNYAATRYP...",
  "mutation_positions": [126, 127, 128, 129, 216, 217],
  "total_mutations": 120,
  "mutations": [
    {
      "position": 126,
      "original_aa": "V",
      "mutated_aa": "A",
      "mutation_code": "V126A",
      "mutated_sequence": "MADNYAATRYP...A...YDPTGLSS..."
    }
  ]
}
```

### Output Structure
```
protein_squences/
└── 2_BcLipase_FASTA/
    ├── 2_BcLipase_batch_001.fasta  (30 sequences)
    ├── 2_BcLipase_batch_002.fasta  (30 sequences)
    ├── 2_BcLipase_batch_003.fasta  (30 sequences)
    ├── 2_BcLipase_batch_004.fasta  (30 sequences)
    └── 2_BcLipase_batch_005.fasta  (1 sequence)
```

### Test Results
- Processed `test_protein_mutations.json`: 121 sequences → 5 FASTA files
- Processed `2_BcLipase_mutations.json`: 121 sequences → 5 FASTA files

---

## Part 5: Documentation Updates

### Files Created/Updated

1. **README.md** (445 lines)
   - Complete workflow documentation
   - Conda environment setup (Apple Silicon and Intel)
   - Step-by-step mutation → FASTA → ColabFold → AutoDock workflow
   - Batch processing timeline
   - Tips & best practices
   - Troubleshooting guide

2. **SETUP.md** (NEW - comprehensive setup guide)
   - Apple Silicon specific instructions
   - Rosetta 2 installation
   - x86_64 environment creation
   - Package descriptions
   - Troubleshooting section

3. **requirements.txt** (26 lines)
   - All pip packages organized by category
   - Web Interface: Flask, Jinja2, Werkzeug, etc.
   - Molecular Docking: vina, meeko, rdkit, prody, biopython, gemmi
   - Scientific: numpy, scipy, Pillow
   - Utilities: pyparsing, packaging

4. **environment.yml** (NEW)
   - Complete conda environment specification
   - Conda packages: boost-cpp, boost, swig
   - All pip packages
   - Platform configuration (osx-64 for Apple Silicon)

5. **backup_requirements.txt** (42 lines)
   - Backup of pip packages with notes
   - Documents vina build from source
   - Includes metadata about build date and configuration

6. **src/README_mutation_to_FASTA.md**
   - Complete documentation for FASTA conversion
   - Usage examples
   - Input/output formats
   - Integration with ColabFold

---

## Part 6: AutoDock Vina Installation (Major Challenge)

### Problem: "bad CPU type in executable: vina"

**Root Cause:**
- Bioconda's `autodock-vina` (v1.1.2) has an ancient binary (i386/PowerPC from ~2005)
- Does NOT work on modern Macs (Intel or Apple Silicon)
- Rosetta 2 only supports x86_64, not 32-bit i386 or PowerPC

**Verification:**
```bash
file $(which vina)
# Output: Mach-O universal binary with 2 architectures: [i386] [ppc_7400]
```

### Solution: Built AutoDock Vina from Source

**Steps Performed:**

1. **Removed broken package:**
```bash
conda remove autodock-vina --force -y
```

2. **Installed dependencies:**
```bash
conda install -c conda-forge boost-cpp=1.78.0 boost=1.78.0 swig=4.2.0
```

3. **Cloned AutoDock Vina:**
```bash
git clone --depth 1 --branch v1.2.5 https://github.com/ccsb-scripps/AutoDock-Vina.git
cd AutoDock-Vina/build/mac/release
```

4. **Created custom Makefile:**
```makefile
BASE=/Users/xinnuo/miniconda3/envs/autodock
BOOST_VERSION=
BOOST_INCLUDE = $(BASE)/include
C_PLATFORM=-pthread
GPP=clang++
C_OPTIONS= -O3 -DNDEBUG -std=c++11 -fvisibility=hidden
BOOST_LIB_VERSION=
BOOST_STATIC=n
BOOST_LIB_PATH=$(BASE)/lib

include ../../makefile_common
```

5. **Built with x86_64 architecture:**
```bash
arch -x86_64 make
```

6. **Fixed library paths:**
```bash
install_name_tool -add_rpath $CONDA_PREFIX/lib vina
```

7. **Installed to conda environment:**
```bash
cp vina $CONDA_PREFIX/bin/vina
chmod +x $CONDA_PREFIX/bin/vina
```

### Result
```bash
vina --version
# Output: AutoDock Vina v1.2.5-mod

file $(which vina)
# Output: Mach-O 64-bit executable x86_64
```

**Binary Location:** `/Users/xinnuo/miniconda3/envs/autodock/bin/vina`

---

## Part 7: Numpy/Scipy Dependency Conflict

### Problem
Installing `boost` from conda pulled in `numpy 1.26.4`, which conflicted with pip-installed `numpy 2.4.6`, causing import errors in scipy and meeko.

**Error Messages:**
```
AttributeError: module 'numpy._globals' has no attribute '_signature_descriptor'
ImportError: numpy._core.multiarray failed to import
ImportError: cannot load module more than once per process
```

### Solution

1. **Removed conflicting versions:**
```bash
pip uninstall numpy scipy -y
conda remove numpy --force -y
```

2. **Reinstalled from pip only:**
```bash
pip install numpy==2.4.6 scipy==1.17.1
```

3. **Verification:**
```bash
python -c "import numpy, scipy; print(f'numpy: {numpy.__version__}'); print(f'scipy: {scipy.__version__}')"
# Output: numpy: 2.4.6, scipy: 1.17.1
```

### Documentation
Added troubleshooting section to SETUP.md (lines 203-229) with symptoms, cause, and solution.

---

## Part 8: PDB to PDBQT Conversion

### Challenge
Meeko (`mk_prepare_receptor.py`) failed with AlphaFold PDB files due to unusual bonding patterns at residues 24 and 150.

**Error:**
```
RuntimeError: Expected 2 paddings for (A:24, A:150) with bonds [(12, 1)], but got 0
```

### Solutions Attempted

1. **Meeko with various flags:** Failed (structural issues)
2. **RDKit conversion:** Failed (valence errors)
3. **ProDy + Simple conversion:** Partially successful
4. **OpenBabel:** ✅ **Success**

### Final Working Solution: OpenBabel

```bash
obabel -ipdb protein_folds/2_BcLipase_T217V_cleaned.pdb \
       -opdbqt \
       -O protein_folds/2_BcLipase_T217V.pdbqt \
       -xr  # rigid receptor
```

**Output:**
- File: `protein_folds/2_BcLipase_T217V.pdbqt`
- Size: 183 KB (2,349 lines)
- Atoms: 2,345 atoms
- Format: Valid PDBQT with proper atom types

**Warning received (safe to ignore):**
```
*** Open Babel Warning in PerceiveBondOrders
Failed to kekulize aromatic bonds
```
This is **normal and safe** for protein receptors - Vina doesn't use bond orders for receptors.

**Result:** File is ready for AutoDock Vina docking!

---

## Complete Environment State

### Conda Environment: `autodock`
- **Platform:** osx-64 (x86_64 via Rosetta 2 on Apple Silicon)
- **Python:** 3.12.11

### Command-Line Tools
- ✅ `vina` v1.2.5-mod (built from source)
- ✅ `mk_prepare_ligand.py` (from meeko)
- ✅ `mk_prepare_receptor.py` (from meeko)
- ✅ `obabel` (OpenBabel for format conversion)

### Python Packages (24 total)

**Molecular Docking & Structure:**
- vina 1.2.7 (Python bindings)
- meeko 0.7.1
- rdkit 2025.9.3
- prody 2.6.1
- biopython 1.87
- gemmi 0.7.5

**Web Interface:**
- Flask 3.0.0
- Jinja2 3.1.6
- Werkzeug 3.1.8
- click 8.4.1
- itsdangerous 2.2.0
- MarkupSafe 3.0.3
- blinker 1.9.0

**Scientific Computing:**
- numpy 2.4.6
- scipy 1.17.1
- Pillow 12.2.0

**Utilities:**
- pyparsing 3.1.1
- packaging 26.2

### Conda Packages (Build Dependencies)
- boost-cpp 1.78.0
- boost 1.78.0
- swig 4.2.0
- openblas
- blas

---

## Complete Workflow

### 1. Setup Environment (One-time)

**For Apple Silicon:**
```bash
softwareupdate --install-rosetta
CONDA_SUBDIR=osx-64 conda env create -f environment.yml
conda activate autodock

# Build vina from source (see SETUP.md for details)
# Then verify:
vina --version
```

**For Intel Mac/Linux:**
```bash
conda env create -f environment.yml
conda activate autodock
```

### 2. Select Mutation Sites (Web Interface)

```bash
python user_interface/app.py
# Open http://localhost:5001
# - Enter protein name
# - Paste sequence
# - Click positions to mutate
# - Save protein data
```

**Output:** `protein_squences/{protein_name}.json`

### 3. Generate Mutations

```bash
python src/mutation.py 2_BcLipase
```

**Output:** `protein_squences/2_BcLipase_mutations.json` (120 mutations)

### 4. Convert to FASTA Batches

```bash
python src/mutation_to_FASTA.py protein_squences/2_BcLipase_mutations.json
```

**Output:** 5 FASTA files in `protein_squences/2_BcLipase_FASTA/`
- `2_BcLipase_batch_001.fasta` (30 sequences)
- `2_BcLipase_batch_002.fasta` (30 sequences)
- `2_BcLipase_batch_003.fasta` (30 sequences)
- `2_BcLipase_batch_004.fasta` (30 sequences)
- `2_BcLipase_batch_005.fasta` (1 sequence)

### 5. Structure Prediction (ColabFold on Google Colab)

**5.1 Upload to Google Drive:**
Create: `/MyDrive/ColabFold/`
Upload: All batch FASTA files

**5.2 Open ColabFold Batch Notebook:**
https://colab.research.google.com/github/sokrypton/ColabFold/blob/main/batch/AlphaFold2_batch.ipynb

**5.3 Configure:**
```python
from google.colab import drive
drive.mount('/content/drive')

query_sequence = "/content/drive/MyDrive/ColabFold/2_BcLipase_batch_001.fasta"
jobname = "2_BcLipase_batch_001"
num_models = 5
num_recycle = 3
use_amber = True
```

**5.4 Run:** Runtime → Run all (3-6 hours per batch)

**5.5 Output:** PDB files saved to Google Drive
- `*_rank_001_*.pdb` - Best model (use this)
- `*_scores_*.json` - Confidence metrics
- `*_pae_*.png` - Error prediction plot

**5.6 Repeat:** Process each batch file separately

### 6. Prepare for AutoDock Docking

**Download PDB files from Google Drive**

**Convert to PDBQT:**
```bash
# Clean PDB first (if needed)
obabel -ipdb protein_folds/structure.pdb \
       -opdb \
       -O protein_folds/structure_clean.pdb

# Convert to PDBQT
obabel -ipdb protein_folds/structure_clean.pdb \
       -opdbqt \
       -O protein_folds/receptor.pdbqt \
       -xr
```

**Prepare ligand (if needed):**
```bash
mk_prepare_ligand.py -i ligand.mol2 -o ligand.pdbqt
```

### 7. Run AutoDock Vina

```bash
vina --receptor protein_folds/receptor.pdbqt \
     --ligand ligand.pdbqt \
     --center_x 15.190 \
     --center_y 53.903 \
     --center_z 16.917 \
     --size_x 20 \
     --size_y 20 \
     --size_z 20 \
     --out result.pdbqt \
     --exhaustiveness 8
```

**Output:** `result.pdbqt` with docked poses ranked by binding energy

---

## Batch Processing Timeline

For 6 mutation positions (120 mutations total):

| Step | Time | Output |
|------|------|--------|
| Select positions (web) | 5 min | `.json` file |
| Generate mutations | <1 min | `_mutations.json` |
| Convert to FASTA | <1 min | 5 FASTA files |
| Upload to Drive | 5 min | - |
| ColabFold batch 1 | 3-6 hrs | 30 PDB files |
| ColabFold batch 2 | 3-6 hrs | 30 PDB files |
| ColabFold batch 3 | 3-6 hrs | 30 PDB files |
| ColabFold batch 4 | 3-6 hrs | 30 PDB files |
| ColabFold batch 5 | 1-2 hrs | 1 PDB file |
| Convert to PDBQT | 5 min | 121 PDBQT files |
| **Total** | **1-2 days** | **121 structures** |

---

## Key Files and Locations

### Documentation
- `README.md` - Main documentation with complete workflow
- `SETUP.md` - Detailed setup guide with troubleshooting
- `src/README_mutation_to_FASTA.md` - FASTA conversion guide

### Configuration
- `requirements.txt` - Pip packages for manual install
- `environment.yml` - Complete environment (conda + pip)
- `backup_requirements.txt` - Current state with notes

### Scripts
- `user_interface/app.py` - Flask web server (port 5001)
- `src/mutation.py` - Generate mutations
- `src/mutation_to_FASTA.py` - Convert to FASTA batches

### Data
- `protein_squences/{name}.json` - Original protein + selected positions
- `protein_squences/{name}_mutations.json` - All mutations
- `protein_squences/{name}_FASTA/` - FASTA batch files

---

## Troubleshooting Reference

### AutoDock Vina Issues

**"bad CPU type in executable":**
- Bioconda package is broken (i386/PowerPC binary)
- Solution: Build from source (see SETUP.md)

**"Boost library is not installed":**
```bash
conda install -c conda-forge boost-cpp swig
```

### Numpy/Scipy Issues

**Import errors with numpy:**
```bash
pip uninstall numpy scipy -y
conda remove numpy --force -y
pip install numpy==2.4.6 scipy==1.17.1
```

### Meeko/PDBQT Issues

**mk_prepare_receptor.py fails:**
- Use OpenBabel instead:
```bash
obabel -ipdb input.pdb -opdbqt -O output.pdbqt -xr
```

**"Failed to kekulize aromatic bonds" warning:**
- Safe to ignore for protein receptors
- Vina doesn't use bond orders

### Google Colab Issues

**Runtime disconnects:**
- Colab free tier has 12-hour limit
- Keep browser tab open
- Don't idle for >90 minutes

**GPU not available:**
- Free tier has dynamic limits
- Wait and try again later
- Consider Colab Pro ($10/month)

---

## Important Notes

### For Apple Silicon Users
1. **Rosetta 2 required** for vina binary (x86_64)
2. **Environment must use osx-64** architecture
3. **Vina must be built from source** (bioconda package broken)

### For All Users
1. **Numpy must be pip version** (2.4.6), not conda version
2. **Boost installation may pull conda numpy** - reinstall pip numpy if needed
3. **ColabFold is recommended** over local AlphaFold (much easier setup)
4. **FASTA batch size of 30** is optimal for Colab's 12-hour limit

### Production Recommendations
1. **Use rank_001 models** from ColabFold (highest confidence)
2. **Check pLDDT scores** in JSON files (>70 is good)
3. **OpenBabel for PDBQT conversion** works better than meeko for AlphaFold PDBs
4. **Test docking parameters** on a few structures before running full batch

---

## Future Improvements

### Potential Enhancements
1. Automate ColabFold submission (currently manual)
2. Add charge calculation to PDBQT conversion
3. Batch PDBQT conversion script for all structures
4. Automated docking script for all mutations
5. Results analysis and visualization

### Known Limitations
1. ColabFold requires manual notebook interaction
2. OpenBabel PDBQT has zero charges (acceptable for Vina)
3. Meeko incompatible with some AlphaFold structures
4. Google Colab free tier has usage limits

---

## References

### Documentation
- ColabFold: https://github.com/sokrypton/ColabFold
- AlphaFold: https://github.com/google-deepmind/alphafold
- AutoDock Vina: http://autodock.scripps.edu/
- AlphaFold Database API: https://alphafold.ebi.ac.uk/api-docs

### Papers
- ColabFold: https://www.nature.com/articles/s41592-022-01488-1
- AlphaFold 2: https://www.nature.com/articles/s41586-021-03819-2
- AutoDock Vina: https://doi.org/10.1002/jcc.21334

---

## Session Statistics

**Files Created/Modified:** 8
- README.md (updated)
- SETUP.md (new)
- environment.yml (new)
- requirements.txt (updated)
- backup_requirements.txt (updated)
- src/mutation_to_FASTA.py (new)
- src/README_mutation_to_FASTA.md (new)
- SESSION_SUMMARY.md (this file)

**Lines of Code:** ~500
**Lines of Documentation:** ~1,100
**Packages Installed:** 24
**Binaries Compiled:** 1 (vina)
**Issues Resolved:** 3 major (vina install, numpy conflict, PDB conversion)

---

**End of Session Summary**
