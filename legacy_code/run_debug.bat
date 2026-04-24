@echo off
cd /d %~dp0
python -u debug_generate.py > test_result.txt 2>&1
type test_result.txt
pause
