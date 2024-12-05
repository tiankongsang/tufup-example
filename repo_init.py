import logging

from tufup.repo import Repository  # 从 tufup 仓库模块导入 Repository 类，用于创建和管理 TUF 仓库

from myapp.settings import APP_NAME  # 从 myapp 设置模块中导入应用程序名称
from repo_settings import (  # 导入仓库设置中的各个参数
    ENCRYPTED_KEYS,  # 指定哪些密钥是加密的
    EXPIRATION_DAYS,  # 各角色签名的过期天数
    KEY_MAP,  # 每个 TUF 角色对应的密钥映射
    KEYS_DIR,  # 密钥所在的目录
    REPO_DIR,  # 仓库所在的目录
    THRESHOLDS,  # 各角色的签名阈值
)

# 创建日志记录器
logger = logging.getLogger(__name__)

"""

免责声明

为了方便，此示例为所有 TUF 角色使用了同一对密钥，私钥未加密且存储在本地。
这种方式 *不安全*，在生产环境中 *不应* 使用。

"""

if __name__ == '__main__':
    # 设置日志记录的基本配置，日志级别设为 INFO
    logging.basicConfig(level=logging.INFO)

    # 创建仓库实例
    repo = Repository(
        app_name=APP_NAME,  # 应用程序的名称
        app_version_attr='myapp.__version__',  # 指定应用程序版本的属性
        repo_dir=REPO_DIR,  # 仓库所在的目录
        keys_dir=KEYS_DIR,  # 密钥所在的目录
        key_map=KEY_MAP,  # 各角色使用的密钥映射
        expiration_days=EXPIRATION_DAYS,  # 各角色签名的过期天数
        encrypted_keys=ENCRYPTED_KEYS,  # 加密的密钥列表
        thresholds=THRESHOLDS,  # 各角色的签名阈值
    )

    # 保存仓库的配置（保存为 JSON 文件）
    repo.save_config()

    # 初始化仓库（如果必要，创建密钥和根元数据）
    repo.initialize()
