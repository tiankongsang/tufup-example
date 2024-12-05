import logging
import shutil
import time

from tufup.client import Client  # 导入 TUF 客户端，用于检查和应用更新

from myapp import settings  # 导入应用程序的设置信息

# 创建日志记录器
logger = logging.getLogger(__name__)

# 当前应用版本，定义为 settings 模块中的 APP_VERSION
__version__ = settings.APP_VERSION

# 进度回调函数，用于在下载时显示进度
def progress_hook(bytes_downloaded: int, bytes_expected: int):
    # 计算下载的进度百分比
    progress_percent = bytes_downloaded / bytes_expected * 100
    # 打印当前下载的百分比（以一行动态显示）
    print(f'\r{progress_percent:.1f}%', end='')
    # 为了模拟慢速下载或大文件下载，睡眠 0.2 秒
    time.sleep(0.2)
    # 如果下载完成（进度达到或超过 100%），则换行
    if progress_percent >= 100:
        print('')

# 更新函数，用于检查并应用更新
def update(pre: str, skip_confirmation: bool = False):
    # 创建更新客户端实例
    client = Client(
        app_name=settings.APP_NAME,  # 应用名称
        app_install_dir=settings.INSTALL_DIR,  # 应用安装目录
        current_version=settings.APP_VERSION,  # 当前应用版本
        metadata_dir=settings.METADATA_DIR,  # 元数据目录
        metadata_base_url=settings.METADATA_BASE_URL,  # 元数据服务器 URL
        target_dir=settings.TARGET_DIR,  # 更新目标目录
        target_base_url=settings.TARGET_BASE_URL,  # 目标文件服务器 URL
        refresh_required=False,  # 是否需要强制刷新元数据
    )

    # 执行更新检查
    new_update = client.check_for_updates(pre=pre)
    if new_update:
        # [可选] 使用自定义元数据（如果可用）
        if new_update.custom:
            # 例如，显示更新的更改列表（见 repo_add_bundle.py 中的定义）
            print('本次更新的更改内容：')
            for item in new_update.custom.get('changes', []):
                print(f'\t- {item}')
        # 应用更新
        client.download_and_apply_update(
            skip_confirmation=skip_confirmation,  # 是否跳过确认提示
            progress_hook=progress_hook,  # 下载进度回调函数
            # 警告：`purge_dst_dir=True` 会不可逆地删除安装目录中的所有内容，
            # 除了 `exclude_from_purge` 指定的路径。因此，只有在确保
            # `app_install_dir` 中没有任何无关内容时才使用 `purge_dst_dir=True`
            purge_dst_dir=False,
            exclude_from_purge=None,  # 无需排除路径
            log_file_name='install.log',  # 日志文件名称
        )

# 主函数，处理命令行参数并执行应用的主要功能
def main(cmd_args):
    # 应用程序应使用 argparse，但这里为了简单，仅做了最小化的参数解析
    pre_release_channel = None  # 预发布频道（例如 alpha、beta 或候选版本）
    skip_confirmation = False  # 是否跳过确认
    while cmd_args:
        arg = cmd_args.pop(0)
        if arg in ['a', 'b', 'rc']:
            pre_release_channel = arg  # 指定预发布频道
        else:
            skip_confirmation = arg == 'skip'  # 如果参数为 'skip'，则跳过确认

    # 应用程序需要确保目录存在
    for dir_path in [settings.INSTALL_DIR, settings.METADATA_DIR, settings.TARGET_DIR]:
        dir_path.mkdir(exist_ok=True, parents=True)  # 创建目录，如果不存在则创建，包括父目录

    # 应用程序必须附带受信任的 "root.json" 元数据文件
    # 该文件由 tufup.repo 工具创建，应用程序必须确保该文件可以在指定的元数据目录中找到
    # 该根元数据文件列出了所有受信任的密钥和 TUF 角色
    if not settings.TRUSTED_ROOT_DST.exists():
        # 如果受信任的元数据文件不存在，则从源复制到目标位置
        shutil.copy(src=settings.TRUSTED_ROOT_SRC, dst=settings.TRUSTED_ROOT_DST)
        logger.info('已将受信任的根元数据复制到缓存中。')

    # 下载并应用任何可用的更新
    update(pre=pre_release_channel, skip_confirmation=skip_confirmation)

    # 执行应用程序的主要功能
    print(f'启动 {settings.APP_NAME} {settings.APP_VERSION}...')
    ...
    print('执行应用程序的功能...')
    ...
    print('完成。')