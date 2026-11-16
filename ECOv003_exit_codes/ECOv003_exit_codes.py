"""
ECOSTRESS Collection 3 Exit Codes
"""
__author__ = "Gregory Halverson"

# --- General Execution Status ---

# Returned when a PGE finishes writing all expected products, OR exits early
# because output granules already exist on disk and `overwrite=False`
# (checked in both `ECOv003-L2T-STARS` and `ECOv003-L3T-L4T-JET`).
SUCCESS_EXIT_CODE = 0

# Default base exit code and catch-all fallback in `L2T_STARS()` when an
# unexpected/unhandled Python exception occurs.
UNCLASSIFIED_FAILURE_EXIT_CODE = 1


# --- CLI & XML RunConfig Errors (2-6) ---

# Returned by CLI `main()` entry points (`ECOv003_DL`, `ECOv003-L3T-L4T-JET`)
# when no run-config path is provided or the supplied path does not exist.
RUNCONFIG_FILENAME_NOT_SUPPLIED = 2

# Raised by `runconfig.read_runconfig()` in both PGEs when the XML run-config
# path cannot be found on disk before parsing begins.
UNABLE_TO_OPEN_RUNCONFIG_FILE = 3

# Raised by `read_runconfig()`, `L2TSTARSConfig`, `ECOv003DLConfig`, and
# `L3TL4TJETConfig` when `untangle` fails to parse the XML or a field fails
# type conversion (e.g., non-integer OrbitNumber or unparseable datetime).
UNABLE_TO_PARSE_RUNCONFIG_FILE = 4

# Reserved for XML run-configs whose group/scalar/vector hierarchy does not
# match the expected OODT CAS input schema.
CORRUPTED_RUNCONFIG_STRUCTURE = 5

# Raised during config initialization (`L2TSTARSConfig`, `ECOv003DLConfig`,
# `L3TL4TJETConfig`) when a required XML group or scalar tag is absent
# (e.g., `StaticAncillaryFileGroup`, `InputFileGroup`, `L2T_LSTE`, `TileId`).
MISSING_RUNCONFIG_VALUE = 6


# --- Local Storage & Input Granule Errors (7-8) ---

# Raised when a required local working, static, or ancillary directory listed
# in `StaticAncillaryFileGroup` cannot be accessed on the filesystem.
FILESYSTEM_INACCESSIBLE = 7

# Raised after RunConfig parsing when an input granule path listed in
# `InputFileGroup` (`L2T_LSTE` in both PGEs; `L2T_STARS` in `L3T_L4T_JET`)
# is missing on disk.
INPUT_FILES_INACCESSIBLE = 8


# --- Granule Quality & Scientific Domain Filters (9-13) ---
# Codes 9-13 tell the SDS orchestrator that a scene/tile was intentionally
# skipped for scientific or geometric reasons (terminal skip, do not retry).

# Raised by upstream L1/L2 PGEs when L1B GEO `OrbitCorrectionPerformed` is false.
UNCALIBRATED_GEOLOCATION = 9

# Raised by upstream L1/L2 PGEs when L1B GEO arrays contain out-of-range
# lat/lon values or span more than 10 degrees.
INVALID_COORDINATES = 10

# Raised by `ECOv003-L2T-STARS` and `ECOv003_DL` when `sentinel_tiles.land()`
# reports no land pixels in the Sentinel tile, or when CMR returns
# `HLSTileNotAvailable` / `HLSNotAvailable` (e.g., open-ocean tiles).
LAND_FILTER = 11

# Raised by `ECOv003-L3T-L4T-JET` (`read_ECOv003_inputs.py`) when all pixels
# in the tile have Solar Zenith Angle >= 90 deg (nighttime overpass), or when
# `StandardMetadata/DayNightFlag` is not "Day".
DAYTIME_FILTER = 12

# Raised by `L3T_L4T_ALEXI` when a tile falls outside the CONUS boundary;
# neighboring tiles in the same scene that succeed can still be mosaicked.
CONUS_FILTER = 13


