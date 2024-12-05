# DISCLAIMER:
# ���ű����Զ�������ϵͳ�д�����ʾ�� "my_app" ��ص��ļ�������֮��ɾ�����ǡ�ɾ��ǰ������ȷ�ϡ�
# ʹ�÷������û��е���
#
# ���ű�ִ�� README �еĲ��裬���ǲֿ�˺Ϳͻ��˵Ĳ�����
# �书���� GitHub workflow �е� test-update-cycle.yml ������ͬ��ֻ���������ڱ��ؿ����������ֶ����Ը����㡣
#
# - ��ʼ��һ���µ�ʾ���ֿ⵽ .\temp_my_app Ŀ¼������������Կ�⣩
# - ʹ�� pyinstaller ���� my_app v1.0 �汾�������
# - �� my_app v1.0 ��ӵ� tufup �ֿ�
# - �� <localappdata>\Programs\my_app ��װ my_app v1.0�����ݴ洢�� <localappdata>\my_app
# - ģ�⿪�� my_app v2.0
# - ʹ�� pyinstaller ���� my_app v2.0 �汾�������
# - �� my_app v2.0 ��ӵ� tufup �ֿ�
# - �������·����������� my_app �� v1 ���µ� v2
#
# ����ű��޷�ִ�У������������
#   `Set-ExecutionPolicy AllSigned`
# �ο�: https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.core/about/about_scripts
#
# ��Ҫע����ǣ����ǿ���ֱ���� GitHub workflow �����д˽ű���������������ֳɶ���������ڵ���ʧ�ܡ�


# ����������д��������˳�
$ErrorActionPreference = "stop"

# ��ִ���ļ�����ʱ�˳������ڿ�ִ���ļ�����֮��
function Assert-ExeSuccess {
    if (!$?) {
        # $? �����ϴ������ִ��״̬���ɹ���Ϊ true��
        Write-Error "failed"
    }
}


# ����
$app_name = "my_app"
$enable_patch_update = $true

# ���ű�������ɾ����Ŀ¼��ע������� $app_name ��β������ myapp.settings �� repo_settings ����һ�£�
$repo_dir = $PSScriptRoot
$temp_dir = "$repo_dir\temp_$app_name"
$app_install_dir = "$env:LOCALAPPDATA\Programs\$app_name"
$app_data_dir = "$env:LOCALAPPDATA\$app_name"
$targets_dir = "$app_data_dir\update_cache\targets"
$all_app_dirs = @($temp_dir, $app_install_dir, $app_data_dir)

# ɾ�� *my_app Ŀ¼����Ҫȷ��
function Remove-MyAppDirectory {
    param($Path)
    if ( $Path -match "$app_name$" ) {
        if (Test-Path $Path) {
            # �ݹ�ɾ����Ŀ¼��������ȷ��
            Remove-Item $Path -Recurse -Confirm
        } else {
            Write-Host "·��������: $Path" -ForegroundColor yellow
        }
    } else {
        Write-Host "$app_name δ������·����: $Path" -ForegroundColor yellow
    }
}

# ɾ�� my_app ��ص�����Ŀ¼
function Remove-MyApp {
    $all_app_dirs | ForEach-Object { Remove-MyAppDirectory $_ }
}


# ���� PyInstaller ����Ӧ�ó����
function Invoke-PyInstaller {
    pyinstaller.exe "$repo_dir\main.spec" --clean -y --distpath "$temp_dir\dist" --workpath "$temp_dir\build"
    Assert-ExeSuccess
}


# ɾ�����в���Ŀ¼���ļ�
Remove-MyApp

# ���Ŀ¼�����ڣ��򴴽���Ŀ¼
$all_app_dirs | ForEach-Object {
    if (!(Test-Path $_)) {
        New-Item -Path $_ -ItemType "directory" | Out-Null
        Write-Host "����Ŀ¼: $_" -ForegroundColor green
    }
}
New-Item -Path $targets_dir -ItemType "directory" -Force | Out-Null

# ���ű���Ҫһ���Ѽ���� Python �����������Ѱ�װ tufup�������� repo_dir ����һ�����⻷����
$venv_path = "$repo_dir\venv\Scripts\activate.ps1"
if (Test-Path $venv_path) {
    & $venv_path
    Write-Host "���⻷���Ѽ���" -ForegroundColor green
} else {
    Write-Host "δ�ҵ����⻷��" -ForegroundColor red
}

