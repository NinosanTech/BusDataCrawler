@echo off
setlocal

::az login --tenant e8564b73-3b06-442c-9d26-e9ba68e73a33

docker login
echo Tagging selenium container
docker tag newvenv-selenium:latest ninohamburg/newvenv-selenium:latest >nul
echo Pushing selenium container
docker push ninohamburg/newvenv-selenium:latest >nul
echo Tagging python container
docker tag newvenv-selenium_python:latest ninohamburg/newvenv-selenium_python:latest >nul
echo Pushing python container
docker push ninohamburg/newvenv-selenium_python:latest >nul

REM Try block
echo Deleting azure container
az container delete --name Webscraper --resource-group Webscraper --yes >nul

echo Warten, bis der Container gelöscht wurde
:check_deletion
call az container show --name Webscraper --resource-group Webscraper >nul 2>&1 >nul
if %errorlevel%==0 (
    echo Container existiert noch, warte und überprüfe erneut
    timeout /t 10 >nul
    goto check_deletion
)

echo Creating new azure container
az container create --resource-group Webscraper --file azure_deploy.yml >nul

echo Finished!
endlocal