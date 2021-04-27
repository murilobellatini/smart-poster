"""
Scripts for transfering data in and out are handled here.
"""
from os import remove
from os.path import exists
from src import bucket, client
from pathlib import Path, PurePosixPath
from src.credentials import gcloud_credentials_dict
from src.paths import GCS_BUCKET, LOCAL_RAW_DATA_PATH, GCS_RAW_DATA_PATH, GCS_BASE_PATH, root_path
from src import custom_logging as logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def upload_to_gcs(
        filename: str,
        local_dir_path: Path = LOCAL_RAW_DATA_PATH,
        remote_dir_path: PurePosixPath = GCS_RAW_DATA_PATH,
        gcs_bucket: PurePosixPath = GCS_BUCKET):
    """
    Uploads file to Google Cloud Storage
    """
    f = FileTransfer(filename, local_dir_path, remote_dir_path, gcs_bucket)
    f.upload_to_gcs()


def download_from_gcs(
        filename: str,
        local_dir_path: Path = LOCAL_RAW_DATA_PATH,
        remote_dir_path: PurePosixPath = GCS_RAW_DATA_PATH,
        gcs_bucket: PurePosixPath = GCS_BUCKET):
    """
    Downloads file locally from Google Cloud Storage
    """
    f = FileTransfer(filename, local_dir_path, remote_dir_path, gcs_bucket)
    f.download_from_gcs()


class FileTransfer():
    """
    FileTransfer is a class for interacting with Google Cloud Storage by
    transfering files remote and locally.
    """

    def __init__(self,
                 filename: str,
                 local_dir_path: Path = None,
                 remote_dir_path: PurePosixPath = None,
                 gcs_bucket: PurePosixPath = GCS_BUCKET):
        """
        FileTransfer class constructor creates path variables for
        transfering files in and out local folder structure
        - `filename`: filename with extension
        - `local_dir_path`: file local directory path, if empty gets mirror from remote_dir_path
        - `remote_dir_path`: remote directory path at bucket,  if empty gets mirror from local_dir_path
        - `gcs_bucket`: bucket name
        """
        self.filename = filename
        self.bucket = gcs_bucket

        if local_dir_path is None and remote_dir_path is None:
            logger.warning(
                f'No dir path arguments given for `{filename}`, file transfering will not work...')
        elif local_dir_path is None and remote_dir_path is not None:
            self.remote_dir_path = remote_dir_path
            self.local_dir_path = self._compose_local_path_(
                self.remote_dir_path)
        elif local_dir_path is not None and remote_dir_path is None:
            self.local_dir_path = local_dir_path
            self.remote_dir_path = self._compose_remote_path_(
                self.local_dir_path)
        else:  # both args have values
            self.local_dir_path = local_dir_path
            self.remote_dir_path = remote_dir_path

        self.full_local_path = self.local_dir_path / \
            self.filename if self.local_dir_path is not None else None
        self.full_remote_path = self.remote_dir_path / \
            self.filename if self.remote_dir_path is not None else None

        if self.bucket != GCS_BUCKET:
            bucket = client.get_bucket(str(self.bucket))

        logger.info(f"""File object created with:
- filename        : {self.filename}
- local_dir_path  : {self.local_dir_path}
- remote_dir_path : {self.remote_dir_path}
- bucket          : {self.bucket}""")

    def upload_to_gcs(self):
        """
        Uploads File object to bucket
        """
        if not self._are_io_parameters_ok():
            return

        blob = bucket.blob(self.full_remote_path)
        remote_files_paths = [blob.name for blob in bucket.list_blobs()]
        if str(self.full_remote_path) in remote_files_paths:
            logger.info(
                f'File already exists at path below. Upload aborted...\n> gs://{self.bucket / self.full_remote_path}')
            return
        else:
            blob.upload_from_filename(str(self.full_local_path))
            logger.info(
                f'File successfully uploaded to path below\n> gs://{self.bucket / self.full_remote_path}')

    def download_from_gcs(self):
        """
        Downloads File object locally
        """
        if not self._are_io_parameters_ok():
            return

        if exists(str(self.full_local_path)):
            should_continue = 'n'
            if logger.level < 30:  # logging.WARNING == 30
                should_continue = input(
                    f'File already exists at path below. This operation will overwrite the file.\n> {self.full_local_path}\nDo you wish to proceed? [y/n]')
            if (should_continue != 'y'):
                logger.warning(
                    f'Operation aborted. File already exists at path below\n> {self.full_local_path}')
                return

        remote_files_paths = [blob.name for blob in bucket.list_blobs()]
        if str(self.full_remote_path) not in remote_files_paths:
            logger.info(
                f'File does not exist at path below. Download aborted...\n> gs://{self.bucket / self.full_remote_path}')
            return
        else:
            gcs_file_path = str(self.full_remote_path)
            blob = bucket.blob(gcs_file_path)

            try:
                local_file_path = str(self.full_local_path)
                blob.download_to_filename(local_file_path)
            except Exception as e:
                remove(local_file_path)  # debug
                raise e

            logger.info(
                f'File successfully downloaded to path below\n> {self.full_local_path}')

    def _compose_remote_path_(self, local_path: Path, gcs_subpath: PurePosixPath = GCS_BASE_PATH):
        """
        Composes remote mirror path based on local path
        """
        relative_path = Path()

        for p in local_path.parts:
            if relative_path != root_path:
                relative_path = relative_path / p
            else:
                gcs_subpath = gcs_subpath / p

        return gcs_subpath

    def _compose_local_path_(self, remote_path: PurePosixPath, target_root_path: Path = root_path):
        """
        Composes local mirror path based on remote path
        """
        return target_root_path.parent / remote_path

    def _are_io_parameters_ok(self):
        """
        Returns a boolean if IO arguments are present, such as `self.local_dir_path` and `self.remote_dir_path`.
        """
        if self.local_dir_path is None or self.remote_dir_path is None:
            logger.warning(
                f'No dir path arguments given for `{self.filename}`, aborting process... Set both of these args to continue.')
            return False

        return True


class FileChecker(FileTransfer):
    """
    FileChecker is a class inherited from FileTransfer with a simpler constructor
    only for checking data integrity, and not transfering data IO bucket.
    """

    def __init__(self,
                 full_local_path: Path,
                 gcs_bucket: PurePosixPath = GCS_BUCKET):
        """
        FileChecker class constructor triggers remote path
        composition from local abs path of file. 
        - `full_local_path` : abs path of file to check
        - `gcs_bucket`      : target bucket name
        """
        self.full_local_path = full_local_path
        self.local_dir_path = self.full_local_path.parent
        self.bucket = gcs_bucket
        self.remote_dir_path = self._compose_remote_path_(self.local_dir_path)
