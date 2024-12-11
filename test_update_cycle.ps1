# DISCLAIMER:
# 本脚本会自动在您的系统中创建与示例 "my_app" 相关的文件，并在之后删除它们。删除前会请求确认。
# 使用风险由用户承担。
#
# 本脚本执行 README 中的步骤，涵盖仓库端和客户端的操作。
# 其功能与 GitHub workflow 中的 test-update-cycle.yml 基本相同，只不过这是在本地开发环境中手动测试更方便。
#
# - 初始化一个新的示例仓库到 .\temp_my_app 目录（包含虚拟密钥库）
# - 使用 pyinstaller 创建 my_app v1.0 版本的捆绑包
# - 将 my_app v1.0 添加到 tufup 仓库
# - 在 <localappdata>\Programs\my_app 安装 my_app v1.0，数据存储在 <localappdata>\my_app
# - 模拟开发 my_app v2.0
# - 使用 pyinstaller 创建 my_app v2.0 版本的捆绑包
# - 将 my_app v2.0 添加到 tufup 仓库
# - 启动更新服务器，并将 my_app 从 v1 更新到 v2
#
# 如果脚本无法执行，运行以下命令：
#   `Set-ExecutionPolicy AllSigned`
# 参考: https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.core/about/about_scripts
#
# 需要注意的是，我们可以直接在 GitHub workflow 中运行此脚本，但将工作流拆分成独立步骤便于调试失败。


# 如果命令行有错误，立即退出
$ErrorActionPreference = "stop"

# 可执行文件出错时退出（用于可执行文件调用之后）
function Assert-ExeSuccess {
    if (!$?) {
        # $? 包含上次命令的执行状态（成功则为 true）
        Write-Error "failed"
    }
}


# 变量
$app_name = "my_app"
$enable_patch_update = $true

# 本脚本创建并删除的目录（注意必须以 $app_name 结尾，且与 myapp.settings 和 repo_settings 保持一致）
$repo_dir = $PSScriptRoot
$temp_dir = "$repo_dir\temp_$app_name"
$app_install_dir = "$env:LOCALAPPDATA\Programs\$app_name"
$app_data_dir = "$env:LOCALAPPDATA\$app_name"
$targets_dir = "$app_data_dir\update_cache\targets"
$all_app_dirs = @($temp_dir, $app_install_dir, $app_data_dir)

# 删除 *my_app 目录，需要确认
function Remove-MyAppDirectory {
    param($Path)
    if ( $Path -match "$app_name$" ) {
        if (Test-Path $Path) {
            # 递归删除该目录，并请求确认
            Remove-Item $Path -Recurse -Confirm
        } else {
            Write-Host "路径不存在: $Path" -ForegroundColor yellow
        }
    } else {
        Write-Host "$app_name 未包含在路径中: $Path" -ForegroundColor yellow
    }
}

# 删除 my_app 相关的所有目录
function Remove-MyApp {
    $all_app_dirs | ForEach-Object { Remove-MyAppDirectory $_ }
}


# 调用 PyInstaller 创建应用程序包
function Invoke-PyInstaller {
    pyinstaller.exe "$repo_dir\main.spec" --clean -y --distpath "$temp_dir\dist" --workpath "$temp_dir\build"
    Assert-ExeSuccess
}


# 删除所有残留目录和文件
Remove-MyApp

# 如果目录不存在，则创建新目录
$all_app_dirs | ForEach-Object {
    if (!(Test-Path $_)) {
        New-Item -Path $_ -ItemType "directory" | Out-Null
        Write-Host "创建目录: $_" -ForegroundColor green
    }
}
New-Item -Path $targets_dir -ItemType "directory" -Force | Out-Null

# 本脚本需要一个已激活的 Python 环境，并且已安装 tufup（假设在 repo_dir 中有一个虚拟环境）
$venv_path = "$repo_dir\venv\Scripts\activate.ps1"
if (Test-Path $venv_path) {
    & $venv_path
    Write-Host "虚拟环境已激活" -ForegroundColor green
} else {
    Write-Host "未找到虚拟环境" -ForegroundColor red
}

