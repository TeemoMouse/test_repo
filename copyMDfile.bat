@ECHO OFF
chcp 65001
XCOPY ".\md\%2" ".\projects\%1\source\_posts\%2*" /Y /V /Q