# ȷ�� Python �����ҵ� myapp
$Env:PYTHONPATH += ";$repo_dir\src"

# ��ʼ���²ֿ�
Write-Host "Ϊ $app_name ��ʼ�� TUF �ֿ�" -ForegroundColor green
python "$repo_dir\repo_init.py"
Assert-ExeSuccess

# ʹ�� PyInstaller ���� my_app v1.0 �汾
Write-Host "���� $app_name v1.0 �汾�������" -ForegroundColor green
Invoke-PyInstaller

# �� my_app v1.0 ��ӵ� tufup �ֿ�
Write-Host "�� $app_name v1.0 ��ӵ��ֿ�" -ForegroundColor green
python "$repo_dir\repo_add_bundle.py"
Assert-ExeSuccess


# ģ�ⰲװ my_app v1.0
Write-Host "�� $app_install_dir ��װ $app_name v1.0" -ForegroundColor green
$myapp_v1_archive = "$temp_dir\repository\targets\$app_name-1.0.tar.gz"
tar -xf $myapp_v1_archive --directory=$app_install_dir

# Ϊ���ò������£����浵���Ƶ�Ŀ��Ŀ¼
if ($enable_patch_update) {
    Write-Host "���ò�������" -ForegroundColor green
    Copy-Item $myapp_v1_archive -Destination $targets_dir
}

# ģ�⿪�� my_app v2.0���޸�Դ����汾�ţ�
Write-Host "�� $app_name �汾��ʱ������ v2.0" -ForegroundColor green
$settings_path = "$repo_dir\src\myapp\settings.py"
(Get-Content $settings_path).Replace("1.0", "2.0") | Set-Content $settings_path

# ʹ�� PyInstaller ���� my_app v2.0 �汾
Write-Host "���� $app_name v2.0 �汾�������" -ForegroundColor green
Invoke-PyInstaller

# �� my_app v2.0 ��ӵ� tufup �ֿ�
Write-Host "�� $app_name v2.0 ��ӵ��ֿ�" -ForegroundColor green
python "$repo_dir\repo_add_bundle.py"
Assert-ExeSuccess

# �ع�Դ�������ʱ�޸�
Write-Host "�ع�Դ�������ʱ�޸�" -ForegroundColor green
(Get-Content $settings_path).Replace("2.0", "1.0") | Set-Content $settings_path

# �������·�����
Write-Host "�������·�����" -ForegroundColor green
$job = Start-Job -ArgumentList @("$temp_dir\repository") -ScriptBlock {
    param($repository_path)
    python -m http.server -d $repository_path
    Assert-ExeSuccess
}
sleep 1  # �����ȴ�����ȷ�������������ɹ�

# ���� my_app ִ�и��£��� v1 ���µ� v2��
Write-Host "���� $app_name �Խ��и���..." -ForegroundColor green
& "$app_install_dir\main.exe"
Assert-ExeSuccess

# �ٴ����� my_app ȷ���Ѹ��µ� v2.0
Write-Host "������ɺ󰴻س�������:"  -ForegroundColor yellow -NoNewLine
Read-Host  # ����ʾ��������
Write-Host "�ٴ����� $app_name ��ȷ�ϰ汾" -ForegroundColor green
$output = & "$app_install_dir\main.exe"
Assert-ExeSuccess

# ֹͣ���·�����
Write-Host "ֹͣ������" -ForegroundColor green
$job | Stop-Job

# ����������
$pattern = "$app_name 2.0"
if ( $output -match $pattern ) {
  Write-Host "`n�ɹ�: �ҵ� $pattern" -ForegroundColor green
} else {
  Write-Host "`nʧ��: δ�ҵ� $pattern�����Ϊ:`n$output" -ForegroundColor red
  exit 1
}

# �����û���������ļ�
$remaining = 0
$all_app_dirs | ForEach-Object {
    if (Test-Path $_) {
        Write-Host "$app_name ���ļ�������: $_" -ForegroundColor yellow
        $remaining += 1
    }
}
if ($remaining) {
    Write-Host "�Ƿ�Ҫɾ����ЩĿ¼?" -ForegroundColor yellow
    if ((Read-Host "[y]/n") -in "", "y") {
        Remove-MyApp
    }
}

