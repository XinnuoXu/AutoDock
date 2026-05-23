# AutoDock Environment Setup Guide

This guide covers setting up the AutoDock environment on different systems, including Apple Silicon Macs.

---

## For Apple Silicon Macs (M1/M2/M3)

AutoDock Vina is compiled for x86_64 (Intel) architecture. On Apple Silicon, you need to create an x86_64 conda environment that runs via Rosetta 2.

### Step 1: Install Rosetta 2 (if not already installed)

```bash
softwareupdate --install-rosetta
```

### Step 2: Create x86_64 Conda Environment

```bash
# Create environment with x86_64 architecture
CONDA_SUBDIR=osx-64 conda create -n autodock python=3.12

# Activate environment
conda activate autodock

# Force environment to use x86_64 packages
conda config --env --set subdir osx-64
```

### Step 3: Install Conda Packages

```bash
# Add required channels
conda config --add channels conda-forge
conda config --add channels bioconda

# Install conda packages
conda install -c conda-forge boost-cpp=1.78.0 swig=4.2.0
conda install -c bioconda autodock-vina=1.1.2
```

### Step 4: Install Python Packages

```bash
pip install -r requirements.txt
```

### Step 5: Verify Installation

```bash
# Check vina command-line tool
vina --version

# Check Python vina
python -c "import vina; print('Python vina installed successfully')"

# Check Flask
python -c "import flask; print('Flask installed successfully')"

# Check rdkit
python -c "import rdkit; print('RDKit installed successfully')"
```

---

## For Intel Macs / Linux

### Step 1: Create Conda Environment

```bash
# Create environment
conda create -n autodock python=3.12
conda activate autodock
```

### Step 2: Install from environment.yml

```bash
# Using environment.yml (recommended)
conda env create -f environment.yml
conda activate autodock
```

OR manually:

```bash
# Add channels
conda config --add channels conda-forge
conda config --add channels bioconda

# Install conda packages
conda install -c conda-forge boost-cpp swig
conda install -c bioconda autodock-vina

# Install pip packages
pip install -r requirements.txt
```

---

## Alternative: Using environment.yml

The easiest way to recreate the exact environment:

```bash
# Create environment from yml file
conda env create -f environment.yml

# Activate
conda activate autodock

# Verify
vina --version
python user_interface/app.py
```

---

## Package List

### Web Interface
- **Flask 3.0.0** - Web framework
- **Jinja2** - Templating engine
- **Werkzeug** - WSGI utilities

### Molecular Docking Tools
- **autodock-vina 1.1.2** - Command-line docking tool (conda)
- **vina 1.2.7** - Python bindings for AutoDock Vina
- **meeko 0.7.1** - Molecule preparation for AutoDock
- **rdkit 2025.9.3** - Cheminformatics toolkit
- **prody 2.6.1** - Protein structure analysis
- **biopython 1.87** - Biological computation
- **gemmi 0.7.5** - Macromolecular crystallography

### Scientific Computing
- **numpy 2.4.6** - Numerical computing
- **scipy 1.17.1** - Scientific computing
- **Pillow 12.2.0** - Image processing

### Build Dependencies
- **boost-cpp 1.78.0** - C++ libraries (required for vina)
- **swig 4.2.0** - Interface compiler (required for vina)
- **openblas** - Linear algebra library

---

## Troubleshooting

### "bad CPU type in executable: vina" (Apple Silicon)

The bioconda vina package (v1.1.2) has an outdated binary (i386/PowerPC) that doesn't work on modern Macs. The solution is to build vina from source.

**Already fixed in this repository!** The vina binary in the environment was built from source (v1.2.5) and includes the proper rpath to conda libraries.

If you need to rebuild:

