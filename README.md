# ASHRAE CLIMATIC DESIGN CONDITIONS python scrape 

This program is designed to only scrape 2021 weather station data.

The fields that it's specifically designed to scrape is n-Year Return Period Values of Extreme Temperature within the
Extreme Annual Design Conditions table. Only the dry bulb (DB) and wet bulb (WB) Max values are pulled.

The output is a .csv file of the above.

## How to run

Make sure the chromedriver.exe is the correct version for the Selenium version.
As of 2024-04-01, the version of selenium is 4.19.0, which runs on chrome driver version 114.0.5735.90.
In this directory is the correct chromedriver for this time.

Run this in your terminal, it will start a venv and install the packages for that venv:

```
chmod +x startup.sh
./startup.sh
```

## To do in the future

Make it so it can scrape 2009, 2013, 2017, and future dates by adding an argument on which year to scrape. 
Needs to fetch the list of years from the clickable button table.

Maybe at some point just scrape the whole page, but would require creating each data structure per table in the page. 

Actually, the best way to do this is to print/ download the page as a PDF then parse it with some PDF parsing library.

# Stuff I ran into

I'm following this [guide](https://leocode.com/development/automation-with-selenium-and-python-for-beginners/
).

The guide doesn't really work because you need to download a specific Chrome driver because the latest version of Chrome
is not compatible with Selenium.

```
C:\Users\donal\PycharmProjects\ashrae\chromedriver.exe
E       selenium.common.exceptions.SessionNotCreatedException: Message: session not created: This version of ChromeDriver only supports Chrome version 114
E       Current browser version is 123.0.6312.86 with binary path C:\Program Files\Google\Chrome\Application\chrome.exe
```

[Non headless](https://storage.googleapis.com/chrome-for-testing-public/123.0.6312.86/win64/chromedriver-win64.zip)
[Headless](https://storage.googleapis.com/chrome-for-testing-public/123.0.6312.86/win64/chrome-headless-shell-win64.zip)