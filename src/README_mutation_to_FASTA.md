# Mutation to FASTA Converter

This script converts mutation JSON files to FASTA format for batch protein structure prediction with AlphaFold/ColabFold.

## Features

- ✅ Converts mutation JSON files to FASTA format
- ✅ Automatically splits sequences into batches of 30 (optimal for Google Colab)
- ✅ Includes original sequence in the first batch
- ✅ Organized output by protein name
- ✅ Processes single files or entire directories
- ✅ Clear naming convention with batch numbers

## Usage

### Process a Single Mutation File

```bash
python src/mutation_to_FASTA.py protein_squences/test_protein_mutations.json
```

### Process All Mutation Files in a Directory

```bash
python src/mutation_to_FASTA.py protein_squences/
```

### Custom Batch Size

```bash
python src/mutation_to_FASTA.py protein_squences/test_protein_mutations.json 50
```

## Input Format

The script expects JSON files with the following structure:

```json
{
  "protein_name": "test_protein",
  "original_sequence": "MADNYAATRYP...",
  "mutation_positions": [5, 12, 23],
  "total_mutations": 120,
  "mutations": [
    {
      "position": 5,
      "original_aa": "A",
      "mutated_aa": "R",
      "mutation_code": "A5R",
      "mutated_sequence": "MADNYRATRYP..."
    },
    ...
  ]
}
```

## Output Structure

```
protein_squences/
├── {protein_name}_FASTA/
│   ├── {protein_name}_batch_001.fasta  (30 sequences: original + 29 mutations)
│   ├── {protein_name}_batch_002.fasta  (30 sequences)
│   ├── {protein_name}_batch_003.fasta  (30 sequences)
│   └── ...
```

## Output FASTA Format

Each FASTA file contains sequences in the following format:

```fasta
>test_protein_original
MADNYAATRYPIILVHGLTGTDKYAGVLEYWYGIQEDLQQRGATVYVANLSGFQSDDGPN...

>test_protein_A5R
MADNYRATRYPIILVHGLTGTDKYAGVLEYWYGIQEDLQQRGATVYVANLSGFQSDDGPN...

>test_protein_A5N
MADNYNATRYPIILVHGLTGTDKYAGVLEYWYGIQEDLQQRGATVYVANLSGFQSDDGPN...
```

## Example Output

```bash
$ python src/mutation_to_FASTA.py protein_squences/test_protein_mutations.json

Processing: protein_squences/test_protein_mutations.json
Protein: test_protein
Total mutations: 120
Mutation positions: [5, 12, 23, 45, 67, 89]
Output directory: protein_squences/test_protein_FASTA
Created: protein_squences/test_protein_FASTA/test_protein_batch_001.fasta (30 sequences)
Created: protein_squences/test_protein_FASTA/test_protein_batch_002.fasta (30 sequences)
Created: protein_squences/test_protein_FASTA/test_protein_batch_003.fasta (30 sequences)
Created: protein_squences/test_protein_FASTA/test_protein_batch_004.fasta (30 sequences)
Created: protein_squences/test_protein_FASTA/test_protein_batch_005.fasta (1 sequences)
✓ Created 5 FASTA batch file(s)
```

## Using with Google Colab ColabFold

1. **Generate FASTA files**:
   ```bash
   python src/mutation_to_FASTA.py protein_squences/
   ```

2. **Upload to Google Drive**:
   - Create folder: `/MyDrive/ColabFold/`
   - Upload batch files one at a time

3. **Open ColabFold Batch Notebook**:
   https://colab.research.google.com/github/sokrypton/ColabFold/blob/main/batch/AlphaFold2_batch.ipynb

4. **Configure and Run**:
   ```python
   query_sequence = "/content/drive/MyDrive/ColabFold/test_protein_batch_001.fasta"
   jobname = "test_protein_batch_001"
   num_models = 5
   ```

5. **Repeat for each batch file**

## Tips

- **Batch Size**: 30 sequences is optimal for Google Colab's 12-hour runtime limit
- **Runtime**: Each batch of ~200 residue proteins takes ~3-6 hours with 5 models
- **Storage**: Keep batch files organized by protein name
- **Naming**: Mutation codes (e.g., A5R) are preserved in sequence IDs

## Troubleshooting

### "No mutations found"
Check that your JSON file has the `mutations` array populated.

### "Invalid batch size"
Ensure the batch size argument is a positive integer.

### Permission errors
Make sure the `protein_squences/` directory is writable.

## Integration with AutoDock Pipeline

After structure prediction:

1. Download predicted PDB files from Colab
2. Use the highest-ranked models (`*_rank_001_*.pdb`)
3. Prepare for AutoDock docking:
   - Remove water molecules if needed
   - Add hydrogens
   - Calculate charges
   - Define binding sites

## Related Files

- `mutation_to_FASTA.py` - Main conversion script
- `protein_squences/*_mutations.json` - Input mutation files
- `protein_squences/*_FASTA/` - Output FASTA batches
