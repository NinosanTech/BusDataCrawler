#FROM mcr.microsoft.com/dotnet/framework/runtime:4.8-windowsservercore-ltsc2019
FROM python:3.12

WORKDIR ./deployment/

#COPY deployment/ChromeSetup.exe .
#RUN ["c:/deployment/ChromeSetup.exe", "FilePath", "./Chrome/", "/silent", "/install"]
#RUN export PATH=$PATH:c:/deployment/Chrome/Application/chrome.exe
#RUN setx /M PATH “%PATH%;%c:/deployment/Chrome/Application/chrome.exe%”

COPY ./requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY ./BusPlatformCrawler/ ./src/BusPlatformCrawler/
COPY ./DataCrawler/ ./src
COPY ./Helper/ ./src/Helper/
EXPOSE 5000

CMD ["python", "-u", "./src/main.py"]
