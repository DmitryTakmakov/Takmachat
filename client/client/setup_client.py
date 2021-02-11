import sys
from cx_Freeze import setup, Executable

build_exe_options = {
    "packages": ["utils", "logs", "client"],
}
setup(
    name="takmachat_client",
    version="0.0.1",
    description="client for small messaging application",
    options={
        "build_exe": build_exe_options
    },
    executables=[Executable('client.py',
                            # base='Win32GUI',
                            targetName='client.exe',
                            )]
)