# --- Remote Auxiliary Data & Network Errors (14-16) ---
# Codes 14-16 distinguish transient remote outages and data latency (retryable)
# from hard transfer failures.

# Raised by `ECOv003-L2T-STARS` (CMR search for HLS/VIIRS) and `ECOv003-L3T-L4T-JET`
# (`FailedGEOS5FPDownload`, `LPDAACServerUnreachable`, `ConnectionError`) when
# remote NASA data servers cannot be reached.
AUXILIARY_SERVER_UNREACHABLE = 14

# Raised by `ECOv003-L2T-STARS` (`L2T_STARS.py` and `generate_STARS_inputs.py`)
# when HLS granules are marked `"missing"` in CMR or coarse VIIRS observations
# are missing within `VIIRS_GIVEUP_DAYS` (4 days of current UTC date).
# Signals the SDS orchestrator to defer and re-queue the job for a later retry.
AUXILIARY_LATENCY = 15

# Raised by `ECOv003-L2T-STARS` (`L2T_STARS.py`, `retrieve_STARS_sources.py`,
# `generate_STARS_inputs.py`) when an auxiliary file transfer fails (`HLSDownloadFailed`,
# `VCD43NRT` `DownloadFailed`, `HLSBandNotAcquired`) or zero coarse inputs are
# available across the lookback window.
DOWNLOAD_FAILED = 16


# --- Product Generation & Output Errors (17-18) ---

# Raised by `ECOv003-L2T-STARS` (`process_STARS_product.py`) and `ECOv003-L3T-L4T-JET`
# when output rasters contain only NaN/no-data values or fail to materialize
# after model/Julia execution.
BLANK_OUTPUT = 17

# Raised when a PGE fails while writing or zipping its final COG product bundle
# or browse image to the output directory.
PRODUCT_WRITE_FAILED = 18


class ECOSTRESSExitCodeException(Exception):
    """
    This is the base class for all ECOSTRESS exceptions with an exit code.
    """
    # Caught at the top level of `L2T_STARS()`, `ECOv003_DL()`, and `L3T_L4T_JET()`
    # to translate domain exceptions directly into process exit codes.
    exit_code = UNCLASSIFIED_FAILURE_EXIT_CODE


class RunConfigFilenameNotSupplied(ECOSTRESSExitCodeException):
    """
    Run config filename argument not supplied in PGE call
    """
    exit_code = RUNCONFIG_FILENAME_NOT_SUPPLIED


class UnableToOpenRunConfig(ECOSTRESSExitCodeException):
    """
    Unable to open run config file
    """
    # Raised in `runconfig.py` across both PGEs if the XML file does not exist.
    exit_code = UNABLE_TO_OPEN_RUNCONFIG_FILE


class UnableToParseRunConfig(ECOSTRESSExitCodeException):
    """
    Unable to parse run config file
    """
    # Raised in `runconfig.py`, `L2TSTARSConfig.py`, `ECOv003_DL.py`, and
    # `L3TL4TJETConfig.py` if XML parsing or field extraction fails.
    exit_code = UNABLE_TO_PARSE_RUNCONFIG_FILE


class CorruptedRunConfigStructure(ECOSTRESSExitCodeException):
    """
    Structure of run config data is corrupted
    """
    exit_code = CORRUPTED_RUNCONFIG_STRUCTURE


class MissingRunConfigValue(ECOSTRESSExitCodeException):
    """
    Missing value in run config file
    """
    # Raised in `L2TSTARSConfig`, `ECOv003DLConfig`, and `L3TL4TJETConfig` when
    # expected XML groups or scalar keys are missing.
    exit_code = MISSING_RUNCONFIG_VALUE


class FilesystemInaccessible(ECOSTRESSExitCodeException):
    """
    Unable to access directory listed in StaticAuxiliaryFileGroup
    """
    exit_code = FILESYSTEM_INACCESSIBLE


