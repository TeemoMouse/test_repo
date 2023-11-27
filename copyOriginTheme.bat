@ECHO OFF
chcp 65001
IF EXIST "./projects/%1/themes/%3" (
    ECHO Diroctory already exists.
) ELSE (
    XCOPY "./all_origin_themes/%2" "./projects/%1/themes/%3" /Y /E /I
)