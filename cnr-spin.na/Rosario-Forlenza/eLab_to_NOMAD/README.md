# eLab_to_NOMAD.py

This folder contains the script `eLab_to_NOMAD.py`, developed during a research internship at the MODA laboratory (CNR-SPIN Naples), with the aim of facilitating the FAIR conversion of experimental data from eLabFTW into the NOMAD metadata format.

---

# Description

'eLab_to_NOMAD.py is a parser developed during an internship at the MODA laboratory, aimed at extracting experimental data related to the PLD fabrication process and in situ monitoring via RHEED, starting from the eLabFTW instance used in the lab.
The program maps this data into an 'archive.json' file compliant with NOMAD ontologies, converts RHEED measurement data into .csv format, and enables the automatic upload of these dato to NOMAD - including RHEED images and intensity files - by creating a new entry compatible with the 'PLDProcess' schema defined in the plugin [nomad-plugin-pld-moda](https://github.com/Rosario-Forlenza/nomad-plugin-pld-moda).

---

## Main Features

- Parses the `.zip` file exported from an eLabFTW experiment
- Extracts metadata and attached files
- Maps data to a valid `archive.json` file compatible with NOMAD ontologies
- Converts RHEED intensity data into `.csv` format
- Generates plots and assigns metadata to the appropriate PLDProcess schema sections
- Asks the user for minimal input (entry name, proposal ID, affiliation)
- Uploads the `.zip` archive to NOMAD using `curl`

---

## Requirements

- Python 3.8+
- The script only uses Python’s built-in standard libraries:
  `json`, `csv`, `glob`, `os`, `zipfile`, `io`, `subprocess`, `datetime`

---

## Related projects

- [`nomad-plugin-pld-moda`](https://github.com/Rosario-Forlenza/nomad-plugin-pld-moda): repository containing the NOMAD plugin made for PLD and RHEED data.
- [`nomad-FAIR-dev`](https://github.com/Rosario-Forlenza/nomad-FAIR-dev): development distribution of NOMAD with this plugin integrated.

---

## License

This code is released under the MIT License — see the [LICENSE](./LICENSE) file for details.
