@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion
set "SRC=%~dp0"
set "TARGET=%LOCALAPPDATA%\hermes\skills\productivity\md-to-pdf"

echo ============================================
echo  md-to-pdf 技能包安装
echo ============================================

where pandoc >nul 2>nul
if errorlevel 1 (
  echo [1/4] 未找到 pandoc，用 winget 安装...
  winget install --id JohnMacFarlane.Pandoc -e --accept-source-agreements --accept-package-agreements
  if errorlevel 1 (
    echo     pandoc 安装失败，请手动装 https://pandoc.org/installing.html 后重跑
    pause
    exit /b 1
  )
) else (
  echo [1/4] pandoc 已存在
)

where typst >nul 2>nul
if errorlevel 1 (
  for %%D in ("%LOCALAPPDATA%\Microsoft\WinGet\Links\typst.exe") do if exist %%D goto :hastypst
  echo [2/4] 未找到 typst，用 winget 安装...
  winget install --id Typst.Typst -e --accept-source-agreements --accept-package-agreements
  if errorlevel 1 (
    echo     typst 安装失败，请手动装 https://github.com/typst/typst/releases 后重跑
    pause
    exit /b 1
  )
  goto :typostdone
)
:hastypst
echo [2/4] typst 已存在
:typostdone

set "PY=python"
%PY% -c "import sys" >nul 2>nul
if errorlevel 1 set "PY=py -3"

%PY% -c "import PIL" >nul 2>nul
if errorlevel 1 (
  echo [3/4] 安装 pillow（图片宽度检测用）...
  %PY% -m pip install pillow
) else (
  echo [3/4] pillow 已存在
)

if /i "%SRC%"=="%TARGET%\" (
  echo [4/4] 已经在目标目录，跳过复制
  goto :selfcheck
)
echo [4/4] 安装技能到 %TARGET%
if not exist "%TARGET%" mkdir "%TARGET%"
xcopy "%SRC%." "%TARGET%\" /E /I /Y >nul
if errorlevel 1 (
  echo     复制失败，请检查权限。
  pause
  exit /b 1
)

:selfcheck
%PY% "%TARGET%\scripts\md2pdf.py" "%TARGET%\demo.md" "%TARGET%\demo.pdf"
if exist "%TARGET%\demo.pdf" (
  echo.
  echo 安装成功。演示文件：%TARGET%\demo.pdf
  start "" "%TARGET%\demo.pdf"
) else (
  echo 自检失败，请把上面的报错发给我。
)

echo.
echo 完成后请重启 Hermes，让它加载新技能。
pause
