import logging
import os
import pathlib
import sys

# 从平台特定的工具中导入平台判断变量，用于区分当前操作系统
from tufup.utils.platform_specific import ON_MAC, ON_WINDOWS

# 创建日志记录器，方便后续记录程序的运行信息
logger = logging.getLogger(__name__)

# 应用程序信息
APP_NAME = 'my_app'  # 应用名称，注意：应用名称不能包含空格
APP_VERSION = '1.0'  # 应用版本号

# 在Windows 10上，常见的应用程序数据存储路径示例：
# - 每个用户的路径：%LOCALAPPDATA%\MyApp
# - 每台机器的路径：%PROGRAMDATA%\MyApp
# 常见的应用程序安装路径：
# - 每个用户的路径：%LOCALAPPDATA%\Programs\MyApp
# - 每台机器的路径：%PROGRAMFILES%\MyApp
# 详情参考微软文档：
# https://docs.microsoft.com/en-us/windows/win32/msi/installation-context

# 获取当前模块目录，当被打包为可执行文件时，此路径等于 sys._MEIPASS
# PyInstaller 文档参考：
# https://pyinstaller.org/en/stable/runtime-information.html#using-file
MODULE_DIR = pathlib.Path(__file__).resolve().parent

# 判断当前是否运行在 PyInstaller 打包的环境中
# PyInstaller 文档参考：
# https://pyinstaller.org/en/stable/runtime-information.html
FROZEN = getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS')

# 开发环境下的临时目录，用于存储开发时的临时数据
DEV_DIR = MODULE_DIR.parent.parent / f'temp_{APP_NAME}'

# 定义应用程序的数据存储和安装目录
if ON_WINDOWS:
    # Windows 系统的每用户路径
    PER_USER_DATA_DIR = pathlib.Path(os.getenv('LOCALAPPDATA'))  # 每用户的数据目录
    PER_USER_PROGRAMS_DIR = PER_USER_DATA_DIR / 'Programs'  # 每用户的程序目录
    # Windows 系统的每台机器路径（仅供参考，未使用）：
    # PER_MACHINE_PROGRAMS_DIR = pathlib.Path(os.getenv('ProgramFiles'))
    # PER_MACHINE_DATA_DIR = pathlib.Path(os.getenv('PROGRAMDATA'))
elif ON_MAC:
    # macOS 系统的每用户路径
    PER_USER_DATA_DIR = pathlib.Path.home() / 'Library'  # 每用户的数据目录
    PER_USER_PROGRAMS_DIR = pathlib.Path.home() / 'Applications'  # 每用户的程序目录
    # macOS 系统的每台机器路径（仅供参考，未使用）：
    # PER_MACHINE_PROGRAMS_DIR = pathlib.Path('/Applications')
    # PER_MACHINE_DATA_DIR = pathlib.Path('/Library')
else:
    # 非Windows或macOS系统的情况下抛出异常
    raise NotImplementedError('Unsupported platform')

# 根据是否为打包环境确定程序目录和数据目录
PROGRAMS_DIR = PER_USER_PROGRAMS_DIR if FROZEN else DEV_DIR  # 程序安装目录
DATA_DIR = PER_USER_DATA_DIR if FROZEN else DEV_DIR  # 数据存储目录

# 定义安装目录、更新缓存目录、元数据目录和目标目录
INSTALL_DIR = PROGRAMS_DIR / APP_NAME  # 应用程序安装目录
UPDATE_CACHE_DIR = DATA_DIR / APP_NAME / 'update_cache'  # 更新缓存目录
METADATA_DIR = UPDATE_CACHE_DIR / 'metadata'  # 元数据目录
TARGET_DIR = UPDATE_CACHE_DIR / 'targets'  # 目标目录

# 定义更新服务器的URL
METADATA_BASE_URL = 'http://localhost:8000/metadata/'  # 元数据服务器URL
TARGET_BASE_URL = 'http://localhost:8000/targets/'  # 目标服务器URL

# 定义可信根元数据文件的位置
TRUSTED_ROOT_SRC = MODULE_DIR.parent / 'root.json'  # 默认位置（打包环境）
if not FROZEN:
    # 如果是开发环境，从本地仓库直接获取根元数据
    sys.path.insert(0, str(MODULE_DIR.parent.parent))  # 添加仓库路径到系统路径
    from repo_settings import REPO_DIR  # 导入仓库设置

    TRUSTED_ROOT_SRC = REPO_DIR / 'metadata' / 'root.json'  # 从仓库获取根元数据
TRUSTED_ROOT_DST = METADATA_DIR / 'root.json'  # 根元数据文件的目标路径
