from cx_Freeze import setup, Executable

base = None
#if sys.platform == "win32":
#    base = "Win32GUI"

executables = [Executable("create_idents.py", base=base)]

packages = ["idna"]
options = {
    'build_exe': {
        'packages':packages,
    },
}

setup(
    name = "Auto ID Generation(Temp)",
    options = options,
    version = "1.0",
    description = '',
    executables = executables
)