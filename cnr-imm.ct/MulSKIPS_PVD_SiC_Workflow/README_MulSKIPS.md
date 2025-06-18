
Outputs include:
- Growth rate (spline, polyfit, finite diff.)
- Surface roughness (microns)
- Vacancy statistics (SV, CV, SAV, CAV, XV)

### 3. Generate FAIR NeXus Output

Run `Parser_May_2.ipynb` to:
- Parse `surf_height.txt`, `results.txt`, and `.xyz` files
- Generate `.nxs` file with metadata and results
- Use FAIRmat schemas `NXmicrostructure_imm_config` and `NXmicrostructure_imm_results`

> Note: FAIRmat may classify `.nxs` files as "Experiment" by default, but this output is from a simulation.

## Output Files

| File              | Description                              |
| ----------------- | ---------------------------------------- |
| `results.txt`     | Growth rate, roughness, vacancy data     |
| `runlog.txt`      | Simulation log                           |
| `surf_height.txt` | Surface height over time                 |
| `I*.xyz`          | Atomic configurations at each timestep   |
| `*.nxs`           | FAIRmat-compliant NeXus file             |

## Citation

If you use this workflow, please cite:
- MulSKIPS: Fisicaro et al., *Phys. Rev. Materials* 4, 2020
- FAIRmat: Wilkinson et al., *Scientific Data* 3, 2016

A `bibtex.bib` file with full references is available in the repository.

## License

Licensed under the MIT License. See the `LICENSE` file.

## Acknowledgements

Developed as part of the FAIR data initiative for materials science:
- CNR-IMM@CT — https://www.imm.cnr.it/
- FAIRmat Project — https://www.fairmat-nfdi.eu/

