import logging
import sys

from notsotuf.common import Patcher
from notsotuf.repo import Keys, Roles, in_, make_gztar_archive

from init_repo import (
    DEV_DIR,
    ENCRYPTED_KEYS,
    KEY_MAP,
    KEYS_DIR,
    METADATA_DIR,
    PRIVATE_KEY_PATH,
    TARGETS_DIR,
)
from myapp.settings import APP_NAME, CURRENT_VERSION

logger = logging.getLogger(__name__)

PYINSTALLER_DIST_DIR_NAME = 'dist'
DIST_DIR = DEV_DIR / PYINSTALLER_DIST_DIR_NAME

if __name__ == '__main__':
    # create archive from latest pyinstaller bundle (assuming we have already
    # created a pyinstaller bundle, and there is only one)
    try:
        bundle_dirs = [path for path in DIST_DIR.iterdir() if path.is_dir()]
    except FileNotFoundError:
        sys.exit(f'Directory not found: {DIST_DIR}\nDid you run pyinstaller?')
    if len(bundle_dirs) != 1:
        sys.exit(f'Expected one bundle, found {len(bundle_dirs)}.')
    bundle_dir = bundle_dirs[0]
    # Note CURRENT_VERSION is the version of the new archive
    new_archive = make_gztar_archive(
        src_dir=bundle_dir, dst_dir=TARGETS_DIR, app_name=APP_NAME, version=CURRENT_VERSION
    )

    # load metadata
    keys = Keys(dir_path=KEYS_DIR, encrypted=ENCRYPTED_KEYS, key_map=KEY_MAP)
    roles = Roles(dir_path=METADATA_DIR)
    roles.initialize(keys=keys)

    # check latest archive before registering the new one
    latest_archive = roles.get_latest_archive()
    if not latest_archive or latest_archive.version < new_archive.version:
        # register new archive
        roles.add_or_update_target(local_path=new_archive.path)

        # create patch, if possible, and register that too
        if latest_archive:
            logger.info(f'Creating patch for {new_archive}')
            patch_path = Patcher.create_patch(
                src_path=TARGETS_DIR / latest_archive.path,
                dst_path=TARGETS_DIR / new_archive.path,
            )
            logger.info(f'Patch created.')
            roles.add_or_update_target(local_path=patch_path)

        # publish updated targets (can safely be called if nothing has changed)
        role_names = ['targets', 'snapshot', 'timestamp']
        roles.publish_targets(
            private_key_paths={name: [PRIVATE_KEY_PATH] for name in role_names},
            expires={name: in_(365) for name in role_names},
        )
