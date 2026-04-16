from enum import IntFlag, auto

class ExitCode(IntFlag):
    SUCCESS = 0
    DOWNLOAD_FAILED = auto()
    SOURCE_TF_FAILED = auto()
    DESTINATION_TF_FAILED = auto()
    CONNECTION_TF_FAILED = auto()
    IMPORT_FAILED = auto()