@echo off
set in_dir=%1
echo %in_dir%
mkdir "out/%in_dir%"

for %%f in (%in_dir%/*.wav) do (
    echo %%f
    sox %in_dir%/%%f out/%in_dir%/%%f silence 1 0.1 1% reverse silence 1 0.1 1% pad 0 0.1
)
EXIT /b 0