# Tufup (TUF-更新器) 示例应用

这个仓库展示了如何使用 [tufup][1] 包来实现应用程序的自动更新。

这是通过一个名为 `myapp` 的虚拟 Windows 应用程序来演示的，该应用程序结合使用了 `tufup` 和 `pyinstaller`。

注意：虽然示例 `myapp` 是使用 `pyinstaller` 打包的，但这并非必需：`tufup` 完全独立于 `pyinstaller`，可以用于*任何*文件包。

注意：虽然示例应用程序是为 Windows（或 macOS）编写的，这仅涉及 `settings.py` 中定义的目录以及用于运行 `pyinstaller` 的脚本。
你可以简单地修改这些来在其他操作系统上使用该示例。

## 问题

如果你有任何问题，请确保先查看[现有讨论][5]和[现有问题][6]。（也请查看 [`tufup` 讨论][10]和 [`tufup` 问题][11]。）

新的*问题*可以在 [Q&A][9] 或 [stackoverflow][8] 上提出，与 `tufup-example` 相关的*错误*可以在[这里][7]报告。

## 设置

创建虚拟环境（或等效环境）并安装依赖：

`pip install -r requirements.txt -r requirements-dev.txt --upgrade`

## 入门

关于基本术语，请参阅 [TUF (The Update Framework)][2] 的文档。

我们从一个已经集成了 `tufup.client` 的虚拟应用程序开始。
详情请参见 `src/myapp/__init__.py`。

这个虚拟应用程序使用 [PyInstaller][3] 打包，但 `tufup` 可以与任何类型的"应用程序包"（即代表应用程序的包含内容的目录）一起使用。

该示例包含一个基本的 PyInstaller `.spec` 文件，确保 `tufup` 根元数据文件（`root.json`）包含在应用程序包中。

虚拟*应用程序*指定了所有 `tufup` 相关文件的存储位置。
这在 `settings.py` 中有说明。

涵盖了以下基本步骤：

1. 初始化仓库
2. 初始发布
   1. 构建应用程序，包括来自仓库的受信任根元数据
   2. 为应用程序创建归档并在仓库中注册
3. 第二次发布
   1. 构建新版本
   2. 为新版本创建归档，创建补丁，并在仓库中注册两者
4. 在本地测试服务器上提供仓库服务
5. 运行"已安装"的应用程序，以便它可以执行自动更新

> 为了快速测试，这些步骤已在 [PowerShell][12] 脚本 [`test_update_cycle.ps1`][13] 中自动化。

在以下部分中可以找到仓库端和客户端的详细步骤说明。

### 仓库端

提供了一些示例脚本用于初始化 tufup 仓库和添加新版本，请参见 `repo_*.py`。

另外，`tufup` 为仓库操作提供了命令行界面（CLI）。
在命令行中输入 `tufup -h` 获取更多信息。

以下是如何设置示例 tufup 仓库，从一个干净的仓库开始，即在仓库根目录（由 `settings.py` 中的 `DEV_DIR` 定义）中不存在 `temp_my_app` 目录：

注意：如果使用 CLI，请参见 `repo_settings.py` 获取合理的值。

1. 运行 `repo_init.py`（CLI：`tufup init`）
2. 运行 `create_pyinstaller_bundle_win.bat` 或 `create_pyinstaller_bundle_mac.sh`
   （注意我们的 `main.spec` 确保最新的 `root.json` 元数据文件包含在包中）
3. 运行 `repo_add_bundle.py`（CLI：`tufup targets add 1.0 temp_my_app/dist/main temp_my_app/keystore`）
4. 修改应用程序，和/或在 `myapp/settings.py` 中增加 `APP_VERSION`
5. 再次运行 `create_pyinstaller_bundle` 脚本
6. 再次运行 `repo_add_bundle.py`（CLI：`tufup targets add 2.0 temp_my_app/dist temp_my_app/keystore`）

