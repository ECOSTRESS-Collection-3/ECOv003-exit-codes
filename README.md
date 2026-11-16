# ECOv003-exit-codes

Standardized integer exit codes and exception classes for **ECOSTRESS Collection 3** Product Generation Executables (PGEs), developed at NASA's Jet Propulsion Laboratory (JPL).

## Overview

In the ECOSTRESS Collection 3 Science Data System (SDS), Product Generation Executables—such as [`ECOv003-L2T-STARS`](https://github.com/ECOSTRESS-Collection-3/ECOv003-L2T-STARS) and [`ECOv003-L3T-L4T-JET`](https://github.com/ECOSTRESS-Collection-3/ECOv003-L3T-L4T-JET)—run as standalone command-line processes orchestrated by a workflow scheduler.

`ECOv003-exit-codes` provides a lightweight, zero-dependency shared contract between PGEs and the SDS orchestrator by pairing integer OS exit codes (`0`–`18`) with a structured Python exception hierarchy rooted at `ECOSTRESSExitCodeException`. This allows the scheduler to distinguish normal completions, expected scientific/spatial filters (e.g., nighttime or ocean-only tiles), transient auxiliary data latency requiring a scheduled retry, and unrecoverable errors.

## Author

**Gregory H. Halverson**  
[gregory.h.halverson@jpl.nasa.gov](mailto:gregory.h.halverson@jpl.nasa.gov)  
NASA Jet Propulsion Laboratory, California Institute of Technology

## Installation

Install from PyPI:

```bash
pip install ECOv003-exit-codes
```

Or install from a local clone for development:

```bash
pip install -e ".[dev]"
```

**Requirements:** Python $\ge$ 3.10 (no third-party runtime dependencies).

## Usage

### Raising Exit-Code Exceptions in PGE Modules

Raise the specific `ECOSTRESSExitCodeException` subclass corresponding to the failure or filter condition encountered:

```python
from os.path import exists
from ECOv003_exit_codes import (
    InputFilesInaccessible,
    LandFilter,
    AuxiliaryLatency,
    BlankOutput,
)

def validate_inputs(l2t_lste_path: str, is_land: bool) -> None:
    if not exists(l2t_lste_path):
        raise InputFilesInaccessible(f"L2T_LSTE file not found: {l2t_lste_path}")

    if not is_land:
        raise LandFilter("Scene rejected: tile contains no land pixels")
```

### Handling Exceptions at the PGE CLI Entry Point

Catch `ECOSTRESSExitCodeException` at the top level of your PGE entry point to map exceptions directly to their standardized integer return code:

```python
import sys
import logging
from ECOv003_exit_codes import (
    SUCCESS_EXIT_CODE,
    UNCLASSIFIED_FAILURE_EXIT_CODE,
    RUNCONFIG_FILENAME_NOT_SUPPLIED,
    ECOSTRESSExitCodeException,
)

logger = logging.getLogger(__name__)

def run_pge(runconfig_filename: str) -> int:
    try:
        # Execute PGE workflow...
        return SUCCESS_EXIT_CODE
    except ECOSTRESSExitCodeException as exc:
        logger.error(f"PGE exited with code {exc.exit_code}: {exc}")
        return exc.exit_code
    except Exception as exc:
        logger.exception(f"Unhandled error: {exc}")
        return UNCLASSIFIED_FAILURE_EXIT_CODE

def main(argv: list[str] | None = None) -> int:
    args = sys.argv[1:] if argv is None else argv
    if not args:
        return RUNCONFIG_FILENAME_NOT_SUPPLIED
    return run_pge(args[0])

if __name__ == "__main__":
    sys.exit(main())
```

## Exit Codes & Exceptions Reference

All custom exceptions inherit from `ECOSTRESSExitCodeException` (which defines `.exit_code = 1` by default) and expose their corresponding integer exit code via the class attribute `ExceptionClass.exit_code`.

| Exit Code | Constant Name | Exception Class | Description / Trigger Condition |
| :---: | :--- | :--- | :--- |
| **`0`** | `SUCCESS_EXIT_CODE` | *(None)* | PGE execution completed successfully. |
| **`1`** | `UNCLASSIFIED_FAILURE_EXIT_CODE` | `ECOSTRESSExitCodeException` | Base exception class and fallback for unclassified failures. |
| **`2`** | `RUNCONFIG_FILENAME_NOT_SUPPLIED` | `RunConfigFilenameNotSupplied` | Run-config filename argument was not supplied in the PGE call. |
| **`3`** | `UNABLE_TO_OPEN_RUNCONFIG_FILE` | `UnableToOpenRunConfig` | Run-config file does not exist or cannot be opened. |
| **`4`** | `UNABLE_TO_PARSE_RUNCONFIG_FILE` | `UnableToParseRunConfig` | Run-config XML file could not be parsed. |
| **`5`** | `CORRUPTED_RUNCONFIG_STRUCTURE` | `CorruptedRunConfigStructure` | Structure of the run-config data is corrupted or invalid. |
| **`6`** | `MISSING_RUNCONFIG_VALUE` | `MissingRunConfigValue` | A required group or parameter is missing from the run-config file. |
| **`7`** | `FILESYSTEM_INACCESSIBLE` | `FilesystemInaccessible` | Unable to access a directory listed in `StaticAuxiliaryFileGroup` / `StaticAncillaryFileGroup`. |
| **`8`** | `INPUT_FILES_INACCESSIBLE` | `InputFilesInaccessible` | Unable to access input product files listed in `InputFileGroup`. |
| **`9`** | `UNCALIBRATED_GEOLOCATION` | `UncalibratedGeolocation` | Scene rejected because L1B GEO metadata reports `OrbitCorrectionPerformed` is `false`. |
| **`10`** | `INVALID_COORDINATES` | `InvalidCoordinates` | Scene rejected because L1B GEO coordinates fall outside `[-90, 90]` lat, `[-180, 180]` lon, or span $> 10^\circ$. |
| **`11`** | `LAND_FILTER` | `LandFilter` | Scene or tile rejected because metadata/grid reports no land pixels covered. |
| **`12`** | `DAYTIME_FILTER` | `DaytimeFilter` | Scene rejected because `StandardMetadata/DayNightFlag` is not `Day` (or solar zenith angle $\ge 90^\circ$). |
| **`13`** | `CONUS_FILTER` | `CONUSFilter` | Granule or tile does not cover the Continental United States (CONUS). |
| **`14`** | `AUXILIARY_SERVER_UNREACHABLE` | `AuxiliaryServerUnreachable` | Connection failed to a remote server hosting auxiliary data (e.g., CMR, LP DAAC, GEOS-5 FP). |
| **`15`** | `AUXILIARY_LATENCY` | `AuxiliaryLatency` | Required auxiliary granule (e.g., HLS, VIIRS) is not yet available; signals scheduler to retry later. |
| **`16`** | `DOWNLOAD_FAILED` | `DownloadFailed` | File transfer for an auxiliary dataset from a remote server to the local filesystem failed. |
| **`17`** | `BLANK_OUTPUT` | `BlankOutput` | Output rasters contained only no-data (`NaN`) values and were not written to a product file. |
| **`18`** | `PRODUCT_WRITE_FAILED` | `ProductWriteFailed` | PGE failed while writing the output product granule or archive to disk. |

## Development & Testing

Run the test suite with `pytest`:

```bash
pytest
```

## License

Licensed under the [Apache License, Version 2.0](LICENSE).