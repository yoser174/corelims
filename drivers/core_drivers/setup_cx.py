import sys
from cx_Freeze import setup, Executable

build_exe_options = {"packages": ["ConfigParser"], "excludes": [""]}

base = None
#if sys.platform == "win32":
#    base = "Win32GUI"

setup(name="SIMDONDAR-Interface [e601]",
      version="0.1",
      description="Interface dengan sistem SIMDONDAR",
      options = {"build_exe":build_exe_options },
      executables= [Executable("run_driver.py", base=base)]
      )
