@ECHO OFF
chcp 65001
XCOPY ".\md\%2_%3.md" ".\projects\%1\source\_posts\%2*" /Y /V /Q