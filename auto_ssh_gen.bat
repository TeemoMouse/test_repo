@ECHO OFF
IF EXIST C:\Users\user\.ssh\id_ed25519.pub GOTO END
ECHO Generating SSH key...
ssh-keygen -t ed25519 -q -N ""

:END
clip < C:\Users\user\.ssh\id_ed25519.pub