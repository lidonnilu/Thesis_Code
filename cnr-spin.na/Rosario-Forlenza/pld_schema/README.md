# PLD-MODA Schema Plugin

This folder contains the core schema developed for the plugin `nomad-plugin-pld-moda`, designed to enable FAIR data management for Pulsed Laser Deposition (PLD) experiments performed at the MODA laboratory (CNR-SPIN Naples), in compliance with the NOMAD metadata infrastructure.

## Description

The schema includes:
- a **main section** for the description of PLD fabrication processes;
- a **subsection for uploading RHEED images**, acquired during the deposition;
- a **subsection for loading RHEED intensity data** from `.csv` files, with automated validation and interactive plot generation using Plotly.

These schema components are integrated into a NOMAD-compatible plugin that extends the  [`fabrication-utilities`] plugin (https://github.com/Trog-404/Fabrication-utilities).

## Repository and integration

The full plugin `nomad-plugin-pld-moda`, which includes this schema, is available at:

🔗 https://github.com/RosarioForlenza/nomad-plugin-pld-moda

A ready-to-use NOMAD development distribution ('nomad-FAIR') with this plugin and its required submodule `fabrication-utilities` already integrated is available at:

🔗 https://github.com/RosarioForlenza/nomad-distro-dev-moda

## Files

- `__init__.py`: entry points and plugin registration
- `pld_schema.py`: definition of the PLD schema and RHEED subsections

## License

This code is released under the MIT License (see LICENSE file).