注意：添加包时，`tufup` 默认创建补丁，这可能需要相当长的时间。
如果你想跳过补丁创建，可以在 `Repository.add_bundle()` 调用中设置 `skip_patch=True`，或在 CLI 命令中添加 `-s` 选项：`tufup targets add -s 2.0 ...`。

现在我们应该有一个具有以下结构的 `temp_my_app` 目录：

```text
temp_my_app
├ build
├ dist
├ keystore
└ repository
  ├ metadata
  └ targets
```

在 `targets` 目录中，我们找到两个应用程序归档（1.0 和 2.0）和相应的补丁文件。

我们可以在 localhost 上提供仓库服务，如下（相对于项目根目录）：

```shell
python -m http.server -d temp_my_app/repository
```

这就是仓库端的全部内容。

### 客户端

在同一系统上（为了方便）：

1. 为了模拟在客户端设备上的初始安装，我们将 `repository/targets` 目录中的归档版本 1.0 手动解压到 `myapp/settings.py` 中指定的 `INSTALL_DIR` 中。

   #### 在 Windows 上

   在默认示例中，`INSTALL_DIR` 将是 `C:\users\<username>\AppData\Local\Programs\my_app` 目录。
   你可以在 PowerShell 中使用 `tar -xf my_app-1.0.tar.gz` 来解压包。

   #### 在 macOS 上

   要将包安装到 macOS 的默认位置，你可以使用
   `mkdir -p ~/Applications/my_app && tar -xf temp_my_app/repository/targets/my_app-1.0.tar.gz -C ~/Applications/my_app`。

2. [可选] 要尝试补丁更新，将归档版本 1.0 复制到 `TARGET_DIR`（这通常由安装程序完成）。
3. 假设仓库文件如上所述在 localhost 上提供服务，我们现在可以直接从 `INSTALL_DIR` 运行新解压的可执行文件 `main.exe` 或 `main`（取决于平台），它将执行更新。
4. 元数据和目标存储在 `UPDATE_CACHE_DIR` 中。

注意：上述步骤涉及 `FROZEN` 状态下的 `INSTALL_DIR`，在 Windows 上通常是 `C:\users\<username>\AppData\Local\Programs\my_app`。
在开发时，当直接从源代码运行 `myapp` 示例时，即 `FROZEN=False`，`INSTALL_DIR` 与生产环境中使用的实际安装目录不同。详情请参见 [settings.py][4]。

### 故障排除

在使用这个示例应用时，很容易陷入不一致的状态，例如由于过时的元数据文件。
这可能导致 tuf 角色验证错误等问题。
如果出现这种情况，通常最简单的方法是为仓库和客户端重新开始：

1. 对于客户端，删除 `UPDATE_CACHE_DIR` 和 `INSTALL_DIR`
2. 对于仓库端，删除 `DEV_DIR`（即上述的 `temp_my_app` 目录）
3. 删除 `.tufup_repo_config`
4. 按照上述步骤设置仓库端和客户端

或者，你可以运行 `test_update_cycle.ps1` 脚本，它也会从默认目录中删除过时的示例文件。

[1]: https://github.com/dennisvang/tufup
[2]: https://theupdateframework.io/
[3]: https://pyinstaller.org/en/stable/
[4]: https://github.com/dennisvang/tufup-example/blob/2af43175d39417f9d3d855d7e8fb2cb6ebd3c155/src/myapp/settings.py#L38
[5]: https://github.com/dennisvang/tufup-example/discussions
[6]: https://github.com/dennisvang/tufup-example/issues?q=is%3Aissue
[7]: https://github.com/dennisvang/tufup-example/issues/new
[8]: https://stackoverflow.com/questions/ask
[9]: https://github.com/dennisvang/tufup-example/discussions/new?category=q-a
[10]: https://github.com/dennisvang/tufup/discussions
[11]: https://github.com/dennisvang/tufup/issues
[12]: https://learn.microsoft.com/en-ca/powershell/scripting/install/installing-powershell
[13]: ./test_update_cycle.ps1
