import logging
import os
import pathlib
import sys

from tufup.utils.platform_specific import ON_MAC, ON_WINDOWS

logger = logging.getLogger(__name__)

# App info
APP_NAME = 'my_app'  # BEWARE: app name cannot contain whitespace
APP_VERSION = '1.0'

# 关于 Windows 系统上的应用程序数据位置�?
# �?Windows 10 上，典型的应用数据位置为�?
# - %PROGRAMDATA%\MyApp（针对所有用户的机器级数据）
# - %LOCALAPPDATA%\MyApp（针对当前用户的数据�?
# 典型的应用安装位置为�?
# - %PROGRAMFILES%\MyApp（针对所有用户的机器级安装）
# - %LOCALAPPDATA%\Programs\MyApp（针对当前用户的安装�?
# 参考：https://docs.microsoft.com/en-us/windows/win32/msi/installation-context

# 当前模块所在的目录（当程序�?PyInstaller 打包成单个文件时，此值为 sys._MEIPASS�?
# 参考：https://pyinstaller.org/en/stable/runtime-information.html#using-file
MODULE_DIR = pathlib.Path(__file__).resolve().parent

# 检查是否在 PyInstaller 打包的环境中运行
# 参考：https://pyinstaller.org/en/stable/runtime-information.html
FROZEN = getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS')

# 开发使用的目录
DEV_DIR = MODULE_DIR.parent.parent / f'temp_{APP_NAME}'

# 应用程序的目录设�?
if ON_WINDOWS:
    # Windows 用户级路�?
    PER_USER_DATA_DIR = pathlib.Path(os.getenv('LOCALAPPDATA'))  # 本地应用数据目录（针对当前用户）
    PER_USER_PROGRAMS_DIR = PER_USER_DATA_DIR / 'Programs'  # 当前用户的程序目�?
    # Windows 机器级路径（仅供说明，未在代码中使用�?
    # PER_MACHINE_PROGRAMS_DIR = pathlib.Path(os.getenv('ProgramFiles'))
    # PER_MACHINE_DATA_DIR = pathlib.Path(os.getenv('PROGRAMDATA'))
elif ON_MAC:
    # macOS 用户级路�?
    PER_USER_DATA_DIR = pathlib.Path.home() / 'Library'  # 用户�?Library 目录
    PER_USER_PROGRAMS_DIR = pathlib.Path.home() / 'Applications'  # 用户�?Applications 目录
    # macOS 机器级路径（仅供说明，未在代码中使用�?
    # PER_MACHINE_PROGRAMS_DIR = pathlib.Path('/Applications')
    # PER_MACHINE_DATA_DIR = pathlib.Path('/Library')
else:
    # 如果是其他平台，抛出未实现错�?
    raise NotImplementedError('不支持的平台')

# 应用程序安装和数据的路径设置
# 如果是在打包环境下（FROZEN），使用用户级目录；否则使用开发目�?
PROGRAMS_DIR = PER_USER_PROGRAMS_DIR if FROZEN else DEV_DIR
DATA_DIR = PER_USER_DATA_DIR if FROZEN else DEV_DIR

INSTALL_DIR = PROGRAMS_DIR / APP_NAME  # 安装目录
UPDATE_CACHE_DIR = DATA_DIR / APP_NAME / 'update_cache'  # 更新缓存目录
METADATA_DIR = UPDATE_CACHE_DIR / 'metadata'  # 元数据目�?
TARGET_DIR = UPDATE_CACHE_DIR / 'targets'  # 目标目录（用于保存更新包�?

# 更新服务器的 URL 设置
METADATA_BASE_URL = 'http://localhost:8000/metadata/'  # 元数据的基准 URL
TARGET_BASE_URL = 'http://localhost:8000/targets/'  # 目标文件的基�?URL

# 受信任的根元数据文件位置
TRUSTED_ROOT_SRC = MODULE_DIR.parent / 'root.json'  # 根元数据的源文件路径
if not FROZEN:
    # 如果不是打包环境，从本地仓库直接获取根元数据
    sys.path.insert(0, str(MODULE_DIR.parent.parent))  # 将仓库目录添加到系统路径中，以便于导�?
    from repo_settings import REPO_DIR  # 导入仓库的配置目�?

    TRUSTED_ROOT_SRC = REPO_DIR / 'metadata' / 'root.json'  # 获取根元数据的路�?
TRUSTED_ROOT_DST = METADATA_DIR / 'root.json'  # 根元数据文件的目标路�?
