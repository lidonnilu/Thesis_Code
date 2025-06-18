This repo contains the contributions related to E. Molteni's MDMC internship work 
on adding functionalities to some NOMAD parsers for electronic structure codes.
See also MDMC master thesis "Extending NOMAD schemas for the UMIL NFFA-DI Theory &
Simulation Installation, with a focus on the Yambo code", DOI: 10.5281/zenodo.15691481

# Note: 
The NOMAD parsers named parser.py mentioned below, part of NOMAD electronic-parsers, 
can only run within the NOMAD platform (https://nomad-lab.eu/nomad-lab/) or on a local NOMAD Oasis (https://nomad-lab.eu/nomad-lab/nomad-oasis.html), in both of which also the .../electronic-parsers/tree/develop/tests folder is present.
Our modified versions only run within a local Oasis (until they will be merged, after successful Pull Requests, into the NOMAD platform).

These parsers can be run, on the corresponding Yambo or Siesta files, either:

a) by making an upload of Yambo or Siesta data such ad the ones contained in this repo,
to the standard NOMAD or to an Oasis opened on a web browser 

b) without the use of the GUI, locally, by command line, on a computer where an Oasis is installed, by:
uv run nomad parse path/mainfile  --> this is mainly useful for debugging aims: data
are not visualized, but one can inspect the output of the parsing process in test format
(to check which quantities are parsed) and possible error messages.
("path" is the complete path of the mainfile, and "mainfile" is its name)

Notice that in both cases the file to be parsed (in (a) this is done automatically by NOMAD,
in (b) it must be specified in the command) is the "mainfile" (which is a r* file for Yambo, a *.out file for Siesta), 
also in those cases where the data we are interested in are in a different file
(a o* file for Yambo spectra, the ns.db file for Yambo coordinates, the dos file for Siesta DOS).

Our Spectra_plotting_EMvers_forgithubrepo.ipynb in the /Yambo_spectra folder 
instead can be run on a jupyterlab installed on a computer where a local Oasis is present:
indeed it imports and uses some of NOMAD classes and quantities.  



Content of this repo:

# /Yambo_atom_coords: Fixing NOMAD issues in the parsing and writing/displaying of chemical composition, 
# atom coordinates, simulation cell

For this implementation, we have made a Pull Request on the NOMAD github repo:
https://github.com/nomad-coe/electronic-parsers/pull/286

See also related information, specifically on the need of having a ns.db file within a /SAVE subfolder 
in Yambo uploads in order for NOMAD to be able to parse and display chemical composition, atom coordinates, simulation cell:
a) NOMAD GitHub, in the Issues section for electronic-parsers: https://github.com/nomad-coe/electronic-parsers/issues:
  Issues: "Add warning to yambo parser when ns.db file is not present", "Add search for ns.db file in Yambo when not in default folder"
b) my detailed Discord thread on this subject, to which (a) is pointing: https://discord.com/channels/1201445470485106719/1208029192881442866/threads/1351201658440519761


Content of /Yambo_atom_coords folder: 

* parser.py (from https://github.com/emolteni/electronic-parsers/tree/develop/electronicparsers/yambo): 
modified NOMAD Yambo parser where I have fixed an issue about a mismatch between 
total number of coordinates and total number of atoms, due to NOMAD incorrectly using the Yambo 
max_n_atoms variable (maximum of the numbers of atoms of all the chemical species present in the system)
instead of the n_atoms one (actual number of atoms of a given chemical species) for allocating
the number of lines for the atom coordinates of each chemical species.

The corresponding standard NOMAD parser, yielding n. atoms / n. coordinates mismatch errors
for systems with different number of atoms of different chemical species,
 is:  https://github.com/nomad-coe/electronic-parsers/tree/develop/electronicparsers/yambo/parser.py

* /CH4_db_minimal (from https://github.com/emolteni/electronic-parsers/tree/develop/tests/data/yambo): 
our "minimal" test folder (containing also a ns.db file within a /SAVE subfolder) for the NOMAD electronic-parsers/test/data/yambo folder, 
for the above-mentioned implementation regarding atom coordinates; r_setup is the yambo mainfile.

The corresponding general NOMAD test folder for Yambo (without our contribution) is:
https://github.com/nomad-coe/electronic-parsers/tree/develop/tests/data/yambo

* test_yamboparser.py (from https://github.com/emolteni/electronic-parsers/tree/develop/tests):
file for running all the NOMAD yambo tests present in https://github.com/emolteni/electronic-parsers/tree/develop/tests/data/yambo,
where I have added the part (test_5) regarding our test folder /CH4_db_minimal.

The corresponding standard NOMAD version (without our contribution) is: https://github.com/nomad-coe/electronic-parsers/tree/develop/tests/test_yamboparser.py


# /Yambo_spectra: adding spectra parsing (and plotting) functionality in the NOMAD Yambo parser 

* Spectra_plotting_EMvers_forgithubrepo.ipynb: our local parser for Yambo spectra only.
Allows for yambo spectra files as o* files with either 3 or 5 columns of data,
using a regular expression such as to match the various possible formats of spectra headers, i.e.:
E/ev[1]            ALPHA-Im[2]        ALPHA-Re[3]        (ALPHAo-Im[4]       ALPHAo-Re[5])
or
E/ev[1]            EPS-Im[2]          EPS-Re[3]          (EPS-Im[4]          EPS-Re[5])
where I have indicated with (.....)  those columns which are not always present.

The columns to be plotted are the first (column 0 according to python, excitation energies) 
and the second (column 1 according to python,  intensities).

This version works on jupyterlab;  our version of the NOMAD Yambo parser containing this part for specctra (adapted for the NOMAD platform) does not work yet in our Oasis 
(no warning, no error messages, yet no spectra plotted), possibly due to issues on which subparser to use
in order to parse the correct file, which is a o* file, not a r* mainfile.
The fact that our local version of the parser works should ensure that the parts about 
matching the specific formats of the headers and columns of data in the file are correct. 

* o-R_methylox_TDLDA.alpha_q1_slepc_alda_bse: test Yambo spectrum file to be parsed

The corresponding standard NOMAD parser is:  https://github.com/nomad-coe/electronic-parsers/tree/develop/electronicparsers/yambo/parser.py


# /Siesta_DOS: adding electronic Density of States (DOS) parsing (and plotting) functionality in the NOMAD Siesta parser 
This implementation already works on our Oasis; we have not made a Pull Request yet on the NOMAD github repo,
since we are planning to implement the plotting of Siesta band structures too.

* parser.py:  modified NOMAD Siesta parser, implementing the parsing of DOS outputs.
  
The corresponding standard NOMAD parser is: https://github.com/nomad-coe/electronic-parsers/tree/develop/electronicparsers/siesta/parser.py

* /Siesta_DOS_bands_data: test folder with a Siesta DOS + band structure run:
  siesta.out is the Siesta mainfile;  dos is the DOS file.
  As explained in my thesis, with our modified parser the DOS parsing and plotting is working,
  although not being yet able to find the Fermi energy value.
  We are using a folder with band structure data also (which currently are not plotted),
  mainly in view of using it later to test our planned implementation of band structure parsing too. 





