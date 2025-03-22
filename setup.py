from cx_Freeze import setup, Executable 

executables1 = [Executable("main_logic.py", base="Win32GUI",icon = "icon.ico")]

build_exe_options = {
    "packages": ["os", "sys","reportlab","markdown"],
    "include_files" : ["icon.ico"]
}

setup(
    name="Ollama GUI",
    version="1.3",
    description="",
    executables= executables1,
    options = {'build_exe' : build_exe_options }
)
