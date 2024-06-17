# CustomerAppiumScripts

## Description

This project is a simple appium script targetting the Customers application. It navigates through the application in a basic manner. 

## Table of Contents

- [Installation](#installation)
- [Usage](#usage)

## Installation

Use the following pip command to install / view relevant dependencies


# Example installation commands
```
pip install -r requirements.txt
```

## Usage
Use the following command in the project directory to run the Appium script. 

```
# Example usage
python test.py
```

You can change the target device in the desired capabilties on line 82. This would be the `deviceId` outlined below. 

```
capabilities = dict(
    platformName='Android',
    automationName='uiautomator2',
    deviceName='Android',
    deviceId='emulator-5554',
    language='en',
    locale='US',
    noReset=True,
    autoLaunch=False
)
```

You can also toggle the application being launched an terminated on lines 101 and 106. That can be seen below in as the `activate_app()` and `terminate_app()` functions. The app start lifecycle is handled by our analysis process so there is no need to launch the app. 

```
    driver.activate_app('app-package')
    
    driver.terminate_app('app-package')