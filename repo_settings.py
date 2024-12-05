import logging
import pathlib

from tufup.repo import DEFAULT_KEY_MAP, DEFAULT_KEYS_DIR_NAME, DEFAULT_REPO_DIR_NAME

logger = logging.getLogger(__name__)

"""

免责声明

为了方便，此示例为所有 TUF 角色使用了同一对密钥，私钥未加密并存储在本地。
这种方式 *不安全*，在生产环境中 *不应* 使用。

"""

# 获取当前模块所在的目录路径
MODULE_DIR = pathlib.Path(__file__).resolve().parent

# 开发环境下的路径设置
DEV_DIR = MODULE_DIR / 'temp_my_app'  # 存放开发中的临时数据
PYINSTALLER_DIST_DIR_NAME = 'dist'  # PyInstaller 的输出目录名
DIST_DIR = DEV_DIR / PYINSTALLER_DIST_DIR_NAME  # 最终 PyInstaller 输出文件的完整路径

# 本地 TUF 仓库和密钥存储路径（在生产中这些密钥通常应该保存在离线环境中）
KEYS_DIR = DEV_DIR / DEFAULT_KEYS_DIR_NAME  # 存储密钥的目录
REPO_DIR = DEV_DIR / DEFAULT_REPO_DIR_NAME  # TUF 仓库目录

# 密钥设置
KEY_NAME = 'my_key'  # 密钥名称
PRIVATE_KEY_PATH = KEYS_DIR / KEY_NAME  # 私钥文件的完整路径
# 将每个角色映射到使用的密钥，这里将所有默认 TUF 角色都映射到同一个密钥
KEY_MAP = {role_name: [KEY_NAME] for role_name in DEFAULT_KEY_MAP.keys()}
ENCRYPTED_KEYS = []  # 该列表表示哪些密钥是加密的，这里为空表示所有密钥未加密
THRESHOLDS = dict(root=1, targets=1, snapshot=1, timestamp=1)  # 每个角色所需的签名数量（阈值）
EXPIRATION_DAYS = dict(root=365, targets=7, snapshot=7, timestamp=1)  # 每个角色的签名有效天数（过期时间）
