@echo off
setlocal enabledelayedexpansion

set /a "random_number=%RANDOM% %% 30 + 10"
set /a "random_number2=%RANDOM% %% 5 + 1"
for /l %%i in (1,1,5) do (
call :innerLoop
   for /l %%j in (10,1,40) do (
    python main.py %%i %%j
   )
)
endlocal