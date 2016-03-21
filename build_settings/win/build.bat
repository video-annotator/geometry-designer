set WINPYDIR=C:\Users\swp\Python\WinPython-32bit-2.7.10\python-2.7.10
set WINPYVER=2.7.10
set HOME=%WINPYDIR%\..\settings
set WINPYARCH="WIN32"

set PATH=%WINPYDIR%\Lib\site-packages\PyQt4;%WINPYDIR%\;%WINPYDIR%\DLLs;%WINPYDIR%\Scripts;%WINPYDIR%\..\tools;

rem keep nbextensions in Winpython directory, rather then %APPDATA% default
set JUPYTER_DATA_DIR=%WINPYDIR%\..\settings

set PROJECTNAME=geometry-designer
set BUILDSETTINGSDIR=%WORKSPACE%\build_settings\win
set MAINSCRIPT=%WORKSPACE%\geometry_designer\__main__.py
set BUILDOUTDIR=%WORKSPACE%\build
set DISTOUTDIR=%WORKSPACE%\dist
set ICONNAME=cf_icon_128x128.ico
set DEV_VERSION=_v0.0.1.dev1

rem echo %WORKSPACE%
rem echo %PROJECTNAME%
rem echo %BUILDSETTINGSDIR%
rem echo %MAINSCRIPT%
rem echo %BUILDOUTDIR%
rem echo %DISTOUTDIR%

@RD /S /Q %BUILDOUTDIR%
@RD /S /Q %DISTOUTDIR%

pip uninstall -y pyforms

pip install https://github.com/UmSenhorQualquer/pyforms/archive/master.zip

pip show pyforms


rem echo "Running pyinstaller --additional-hooks-dir %BUILDSETTINGSDIR%\hooks --name %PROJECTNAME% --icon %BUILDSETTINGSDIR%\%ICONNAME% --onefile %MAINSCRIPT%"

pyinstaller --additional-hooks-dir "%BUILDSETTINGSDIR%\hooks" --name "%PROJECTNAME%%DEV_VERSION%" --icon "%BUILDSETTINGSDIR%\%ICONNAME% --onefile %MAINSCRIPT%"