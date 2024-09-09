@echo off
setlocal

::az login --tenant e8564b73-3b06-442c-9d26-e9ba68e73a33

docker login
echo Tagging python container
docker tag newvenv-database_migration:latest ninohamburg/newvenv-database_migration:latest >nul
echo Pushing python container
docker push ninohamburg/newvenv-database_migration:latest >nul

REM Try block
echo Deleting azure container
az container delete --name DB-Migration --resource-group Webscraper --yes >nul

echo Warten, bis der Container gelöscht wurde
:check_deletion
call az container show --name DB-Migration --resource-group Webscraper >nul 2>&1 >nul
if %errorlevel%==0 (
    echo Container existiert noch, warte und überprüfe erneut
    timeout /t 10 >nul
    goto check_deletion
)

echo Creating new azure container
az container create --restart-policy Never --resource-group Webscraper --file azure_deploy_db_migration.yml >nul

echo Finished!
endlocal