class InputFilesInaccessible(ECOSTRESSExitCodeException):
    """
    Unable to access input product files listed in InputFileGroup
    """
    # Raised in `L2T_STARS.py` (missing `L2T_LSTE`) and `read_ECOv003_configuration.py` /
    # `read_ECOv003_inputs.py` (missing `L2T_LSTE` or `L2T_STARS`).
    exit_code = INPUT_FILES_INACCESSIBLE


class UncalibratedGeolocation(ECOSTRESSExitCodeException):
    """
    ECOSTRESS scene rejected because L1B GEO file set OrbitCorrectionPerformed to false
    """
    exit_code = UNCALIBRATED_GEOLOCATION


class InvalidCoordinates(ECOSTRESSExitCodeException):
    """
    ECOSTRESS scene rejected because L1B GEO geolocation arrays contain coordinates outside the valid range of -90 to 90 latitude, -180 to 180 longitude, or the range of either exceeds 10 degrees
    """
    exit_code = INVALID_COORDINATES


class LandFilter(ECOSTRESSExitCodeException):
    """
    ECOSTRESS scene rejected because L1B metadata reports no land pixels covered
    """
    # Raised in `L2T_STARS.py` when `sentinel_tiles.land(tile)` is False or CMR
    # reports no HLS coverage for an ocean tile.
    exit_code = LAND_FILTER


class DaytimeFilter(ECOSTRESSExitCodeException):
    """
    ECOSTRESS scene rejected because StandardMetadata/DayNightFlag attribute in the L2T_LSTE input product contains a value other than Day.
    """
    # Raised in `ECOv003-L3T-L4T-JET` (`read_ECOv003_inputs.py`) when all pixels
    # in the tile have SZA >= 90 degrees (nighttime).
    exit_code = DAYTIME_FILTER


class CONUSFilter(ECOSTRESSExitCodeException):
    """
    ECOSTRESS scene rejected the granule does not cover CONUS. In the case that an ECOSTRESS Orbit/Scene granule is on the edge of the CONUS boundary, some of the the L3T_L4T_ALEXI tiles may succeed while others return this exit code. The tiles that do succeed can still be mosaicked by L3G_L4G_ALEXI.
    """
    exit_code = CONUS_FILTER


class AuxiliaryServerUnreachable(ECOSTRESSExitCodeException):
    """
    This exit code reports that a connection could not be made to one of the remote servers hosting auxiliary data. Sometimes these servers are down for maintenance for a few hours at a time.
    """
    # Raised in `L2T_STARS.py` when CMR is unreachable for HLS or VIIRS; mapped
    # in `L3T_L4T_JET` when GEOS-5 FP or LP DAAC servers cannot be reached.
    exit_code = AUXILIARY_SERVER_UNREACHABLE


class AuxiliaryLatency(ECOSTRESSExitCodeException):
    """
    This exit code reports that a required granule from an auxiliary data source is not yet available.
    """
    # Raised in `L2T_STARS.py` (missing HLS Sentinel/Landsat granules) and
    # `generate_STARS_inputs.py` (missing VIIRS granules within `VIIRS_GIVEUP_DAYS`).
    exit_code = AUXILIARY_LATENCY


class DownloadFailed(ECOSTRESSExitCodeException):
    """
    This exit code reports that the file transfer for an auxiliary file from the remote server to the local filesystem failed. This can happen intermittently, but if it happens persistently, then the security or API of the remote server may have made a breaking change.
    """
    # Raised/caught in `L2T_STARS.py`, `retrieve_STARS_sources.py`, and
    # `generate_STARS_inputs.py` when HLS or VCD43NRT downloads fail.
    exit_code = DOWNLOAD_FAILED


class BlankOutput(ECOSTRESSExitCodeException):
    """
    This exit code reports that the output images contained only no-data values and were not written to a product file.
    """
    # Raised in `process_STARS_product.py` (missing/empty NDVI or albedo posteriors)
    # and in `ECOv003-L3T-L4T-JET` when model output layers are blank.
    exit_code = BLANK_OUTPUT


class ProductWriteFailed(ECOSTRESSExitCodeException):
    """
    This exit code reports that the PGE was unable to write its product file.
    """
    exit_code = PRODUCT_WRITE_FAILED