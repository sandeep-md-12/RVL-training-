class FileNotFoundError(Exception):
    pass

class InvalidFileTypeError(Exception):
    pass

class CSVNotLoadedError(Exception):
    pass

class InvalidColumnError(Exception):
    pass

class FilterError(Exception):
    pass

class S3UploadError(Exception):
    pass

class S3FileNotFoundError(Exception):
    pass

class S3DownloadError(Exception):
    pass
