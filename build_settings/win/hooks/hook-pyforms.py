from PyInstaller.utils.hooks import collect_data_files

hiddenimports = ["pyforms.controls"]

datas = collect_data_files('pyforms')
