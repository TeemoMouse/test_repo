@ECHO OFF
chcp 65001
IF [%1] == [] (
    GOTO EOF
)

CD "./projects"
hexo init %1
CD %1
npm install
EXIT

:EOF
ECHO Erro: No Input.
PAUSE