import logging
import sys

from tufup.repo import Repository  # 从 tufup 仓库模块导入 Repository 类，用于创建和管理 TUF 仓库

from repo_settings import DIST_DIR, KEYS_DIR  # 导入包输出目录和密钥存储目录的配置

# 获取当前模块的日志记录器
logger = logging.getLogger(__name__)

if __name__ == '__main__':
    # 从最新的 pyinstaller 生成的捆绑包创建一个压缩包（假设已经使用 PyInstaller 创建了捆绑包，并且只有一个）
    try:
        # 查找 DIST_DIR 目录中所有子目录（即 PyInstaller 生成的捆绑包目录）
        bundle_dirs = [path for path in DIST_DIR.iterdir() if path.is_dir()]
    except FileNotFoundError:
        # 如果目录不存在，提示用户并退出程序
        sys.exit(f'目录未找到: {DIST_DIR}\n您是否运行了 pyinstaller ?')

    # 确保只有一个捆绑包目录
    if len(bundle_dirs) != 1:
        sys.exit(f'期望找到一个捆绑包，但找到了 {len(bundle_dirs)} 个。')

    # 获取捆绑包目录
    bundle_dir = bundle_dirs[0]
    print(f'添加捆绑包: {bundle_dir}')

    # 从配置文件创建仓库实例（假设仓库已经初始化过）
    repo = Repository.from_config()

    # 将新的应用程序捆绑包添加到仓库（会自动读取 myapp.__version__ 版本信息）
    repo.add_bundle(
        new_bundle_dir=bundle_dir,  # 指定新的捆绑包目录
        # [可选] 自定义元数据可以是任何字典（默认是 None）
        custom_metadata={'changes': ['新增功能 x', '修复了错误 y']},
    )

    # 发布仓库的更改，使用提供的密钥目录进行签名
    repo.publish_changes(private_key_dirs=[KEYS_DIR])

    print('完成。')
