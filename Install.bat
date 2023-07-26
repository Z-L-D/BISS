:: Create python local environment
python -m venv env
call .\env\Scripts\activate.bat

:: Install python dependences
pip install -r requirements.txt

:: Install geckodriver
cd env
IF NOT EXIST bin\ (
	mkdir bin
)
cd bin
IF NOT EXIST geckodriver.exe (
	powershell -Command "Invoke-WebRequest -OutFile geckodriver.zip -Uri https://github.com/mozilla/geckodriver/releases/download/v0.33.0/geckodriver-v0.33.0-win32.zip"
    	powershell -Command "Expand-Archive -Path geckodriver.zip -DestinationPath ."
    	del geckodriver.zip
)

cd ..\..


echo python -m venv env > Run.bat
echo call .\env\Scripts\activate.bat >> Run.bat
echo python biss.py >> Run.bat
echo cmd /k >> Run.bat