# 确保 Python 可以找到 myapp
$Env:PYTHONPATH += ";$repo_dir\src"

# 初始化新仓库
Write-Host "为 $app_name 初始化 TUF 仓库" -ForegroundColor green
python "$repo_dir\repo_init.py"
Assert-ExeSuccess

# 使用 PyInstaller 创建 my_app v1.0 版本
Write-Host "创建 $app_name v1.0 版本的捆绑包" -ForegroundColor green
Invoke-PyInstaller

# 将 my_app v1.0 添加到 tufup 仓库
Write-Host "将 $app_name v1.0 添加到仓库" -ForegroundColor green
python "$repo_dir\repo_add_bundle.py"
Assert-ExeSuccess


# 模拟安装 my_app v1.0
Write-Host "在 $app_install_dir 安装 $app_name v1.0" -ForegroundColor green
$myapp_v1_archive = "$temp_dir\repository\targets\$app_name-1.0.tar.gz"
tar -xf $myapp_v1_archive --directory=$app_install_dir

# 为启用补丁更新，将存档复制到目标目录
if ($enable_patch_update) {
    Write-Host "启用补丁更新" -ForegroundColor green
    Copy-Item $myapp_v1_archive -Destination $targets_dir
}

# 模拟开发 my_app v2.0（修改源代码版本号）
Write-Host "将 $app_name 版本临时提升至 v2.0" -ForegroundColor green
$settings_path = "$repo_dir\src\myapp\settings.py"
(Get-Content -Path $settings_path -Encoding UTF8).Replace("1.0", "2.0") | Set-Content -Path $settings_path -Encoding UTF8

# 使用 PyInstaller 创建 my_app v2.0 版本
Write-Host "创建 $app_name v2.0 版本的捆绑包" -ForegroundColor green
Invoke-PyInstaller

# 将 my_app v2.0 添加到 tufup 仓库
Write-Host "将 $app_name v2.0 添加到仓库" -ForegroundColor green
python "$repo_dir\repo_add_bundle.py"
Assert-ExeSuccess

# 回滚源代码的临时修改
Write-Host "回滚源代码的临时修改" -ForegroundColor green
(Get-Content -Path $settings_path -Encoding UTF8).Replace("2.0", "1.0") | Set-Content -Path $settings_path -Encoding UTF8

# 启动更新服务器
Write-Host "启动更新服务器" -ForegroundColor green
$job = Start-Job -ArgumentList @("$temp_dir\repository") -ScriptBlock {
    param($repository_path)
    python -m http.server -d $repository_path
    Assert-ExeSuccess
}
sleep 1  # 稍作等待，以确保服务器启动成功

# 运行 my_app 执行更新（从 v1 更新到 v2）
Write-Host "运行 $app_name 以进行更新..." -ForegroundColor green
& "$app_install_dir\main.exe"
Assert-ExeSuccess

# 再次运行 my_app 确认已更新到 v2.0
Write-Host "更新完成后按回车键继续:"  -ForegroundColor yellow -NoNewLine
Read-Host  # 不显示输入内容
Write-Host "再次运行 $app_name 以确认版本" -ForegroundColor green
$output = & "$app_install_dir\main.exe"
Assert-ExeSuccess

# 停止更新服务器
Write-Host "停止服务器" -ForegroundColor green
$job | Stop-Job

# 测试输出结果
$pattern = "$app_name 2.0"
if ( $output -match $pattern ) {
  Write-Host "`n成功: 找到 $pattern" -ForegroundColor green
} else {
  Write-Host "`n失败: 未找到 $pattern，输出为:`n$output" -ForegroundColor red
  exit 1
}

# 提醒用户清理残留文件
$remaining = 0
$all_app_dirs | ForEach-Object {
    if (Test-Path $_) {
        Write-Host "$app_name 的文件残留在: $_" -ForegroundColor yellow
        $remaining += 1
    }
}
if ($remaining) {
    Write-Host "是否要删除这些目录?" -ForegroundColor yellow
    if ((Read-Host "[y]/n") -in "", "y") {
        Remove-MyApp
    }
}

