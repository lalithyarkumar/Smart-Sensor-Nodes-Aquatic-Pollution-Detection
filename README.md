# Smart Sensor Nodes for Aquatic Pollution Detection

## An IoT-Enabled Smart Water Quality Monitoring System Using Machine Learning-Based Classification

## Project Overview

This project presents an IoT-based smart water quality monitoring system that collects water quality parameters using sensors and applies machine learning techniques to classify water quality.

The system is developed using two implementations: a physical hardware prototype and a software simulation.

## Project Implementations

### 1. Hardware Implementation

The physical prototype uses an ESP32 microcontroller connected to four sensors:

- pH Sensor
- Turbidity Sensor
- TDS Sensor
- DS18B20 Temperature Sensor

The collected readings are displayed on an LCD and transmitted to the ThingSpeak cloud platform using Wi-Fi.

A Flask-based web application integrates a trained machine learning model to classify water quality and provide prediction results.

**Explore:** [Hardware Implementation](Hardware/README.md)

### 2. Software Implementation

The software implementation uses the Wokwi simulation platform to simulate the smart water quality monitoring system with nine water quality parameters.

It incorporates Python, MQTT communication, and a Random Forest machine learning model for water quality classification.

**Explore:** [Software Implementation](Software/README.md)

## Technologies Used

- ESP32
- Arduino IDE
- Embedded C/C++
- Python
- Internet of Things (IoT)
- ThingSpeak
- Flask
- MQTT
- Wokwi
- Machine Learning
- Random Forest
- Support Vector Machine (SVM)

## Repository Structure

```text
Smart-Sensor-Nodes-Aquatic-Pollution-Detection/
│
├── Hardware/
│   ├── Arduino_Code/
│   ├── Flask_Application/
│   ├── Circuit_Diagram/
│   ├── Images/
│   └── README.md
│
├── Software/
│   └── README.md
│
└── README.md
```

## Project Objectives

- Monitor important water quality parameters in real time.
- Collect and transmit sensor data using IoT technology.
- Store and visualize sensor readings through a cloud platform.
- Apply machine learning techniques for water quality classification.
- Provide an accessible system for monitoring water quality.

## Security

Private credentials, including Wi-Fi passwords, API keys, Telegram bot tokens, and secret keys, are excluded from the public repository.

## Project Domain

Internet of Things (IoT) | Embedded Systems | Machine Learning | Water Quality Monitoring
