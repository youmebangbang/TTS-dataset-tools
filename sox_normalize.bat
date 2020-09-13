@echo off
set in_dir=%1
set normalize=%2
echo %in_dir% %normalize%
mkdir "out/%in_dir%"

for %%f in (%in_dir%/*.wav) do (
    echo %%f
    sox %in_dir%/%%f --norm=%normalize% out/%in_dir%/%%f 
)
EXIT /b 0
