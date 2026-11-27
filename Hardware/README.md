# Hardware Implementation

This folder contains the physical hardware implementation of the **IoT-Enabled Smart Water Quality Monitoring System Using Machine Learning-Based Classification**.

The system uses an ESP32 microcontroller connected to water quality sensors to collect real-time data. The collected sensor readings are displayed on an LCD and transmitted to the ThingSpeak cloud platform. A Flask-based web application uses a machine learning model to classify water quality.

## 1. Hardware Components

The following components are used in the physical prototype:

- ESP32 DevKit V1
- pH Sensor
- Turbidity Sensor
- TDS Sensor
- DS18B20 Temperature Sensor
- 16x2 I2C LCD Display
- 5V DC Power Supply

## 2. Arduino Implementation

The Arduino code is developed using the Arduino IDE.

The ESP32 collects readings from the four sensors:
- pH
- Turbidity
- Total Dissolved Solids (TDS)
- Temperature

The collected readings are processed by the ESP32 and uploaded to ThingSpeak using Wi-Fi.

**Folder:** `Arduino_Code/`

## 3. ThingSpeak Cloud Dashboard

ThingSpeak is used for cloud-based storage and visualization of sensor readings.

The dashboard displays:
- pH values
- Temperature readings
- Turbidity values
- TDS values
- Water Quality Index (WQI)

**Dashboard Image:** `ThingSpeak_Dashboard.png`

## 4. Flask Web Application

A Flask-based web application is developed to monitor water quality and provide classification results using a trained machine learning model.

The application includes:
- User registration and login
- Water quality prediction
- Machine learning-based classification
- Prediction history
- Telegram alerts for poor or unsafe water quality

**Folder:** `Flask_Application/`

The Flask application uses the trained model, scaler, label encoder, and feature order files stored in the `models/` directory.

## 5. Project Images

- `ESP32_Circuit_Diagram.png` – Circuit diagram of the hardware setup.
- `Hardware_Implementation.png` – Physical hardware prototype.
- `ThingSpeak_Dashboard.png` – Cloud dashboard displaying sensor readings.

## 6. Technologies Used

- ESP32
- Arduino IDE
- Embedded C/C++
- ThingSpeak
- Python
- Flask
- Machine Learning
- SQLite
- Telegram Bot API

## 7. Security Note

Private credentials such as Wi-Fi passwords, ThingSpeak API keys, Telegram bot tokens, and Flask secret keys are not included in the public repository. Refer to `Flask_Application/private_config.example.py` for the configuration template.
