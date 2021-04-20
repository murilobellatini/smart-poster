"""
All relevant paths stored in constant variables
"""

from sys import platform
from pathlib import Path
from pathlib import PurePosixPath


# local paths
root_path = Path(__file__).parents[1]


LOCAL_GLOBAL_DATA = root_path / 'data/global'
LOCAL_EXTERNAL_DATA_PATH = root_path / 'data/external'
LOCAL_RAW_DATA_PATH = root_path / 'data/raw'
LOCAL_INTERIM_DATA_PATH = root_path / 'data/interim'
LOCAL_PROCESSED_DATA_PATH = root_path / 'data/processed'
LOCAL_TRANSCR_BATCH_PATH = root_path / 'data/batches'
LOCAL_MODELS_PATH = root_path / 'models'
LOCAL_CREDENTIALS_PATH = root_path / 'credentials'

# Google Cloud Storage paths (@todo: implement)
# GCS_BUCKET = PurePosixPath('auto-post-generator')
# GCS_BASE_PATH = PurePosixPath('root')
# GCS_EXTERNAL_DATA_PATH = GCS_BASE_PATH / 'data/external'
# GCS_RAW_DATA_PATH = GCS_BASE_PATH / 'data/raw'
# GCS_INTERIM_DATA_PATH = GCS_BASE_PATH / 'data/interim'
# GCS_PROCESSED_DATA_PATH = GCS_BASE_PATH / 'data/processed'
# GCS_TRANSCR_BATCH_PATH = GCS_BASE_PATH / 'data/batches'
# GCS_MODELS_PATH = GCS_BASE_PATH / 'models'
