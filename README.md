# Wireless Signal Scanner

## Overview
This project uses Software Defined Radio (SDR) devices like HackRF One and BladeRF to scan for various wireless signals including Bluetooth, Wi-Fi, LTE, and NFC. It provides an easy way to analyze the signal strength, frequency range, and application type across different wireless standards.

## Prerequisites
- Python 3.x
- SDR device (HackRF One or BladeRF)
- GNU Radio installed on host

## Installation

### Clone the repository
```bash
git clone https://github.com/yourusername/wireless-signal-scanner.git
cd wireless-signal-scanner
```

### Install dependencies
```bash
pip install -r requirements.txt
```

## Usage
Before running the script, ensure your SDR device is connected. Then execute:
```bash
python scanner.py
```

## Configuration
You can modify the scanning parameters directly in the script to adjust the frequency ranges, duration per step, and threshold values according to your requirements.
