import sys
from cx_Freeze import setup, Executable

# Dependencies are automatically detected, but it might need fine tuning.
build_exe_options = {
    "include_files":['run_driver.bat','run_driver.ini','run_driver.yaml', ],
    "includes": ["argparse",],
    "excludes": ["tkinter", "unittest"],
    "zip_include_packages": ["encodings", "PySide6"],
}

# base="Win32GUI" should be used only for Windows GUI app
# base = "Win32GUI" if sys.platform == "win32" else None

setup(
    name="corelims_online",
    version="0.0.3",
    description="coreLIMS online analyzer communications",
    options={"build_exe": build_exe_options},
    executables=[Executable("run_driver.py")],
)
