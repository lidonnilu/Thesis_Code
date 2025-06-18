This repo contains the code written during the MDMC internship.

> ⚠️ **Note:** 
See https://github.com/Trog-404/Fabrication-utilities for the NOMAD plugin used in this facility.

> ⚠️ **Note:** 
See 10.5281/zenodo.15678583 for the thesis work to find more details.



# official.py

official.py contains the program used to compile and modify json files in a user friendly way.
It is also the only python file that may run standalone, since all of the following are part of a greater ecosystem, and are here only for sharing purposes.

# BUTTON_UPLOAD_FAIR.py

BUTTON_UPLOAD_FAIR.py contains the functions in the backend of CAMS, the CNR-ISMN's LIMS, that make possible to extract all the data from a process and send it to NOMAD. It calls the two files descripted below.
The backend is built on jam.py framework, hence this function might work on different infrastructure after several adjustments.

# cams2nomad.py

cams2nomad.py is the the dictionary containing the mapping between the CAMS parameters and the NOMAD keys. It facilitates the name conversion, and keeps the logic code clean.
This module houses a dictionary entry for each CAMS step type, each containing three fields:

1. **`m_def`** – This unambiguously links a CAMS step type to its corresponding NOMAD class. Several CAMS step types can map to the same NOMAD class thanks to their shared generalization.

2. **`mapping`** – A sub-dictionary pairing NOMAD field names with their CAMS counterparts. During conversion, for each pair, the code retrieves the value under the CAMS key and assigns it to the appropriate NOMAD key.

3. **`transformations`** – Another sub-dictionary that assigns a transformation function to specific NOMAD keys. When the raw CAMS value requires unit conversion or type casting to meet NOMAD standards, the function is applied before assignment.

# API_collection.py

API_collection.py gathers a series of function for the real upload of a file to NOMAD. It manages data exchanging between a client and the NOMAD server, exploiting its APIs.

### NOMAD Upload Plugin for CAMS

NOMAD provides a set of example Python utilities that streamline data‑upload workflows, making them easy to automate and integrate within existing Python pipelines.  
After minor tweaks—mainly stronger exception handling—these utilities were merged into a single **plugin file** that the CAMS backend can import directly.  
Once your data are extracted, one simple call to this plugin handles the entire upload‑and‑publish sequence, keeping backend code clean and well‑organized.



#### Core Functions

| Function | Purpose |
|----------|---------|
| **`get_authentication_token`** | Authenticates against the NOMAD API with a username and password and returns the access token needed for all subsequent requests. Includes robust HTTP and connection‑error handling. |
| **`upload_to_NOMAD`** | Uploads a file (or compressed archive) to NOMAD. The repository automatically decompresses and processes archives. |
| **`check_upload_status`** | Queries the current processing state of a given `upload_id`, allowing you to track progress or detect failures. |
| **`wait_for_upload_completion`** | Polls `check_upload_status` at fixed intervals until processing succeeds or a timeout occurs—ideal for unattended workflows. |
| **`get_upload_entries`** | After a successful upload, retrieves the list of processed entries (file names, entry IDs, and other metadata) and returns them as a dictionary. |
| **`delete_upload`** | Removes an upload from NOMAD—handy for cleaning up failed or unneeded data. All request‑related exceptions are handled gracefully. |
| **`upload_file`** | **High‑level pipeline coordinator.** Performs authentication, upload, status waiting, entry retrieval, and optional cleanup. This is the main entry point invoked by the CAMS backend. |
| **`publish_upload`** | Makes a completed upload publicly visible in the NOMAD repository. |

---
