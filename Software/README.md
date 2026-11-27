# Software Implementation – Wokwi Simulation

This folder contains the software simulation of the **IoT-Enabled Smart Water Quality Monitoring System Using Machine Learning-Based Classification**, developed using the Wokwi online simulation platform.

## 1. Simulation Overview

The system simulates water quality monitoring using nine parameters:

- pH
- Turbidity
- Temperature
- Total Dissolved Solids (TDS)
- Lead
- Cadmium
- Dissolved Oxygen (DO)
- Ammonia
- Nitrate

The simulation generates water quality data, which is communicated to a Python application for processing and machine learning-based classification.

## 2. Technologies and Tools Used

- **Wokwi:** ESP32-based hardware simulation
- **Python:** Data processing and machine learning implementation
- **MQTT:** Communication between the simulation and Python application
- **Machine Learning:** Water quality classification
- **Random Forest:** Classification algorithm
- **Google Colab:** Model development and evaluation

## 3. Main Implementation Modules

1. ESP32-based Wokwi simulation
2. Simulated water quality data generation
3. MQTT-based data communication
4. Python-based data processing
5. Random Forest model training and classification
6. Model performance evaluation and result visualization

## 4. System Workflow

1. Water quality parameters are simulated using Wokwi.
2. Simulated sensor readings are communicated through MQTT.
3. Python receives and processes the incoming data.
4. The Random Forest model performs water quality classification.
5. Model performance is evaluated and results are visualized.

## 5. Objective

The objective of this implementation is to simulate an IoT-based water quality monitoring system and evaluate water quality classification using machine learning techniques.
