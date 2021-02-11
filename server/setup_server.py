import sys
from cx_Freeze import setup, Executable

build_exe_options = {
    "packages": ["utils", "logs", "server"],
}
setup(
    name="takmachat_server",
    version="0.0.1",
    description="server for small messaging application",
    options={
        "build_exe": build_exe_options
    },
    executables=[Executable('server.py',
                            # base='Win32GUI',
                            targetName='server.exe',
                            )]
)