```bash
conda activate autodock

# Clone and build AutoDock Vina
cd /tmp
git clone --depth 1 --branch v1.2.5 https://github.com/ccsb-scripps/AutoDock-Vina.git
cd AutoDock-Vina/build/mac/release

# Create Makefile pointing to conda libraries
cat > Makefile << 'EOF'
BASE=$(CONDA_PREFIX)
BOOST_VERSION=
BOOST_INCLUDE = $(BASE)/include
C_PLATFORM=-pthread
GPP=clang++
C_OPTIONS= -O3 -DNDEBUG -std=c++11 -fvisibility=hidden
BOOST_LIB_VERSION=
BOOST_STATIC=n
BOOST_LIB_PATH=$(BASE)/lib

include ../../makefile_common
EOF

# Build with x86_64 architecture
arch -x86_64 make

# Add rpath so it finds conda boost libraries
install_name_tool -add_rpath $CONDA_PREFIX/lib vina

# Install to conda environment
cp vina $CONDA_PREFIX/bin/vina
chmod +x $CONDA_PREFIX/bin/vina

# Test
vina --version
```

### "Boost library is not installed"

Install boost-cpp via conda before installing vina:

```bash
conda install -c conda-forge boost-cpp swig
pip install vina
```

### Numpy/Scipy Import Errors (AttributeError, ImportError)

**Symptoms:**
- `AttributeError: module 'numpy._globals' has no attribute '_signature_descriptor'`
- `ImportError: numpy._core.multiarray failed to import`
- `ImportError: cannot load module more than once per process`

**Cause:** Conflict between conda-installed numpy (1.26.4 from boost dependency) and pip-installed numpy (2.4.6).

**Solution:**

```bash
conda activate autodock

# Remove both versions
pip uninstall numpy scipy -y
conda remove numpy --force -y

# Reinstall from pip only
pip install numpy==2.4.6 scipy==1.17.1

# Verify
python -c "import numpy, scipy; print(f'numpy: {numpy.__version__}'); print(f'scipy: {scipy.__version__}')"
# Should show: numpy: 2.4.6, scipy: 1.17.1
```

**Note:** When conda installs `boost`, it may pull in numpy 1.26.4 as a dependency. The pip-installed numpy 2.4.6 should override it, but if conflicts occur, use the solution above.

### "command not found: vina"

Install the command-line tool via conda:

```bash
conda install -c bioconda autodock-vina
```

### Port 5001 already in use

Change the port in `user_interface/app.py` or kill the existing process:

```bash
lsof -i :5001
kill -9 <PID>
```

---

## Environment Export

To export your current environment for sharing:

```bash
# Export to YAML (recommended)
conda env export > environment.yml

# Export to requirements.txt (pip only)
pip freeze > requirements.txt

# Export conda packages list
conda list --export > conda_packages.txt
```

---

## Starting Fresh

If you need to completely recreate the environment:

```bash
# Remove old environment
conda deactivate
conda env remove -n autodock

# For Apple Silicon:
CONDA_SUBDIR=osx-64 conda env create -f environment.yml

# For Intel/Linux:
conda env create -f environment.yml

# Activate and verify
conda activate autodock
vina --version
python user_interface/app.py
```

---

## Quick Reference

| Command | Purpose |
|---------|---------|
| `conda activate autodock` | Activate environment |
| `conda deactivate` | Deactivate environment |
| `conda list` | List installed packages |
| `conda env list` | List all environments |
| `pip list` | List pip packages |
| `vina --version` | Check AutoDock Vina version |
| `python user_interface/app.py` | Start web server |

---

## System Requirements

- **Python**: 3.12 (tested)
- **Operating System**: macOS (Apple Silicon or Intel), Linux
- **RAM**: 4GB minimum, 8GB+ recommended
- **Disk Space**: ~2GB for environment and dependencies
- **For Apple Silicon**: Rosetta 2 required

---

## Notes

1. **Apple Silicon Users**: The environment runs in x86_64 mode via Rosetta 2 for compatibility with AutoDock Vina
2. **RDKit**: May take several minutes to install due to compilation
3. **AutoDock Vina**: Two versions are installed:
   - Command-line tool (`vina` command) from bioconda
   - Python bindings (`import vina`) from PyPI
4. **Conda Channels**: Order matters - conda-forge and bioconda must be added

---

## License

[Add your license information]

## Support

For issues related to:
- **AutoDock Vina**: https://github.com/ccsb-scripps/AutoDock-Vina
- **RDKit**: https://github.com/rdkit/rdkit
- **Meeko**: https://github.com/forlilab/Meeko
- **This project**: [Add your repository URL]
