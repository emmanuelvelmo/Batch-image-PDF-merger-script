from cx_Freeze import setup, Executable

setup(name="Batch image PDF merger", executables=[Executable("Batch image PDF merger script.py")], options={"build_exe": {"excludes": ["tkinter"]}})