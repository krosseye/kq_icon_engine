# ruff: noqa: N999 - PyInstaller requires this file name
from PyInstaller.utils.hooks import collect_data_files

datas = collect_data_files("kq_icon_engine")
