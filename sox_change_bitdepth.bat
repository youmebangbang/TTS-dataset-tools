@echo off
set in_dir=%1
set depth=%2
echo %in_dir% %depth%
mkdir "out/%in_dir%"

for %%f in (%in_dir%/*.wav) do (
    echo %%f
    sox %in_dir%/%%f -b %depth% out/%in_dir%/%%f 
)
EXIT /b 0
