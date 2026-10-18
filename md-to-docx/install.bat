@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion
set "SRC=%~dp0"
set "TARGET=%LOCALAPPDATA%\hermes\skills\productivity\md-to-docx"

echo ============================================
echo  md-to-docx 技能包安装
echo ============================================

REM 1) 依赖检查
where pandoc >nul 2>nul
if errorlevel 1 (
  echo [1/3] 未找到 pandoc，尝试用 winget 安装...
  winget install --id JohnMacFarlane.Pandoc -e --accept-source-agreements --accept-package-agreements
  if errorlevel 1 (
    echo     winget 安装失败。请手动安装 https://pandoc.org/installing.html 后重新运行本脚本。
    pause
    exit /b 1
  )
) else (
  echo [1/3] pandoc 已存在
)

set "PY=python"
%PY% -c "import sys" >nul 2>nul
if errorlevel 1 set "PY=py -3"

%PY% -c "import docx" >nul 2>nul
if errorlevel 1 (
  echo [2/3] 安装 python-docx...
  %PY% -m pip install python-docx
) else (
  echo [2/3] python-docx 已存在
)

REM 2) 复制技能包
if /i "%SRC%"=="%TARGET%\" (
  echo [3/3] 已经在目标目录，跳过复制
  goto :selfcheck
)
echo [3/3] 安装技能到 %TARGET%
if not exist "%TARGET%" mkdir "%TARGET%"
xcopy "%SRC%." "%TARGET%\" /E /I /Y >nul
if errorlevel 1 (
  echo     复制失败，请检查权限。
  pause
  exit /b 1
)

:selfcheck
REM 3) 重建模板并自检
if not exist "%TARGET%\scripts\reference.docx" (
  %PY% "%TARGET%\scripts\make_template.py" "%TARGET%\scripts\reference.docx"
)

%PY% "%TARGET%\scripts\md2docx.py" "%SRC%demo.md" "%SRC%demo.docx"
if exist "%SRC%demo.docx" (
  echo.
  echo 安装成功。已生成演示文件：%SRC%demo.docx
  start "" "%SRC%demo.docx"
) else (
  echo 自检失败，请把上面的报错发给我。
)

echo.
echo 完成后请重启 Hermes，让它加载新技能。
pause
