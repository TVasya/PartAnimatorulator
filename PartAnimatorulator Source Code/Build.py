from cx_Freeze import setup, Executable

setup(
    name="PartAnimatorulator",
    version='0.0.1b',
    author='TerminatorVasya / vskm',
    description='PARTS_ANIMATIONS.bin Editor',
    executables = [
    Executable("F:\Vasya's\PartAnimatorulator\Main.py",
               icon = "F:\Vasya's\PartAnimatorulator\Icon.ico")]
)