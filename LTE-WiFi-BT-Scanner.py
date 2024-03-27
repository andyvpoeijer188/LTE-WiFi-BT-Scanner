from gnuradio import gr, blocks, analog
from gnuradio.filter import dc_blocker_cc

from scipy.signal import find_peaks
import numpy as np
import osmosdr
import time
import datetime
import csv
import os

from tqdm import tqdm

# Bluetooth channels and use dictionary, the key is in GHz
bluetooth_channels = {
    2402: {'channel_number': 37, 'frequency_range': (2401, 2403),'application': 'P.Adv'},
    2404: {'channel_number': 0, 'frequency_range': (2403, 2405), 'application': 'Data Ch'},
    2406: {'channel_number': 1, 'frequency_range': (2405, 2407), 'application': 'Data Ch'},
    2408: {'channel_number': 2, 'frequency_range': (2407, 2409), 'application': 'Data Ch'},
    2410: {'channel_number': 3, 'frequency_range': (2409, 2411), 'application': 'Data Ch'},
    2412: {'channel_number': 4, 'frequency_range': (2411, 2413), 'application': 'Data Ch'},
    2414: {'channel_number': 5, 'frequency_range': (2413, 2415), 'application': 'Data Ch'},
    2416: {'channel_number': 6, 'frequency_range': (2415, 2417), 'application': 'Data Ch'},
    2418: {'channel_number': 7, 'frequency_range': (2417, 2419), 'application': 'Data Ch'},
    2420: {'channel_number': 8, 'frequency_range': (2419, 2421), 'application': 'Data Ch'},
    2422: {'channel_number': 9, 'frequency_range': (2421, 2423), 'application': 'Data Ch'},
    2424: {'channel_number': 10, 'frequency_range': (2423, 2425), 'application': 'Data Ch'},
    2426: {'channel_number': 38, 'frequency_range': (2425, 2427), 'application': 'P.Adv'},
    2428: {'channel_number': 11, 'frequency_range': (2427, 2429), 'application': 'Data Ch'},
    2430: {'channel_number': 12, 'frequency_range': (2429, 2431), 'application': 'Data Ch'},
    2432: {'channel_number': 13, 'frequency_range': (2431, 2433), 'application': 'Data Ch'},
    2434: {'channel_number': 14, 'frequency_range': (2433, 2435), 'application': 'Data Ch'},
    2436: {'channel_number': 15, 'frequency_range': (2435, 2437), 'application': 'Data Ch'},
    2438: {'channel_number': 16, 'frequency_range': (2437, 2439), 'application': 'Data Ch'},
    2440: {'channel_number': 17, 'frequency_range': (2439, 2441), 'application': 'Data Ch'},
    2442: {'channel_number': 18, 'frequency_range': (2441, 2443), 'application': 'Data Ch'},
    2444: {'channel_number': 19, 'frequency_range': (2443, 2445), 'application': 'Data Ch'},
    2446: {'channel_number': 20, 'frequency_range': (2445, 2447), 'application': 'Data Ch'},
    2448: {'channel_number': 21, 'frequency_range': (2447, 2449), 'application': 'Data Ch'},
    2450: {'channel_number': 22, 'frequency_range': (2449, 2451), 'application': 'Data Ch'},
    2452: {'channel_number': 23, 'frequency_range': (2451, 2453), 'application': 'Data Ch'},
    2454: {'channel_number': 24, 'frequency_range': (2453, 2455), 'application': 'Data Ch'},
    2456: {'channel_number': 25, 'frequency_range': (2455, 2457), 'application': 'Data Ch'},
    2458: {'channel_number': 26, 'frequency_range': (2457, 2459), 'application': 'Data Ch'},
    2460: {'channel_number': 27, 'frequency_range': (2459, 2461), 'application': 'Data Ch'},
    2462: {'channel_number': 28, 'frequency_range': (2461, 2463), 'application': 'Data Ch'},
    2464: {'channel_number': 29, 'frequency_range': (2463, 2465), 'application': 'Data Ch'},
    2466: {'channel_number': 30, 'frequency_range': (2465, 2467), 'application': 'Data Ch'},
    2468: {'channel_number': 31, 'frequency_range': (2467, 2469), 'application': 'Data Ch'},
    2470: {'channel_number': 32, 'frequency_range': (2469, 2471), 'application': 'Data Ch'},
    2472: {'channel_number': 33, 'frequency_range': (2471, 2473), 'application': 'Data Ch'},
    2474: {'channel_number': 34, 'frequency_range': (2473, 2475), 'application': 'Data Ch'},
    2476: {'channel_number': 35, 'frequency_range': (2475, 2477), 'application': 'Data Ch'},
    2478: {'channel_number': 36, 'frequency_range': (2477, 2479), 'application': 'Data Ch'},
    2480: {'channel_number': 39, 'frequency_range': (2479, 2481), 'application': 'P.Adv'},
}

# Wi-Fi channels dictionary, key is in GHz
wifi_channels = {
    # Wi-Fi 2.4 GHz
    2412: {'channel_number': 1, 'frequency_range': (2401, 2423), 'application': 'Wi-Fi 4'},
    2417: {'channel_number': 2, 'frequency_range': (2406, 2428), 'application': 'Wi-Fi 4'},
    2422: {'channel_number': 3, 'frequency_range': (2411, 2433), 'application': 'Wi-Fi 4'},
    2427: {'channel_number': 4, 'frequency_range': (2416, 2438), 'application': 'Wi-Fi 4'},
    2432: {'channel_number': 5, 'frequency_range': (2421, 2443), 'application': 'Wi-Fi 4'},
    2437: {'channel_number': 6, 'frequency_range': (2426, 2448), 'application': 'Wi-Fi 4'},
    2442: {'channel_number': 7, 'frequency_range': (2431, 2453), 'application': 'Wi-Fi 4'},
    2447: {'channel_number': 8, 'frequency_range': (2436, 2458), 'application': 'Wi-Fi 4'},
    2452: {'channel_number': 9, 'frequency_range': (2441, 2463), 'application': 'Wi-Fi 4'},
    2457: {'channel_number': 10, 'frequency_range': (2446, 2468), 'application': 'Wi-Fi 4'},
    2462: {'channel_number': 11, 'frequency_range': (2451, 2473), 'application': 'Wi-Fi 4'},
    2467: {'channel_number': 12, 'frequency_range': (2456, 2478), 'application': 'Wi-Fi 4'},
    2472: {'channel_number': 13, 'frequency_range': (2461, 2483), 'application': 'Wi-Fi 4'},
    2484: {'channel_number': 14, 'frequency_range': (2473, 2495), 'application': 'Wi-Fi 4'}, 
    
    # Wifi 5.0 GHz
    5180: {'channel_number': 32, 'frequency_range': (5150, 5170), 'application': 'Wi-Fi 5'},
    5180: {'channel_number': 36, 'frequency_range': (5170, 5190), 'application': 'Wi-Fi 5'},
    5200: {'channel_number': 40, 'frequency_range': (5190, 5210), 'application': 'Wi-Fi 5'},
    5220: {'channel_number': 44, 'frequency_range': (5210, 5230), 'application': 'Wi-Fi 5'},
    5240: {'channel_number': 48, 'frequency_range': (5230, 5250), 'application': 'Wi-Fi 5'},
    5260: {'channel_number': 52, 'frequency_range': (5250, 5270), 'application': 'Wi-Fi 5'},
    5280: {'channel_number': 56, 'frequency_range': (5270, 5290), 'application': 'Wi-Fi 5'},
    5300: {'channel_number': 60, 'frequency_range': (5290, 5310), 'application': 'Wi-Fi 5'},
    5320: {'channel_number': 64, 'frequency_range': (5310, 5330), 'application': 'Wi-Fi 5'},
    5340: {'channel_number': 68, 'frequency_range': (5330, 5350), 'application': 'Wi-Fi 5'},
    5360: {'channel_number': 72, 'frequency_range': (5350, 5370), 'application': 'Wi-Fi 5'},
    5380: {'channel_number': 76, 'frequency_range': (5370, 5390), 'application': 'Wi-Fi 5'},
    5400: {'channel_number': 80, 'frequency_range': (5390, 5410), 'application': 'Wi-Fi 5'},
    5420: {'channel_number': 84, 'frequency_range': (5410, 5430), 'application': 'Wi-Fi 5'},
    5440: {'channel_number': 88, 'frequency_range': (5430, 5450), 'application': 'Wi-Fi 5'},
    5460: {'channel_number': 92, 'frequency_range': (5450, 5470), 'application': 'Wi-Fi 5'},
    5480: {'channel_number': 96, 'frequency_range': (5470, 5490), 'application': 'Wi-Fi 5'},
    5500: {'channel_number': 100, 'frequency_range': (5490, 5510), 'application': 'Wi-Fi 5'},
    5520: {'channel_number': 104, 'frequency_range': (5510, 5530), 'application': 'Wi-Fi 5'},
    5540: {'channel_number': 108, 'frequency_range': (5530, 5550), 'application': 'Wi-Fi 5'},
    5560: {'channel_number': 112, 'frequency_range': (5550, 5570), 'application': 'Wi-Fi 5'},
    5580: {'channel_number': 116, 'frequency_range': (5570, 5590), 'application': 'Wi-Fi 5'},
    5600: {'channel_number': 120, 'frequency_range': (5590, 5610), 'application': 'Wi-Fi 5'},
    5620: {'channel_number': 124, 'frequency_range': (5610, 5630), 'application': 'Wi-Fi 5'},
    5640: {'channel_number': 128, 'frequency_range': (5630, 5650), 'application': 'Wi-Fi 5'},
    5660: {'channel_number': 132, 'frequency_range': (5650, 5670), 'application': 'Wi-Fi 5'},
    5680: {'channel_number': 136, 'frequency_range': (5670, 5690), 'application': 'Wi-Fi 5'},
    5700: {'channel_number': 140, 'frequency_range': (5690, 5710), 'application': 'Wi-Fi 5'},
    5720: {'channel_number': 144, 'frequency_range': (5710, 5730), 'application': 'Wi-Fi 5'},
    5745: {'channel_number': 149, 'frequency_range': (5735, 5755), 'application': 'Wi-Fi 5'},
    5785: {'channel_number': 157, 'frequency_range': (5775, 5795), 'application': 'Wi-Fi 5'},
    5805: {'channel_number': 161, 'frequency_range': (5795, 5815), 'application': 'Wi-Fi 5'},
    5825: {'channel_number': 165, 'frequency_range': (5815, 5835), 'application': 'Wi-Fi 5'},
    5845: {'channel_number': 169, 'frequency_range': (5835, 5855), 'application': 'Wi-Fi 5'},
    5865: {'channel_number': 173, 'frequency_range': (5855, 5875), 'application': 'Wi-Fi 5'},
    5885: {'channel_number': 177, 'frequency_range': (5875, 5895), 'application': 'Wi-Fi 5'},
}

# NFC channel dictionary, key is in GHz
nfc_bands = {
    0.01356: {'frequency_range': (0.01354, 0.01358), 'application': 'NFC'}
}

# LTE channels dictionary, key is in GHz
lte_bands = {
    2100: {'band_number': 1, 'application': 'LTE', 'name': 'IMT', 'duplex_mode': 'FDD',
           'uplink_frequency_range': (1920, 1980), 'downlink_frequency_range': (2110, 2170),
           'channel_bandwidths': [5, 10, 15, 20]},
    1900: {'band_number': 2, 'application': 'LTE', 'name': 'PCS', 'duplex_mode': 'FDD',
           'uplink_frequency_range': (1850, 1910), 'downlink_frequency_range': (1930, 1990),
           'channel_bandwidths': [1.4, 3, 5, 10, 15, 20]},
    1800: {'band_number': 3, 'application': 'LTE', 'name': 'DCS', 'duplex_mode': 'FDD',
           'uplink_frequency_range': (1710, 1785), 'downlink_frequency_range': (1805, 1880),
           'channel_bandwidths': [1.4, 3, 5, 10, 15, 20]},
    1700: {'band_number': 4, 'application': 'LTE', 'name': 'AWS-1', 'duplex_mode': 'FDD',
           'uplink_frequency_range': (1710, 1755), 'downlink_frequency_range': (2110, 2155),
           'channel_bandwidths': [1.4, 3, 5, 10, 15, 20]},
    850: {'band_number': 5, 'application': 'LTE', 'name': 'Cellular', 'duplex_mode': 'FDD',
          'uplink_frequency_range': (824, 849), 'downlink_frequency_range': (869, 894),
          'channel_bandwidths': [1.4, 3, 5, 10]},
    2600: {'band_number': 7, 'application': 'LTE', 'name': 'IMT-E', 'duplex_mode': 'FDD',
           'uplink_frequency_range': (2500, 2570), 'downlink_frequency_range': (2620, 2690),
           'channel_bandwidths': [5, 10, 15, 20]},
    900: {'band_number': 8, 'application': 'LTE', 'name': 'Extended GSM', 'duplex_mode': 'FDD',
          'uplink_frequency_range': (880, 915), 'downlink_frequency_range': (925, 960),
          'channel_bandwidths': [1.4, 3, 5, 10]},
    700: {'band_number': 12, 'application': 'LTE', 'name': 'Lower SMH', 'duplex_mode': 'FDD',
          'uplink_frequency_range': (699, 716), 'downlink_frequency_range': (729, 746),
          'channel_bandwidths': [1.4, 3, 5, 10]},
    1500: {'band_number': 11, 'application': 'LTE', 'name': 'Lower PDC (Japan)', 'duplex_mode': 'FDD',
           'uplink_frequency_range': (1427.9, 1447.9), 'downlink_frequency_range': (1475.9, 1495.9),
           'channel_bandwidths': [5, 10]},
    700: {'band_number': 13, 'application': 'LTE', 'name': 'Upper SMH', 'duplex_mode': 'FDD',
          'uplink_frequency_range': (777, 787), 'downlink_frequency_range': (746, 756),
          'channel_bandwidths': [5, 10]},
    700: {'band_number': 14, 'application': 'LTE', 'name': 'Upper SMH', 'duplex_mode': 'FDD',
          'uplink_frequency_range': (788, 798), 'downlink_frequency_range': (758, 768),
          'channel_bandwidths': [5, 10]},
    700: {'band_number': 17, 'application': 'LTE', 'name': 'Lower SMH', 'duplex_mode': 'FDD',
          'uplink_frequency_range': (704, 716), 'downlink_frequency_range': (734, 746),
          'channel_bandwidths': [5, 10]},
    850: {'band_number': 18, 'application': 'LTE', 'name': 'Lower 800 (Japan)', 'duplex_mode': 'FDD',
           'uplink_frequency_range': (815, 830), 'downlink_frequency_range': (860, 875),
           'channel_bandwidths': [5, 10, 15]},
    850: {'band_number': 19, 'application': 'LTE', 'name': 'Upper 800 (Japan)', 'duplex_mode': 'FDD',
           'uplink_frequency_range': (830, 845), 'downlink_frequency_range': (875, 890),
           'channel_bandwidths': [5, 10, 15]},
    800: {'band_number': 20, 'application': 'LTE', 'name': 'Digital Dividend (EU)', 'duplex_mode': 'FDD',
           'uplink_frequency_range': (832, 862), 'downlink_frequency_range': (791, 821),
           'channel_bandwidths': [5, 10, 15, 20]},
    1500: {'band_number': 21, 'application': 'LTE', 'name': 'Upper PDC (Japan)', 'duplex_mode': 'FDD',
           'uplink_frequency_range': (1447.9, 1462.9), 'downlink_frequency_range': (1495.9, 1510.9),
           'channel_bandwidths': [5, 10, 15]},
    1600: {'band_number': 24, 'application': 'LTE', 'name': 'Upper L-Band (US)', 'duplex_mode': 'FDD',
           'uplink_frequency_range': (1626.5, 1660.5), 'downlink_frequency_range': (1525, 1559),
           'channel_bandwidths': [5, 10]},
    1900: {'band_number': 25, 'application': 'LTE', 'name': 'Extended PCS', 'duplex_mode': 'FDD',
           'uplink_frequency_range': (1850, 1915), 'downlink_frequency_range': (1930, 1995),
           'channel_bandwidths': [1.4, 3, 5, 10, 15, 20]},
    850: {'band_number': 26, 'application': 'LTE', 'name': 'Extended Cellular', 'duplex_mode': 'FDD',
           'uplink_frequency_range': (814, 849), 'downlink_frequency_range': (859, 894),
           'channel_bandwidths': [1.4, 3, 5, 10, 15]},
    700: {'band_number': 28, 'application': 'LTE', 'name': 'APT', 'duplex_mode': 'FDD',
           'uplink_frequency_range': (703, 748), 'downlink_frequency_range': (758, 803),
           'channel_bandwidths': [3, 5, 10, 15, 20]},
    700: {'band_number': 29, 'application': 'SDL', 'name': 'Lower SMH', 'duplex_mode': 'SDL',
           'downlink_frequency_range': (717, 728),
           'channel_bandwidths': [3, 5, 10]},
    2300: {'band_number': 30, 'application': 'LTE', 'name': 'WCS', 'duplex_mode': 'FDD',
           'uplink_frequency_range': (2305, 2315), 'downlink_frequency_range': (2350, 2360),
           'channel_bandwidths': [5, 10]},
    450: {'band_number': 31, 'application': 'LTE', 'name': 'NMT', 'duplex_mode': 'FDD',
           'uplink_frequency_range': (452.5, 457.5), 'downlink_frequency_range': (462.5, 467.5),
           'channel_bandwidths': [1.4, 3, 5]},
    1500: {'band_number': 32, 'application': 'SDL', 'name': 'L-Band (EU)', 'duplex_mode': 'SDL',
           'downlink_frequency_range': (1452, 1496),
           'channel_bandwidths': [5, 10, 15, 20]},
    2000: {'band_number': 34, 'application': 'TDD', 'name': 'IMT', 'duplex_mode': 'TDD',
           'uplink_frequency_range': (2010, 2025),
           'channel_bandwidths': [5, 10, 15]},
    1900: {'band_number': 37, 'application': 'TDD', 'name': 'PCS', 'duplex_mode': 'TDD',
           'uplink_frequency_range': (1910, 1930),
           'channel_bandwidths': [5, 10, 15, 20]},
    2600: {'band_number': 38, 'application': 'TDD', 'name': 'IMT-E', 'duplex_mode': 'TDD',
           'uplink_frequency_range': (2570, 2620),
           'channel_bandwidths': [5, 10, 15, 20]},
    1900: {'band_number': 39, 'application': 'TDD', 'name': 'DCS-IMT Gap', 'duplex_mode': 'TDD',
           'uplink_frequency_range': (1880, 1920),
           'channel_bandwidths': [5, 10, 15, 20]},
    2300: {'band_number': 40, 'application': 'TDD', 'name': 'S-Band', 'duplex_mode': 'TDD',
           'uplink_frequency_range': (2300, 2400),
           'channel_bandwidths': [5, 10, 15, 20]},
    2500: {'band_number': 41, 'application': 'TDD', 'name': 'BRS (US)', 'duplex_mode': 'TDD',
           'uplink_frequency_range': (2496, 2690),
           'channel_bandwidths': [5, 10, 15, 20]},
    3500: {'band_number': 42, 'application': 'TDD', 'name': 'CBRS (EU, Japan)', 'duplex_mode': 'TDD',
           'uplink_frequency_range': (3400, 3600),
           'channel_bandwidths': [5, 10, 15, 20]},
    3700: {'band_number': 43, 'application': 'TDD', 'name': 'C-Band', 'duplex_mode': 'TDD',
           'uplink_frequency_range': (3600, 3800),
           'channel_bandwidths': [5, 10, 15, 20]},
    5200: {'band_number': 46, 'application': 'TDD', 'name': 'U-NII-1-4', 'duplex_mode': 'TDD',
           'uplink_frequency_range': (5150, 5925),
           'channel_bandwidths': [10, 20]},
    5900: {'band_number': 47, 'application': 'TDD', 'name': 'U-NII-4', 'duplex_mode': 'TDD',
           'uplink_frequency_range': (5855, 5925),
           'channel_bandwidths': [10, 20]},
    3500: {'band_number': 48, 'application': 'TDD', 'name': 'CBRS (US)', 'duplex_mode': 'TDD',
           'uplink_frequency_range': (3550, 3700),
           'channel_bandwidths': [5, 10, 15, 20]},
    1500: {'band_number': 50, 'application': 'TDD', 'name': 'L-Band (EU)', 'duplex_mode': 'TDD',
           'uplink_frequency_range': (1432, 1517),
           'channel_bandwidths': [3, 5, 10, 15, 20]},
    1500: {'band_number': 51, 'application': 'TDD', 'name': 'L-Band Extension (EU)', 'duplex_mode': 'TDD',
           'uplink_frequency_range': (1427, 1432),
           'channel_bandwidths': [3, 5]},
    2400: {'band_number': 53, 'application': 'TDD', 'name': 'S-Band', 'duplex_mode': 'TDD',
           'uplink_frequency_range': (2483.5, 2495),
           'channel_bandwidths': [1.4, 3, 5, 10]},
    1600: {'band_number': 54, 'application': 'TDD', 'name': 'L-Band', 'duplex_mode': 'TDD',
           'uplink_frequency_range': (1670, 1675),
           'channel_bandwidths': [1.4, 3, 5]},
    2100: {'band_number': 65, 'application': 'FDD', 'name': 'Extended IMT', 'duplex_mode': 'FDD',
           'uplink_frequency_range': (1920, 2010), 'downlink_frequency_range': (2110, 2200),
           'channel_bandwidths': [1.4, 3, 5, 10, 15, 20]},
    1700: {'band_number': 66, 'application': 'FDD', 'name': 'Extended AWS (AWS-1-3)', 'duplex_mode': 'FDD',
           'uplink_frequency_range': (1710, 1780), 'downlink_frequency_range': (2110, 2200),
           'channel_bandwidths': [1.4, 3, 5, 10, 15, 20]},
    700: {'band_number': 67, 'application': 'SDL', 'name': 'EU 700', 'duplex_mode': 'SDL',
           'downlink_frequency_range': (738, 758),
           'channel_bandwidths': [5, 10, 15, 20]},
    2600: {'band_number': 69, 'application': 'SDL', 'name': 'IMT-E', 'duplex_mode': 'SDL',
           'downlink_frequency_range': (2570, 2620),
           'channel_bandwidths': [5, 10, 15, 20]},
    1700: {'band_number': 70, 'application': 'FDD', 'name': 'Supplementary AWS (AWS-2-4)', 'duplex_mode': 'FDD',
           'uplink_frequency_range': (1695, 1710), 'downlink_frequency_range': (1995, 2020),
           'channel_bandwidths': [5, 10, 15, 20]},
    600: {'band_number': 71, 'application': 'FDD', 'name': 'Digital Dividend (US)', 'duplex_mode': 'FDD',
           'uplink_frequency_range': (663, 698), 'downlink_frequency_range': (617, 652),
           'channel_bandwidths': [5, 10, 15, 20]},
    450: {'band_number': 72, 'application': 'FDD', 'name': 'PMR (EU)', 'duplex_mode': 'FDD',
           'uplink_frequency_range': (451, 456), 'downlink_frequency_range': (461, 466),
           'channel_bandwidths': [1.4, 3, 5]},
    450: {'band_number': 73, 'application': 'FDD', 'name': 'PMR (APT)', 'duplex_mode': 'FDD',
           'uplink_frequency_range': (450, 455), 'downlink_frequency_range': (460, 465),
           'channel_bandwidths': [1.4, 3, 5]},
    1500: {'band_number': 74, 'application': 'FDD', 'name': 'Lower L-Band (US)', 'duplex_mode': 'FDD',
           'uplink_frequency_range': (1427, 1470), 'downlink_frequency_range': (1475, 1518),
           'channel_bandwidths': [1.4, 3, 5, 10, 15, 20]},
    1500: {'band_number': 75, 'application': 'SDL', 'name': 'L-Band (EU)', 'duplex_mode': 'SDL',
           'downlink_frequency_range': (1432, 1517),
           'channel_bandwidths': [5, 10, 15, 20]},
    1500: {'band_number': 76, 'application': 'SDL', 'name': 'L-Band Extension (EU)', 'duplex_mode': 'SDL',
           'downlink_frequency_range': (1427, 1432),
           'channel_bandwidths': [5]},
    700: {'band_number': 85, 'application': 'FDD', 'name': 'Extended Lower SMH', 'duplex_mode': 'FDD',
           'uplink_frequency_range': (698, 716), 'downlink_frequency_range': (728, 746),
           'channel_bandwidths': [5, 10]},
    410: {'band_number': 87, 'application': 'FDD', 'name': 'PMR (APT)', 'duplex_mode': 'FDD',
           'uplink_frequency_range': (410, 415), 'downlink_frequency_range': (420, 425),
           'channel_bandwidths': [1.4, 3, 5]},
    410: {'band_number': 88, 'application': 'FDD', 'name': 'PMR (EU)', 'duplex_mode': 'FDD',
           'uplink_frequency_range': (412, 417), 'downlink_frequency_range': (422, 427),
           'channel_bandwidths': [1.4, 3, 5]},
    700: {'band_number': 103, 'application': 'FDD', 'name': 'Upper SMH', 'duplex_mode': 'FDD',
           'uplink_frequency_range': (787, 788), 'downlink_frequency_range': (757, 758),
           'channel_bandwidths': []},
    900: {'band_number': 106, 'application': 'FDD', 'name': 'LMR (US)', 'duplex_mode': 'FDD',
           'uplink_frequency_range': (896, 901), 'downlink_frequency_range': (935, 940),
           'channel_bandwidths': [1.4, 3]},
    600: {'band_number': 107, 'application': 'SDO', 'name': 'UHF', 'duplex_mode': 'SDO',
           'downlink_frequency_range': (612, 652),
           'channel_bandwidths': [6, 7, 8]},
    500: {'band_number': 108, 'application': 'SDO', 'name': 'UHF', 'duplex_mode': 'SDO',
           'downlink_frequency_range': (470, 698),
           'channel_bandwidths': [6, 7, 8]}
}

# Create folder for raw data capture
raw_data_path = f'Raw_Data/Scan-{datetime.datetime.now().strftime("%Y%m%d-%H%M")}'
if not os.path.exists(raw_data_path):
    os.makedirs(raw_data_path)
    
# Create Name for the CSV
file_name = f'Scan-{datetime.datetime.now().strftime("%Y%m%d-%H%M")}.csv'

# Check if an CSV file already exists with the same name, if yes, then add a number to the new file
if os.path.exists(file_name):
    new_file_name = f'{file_name}'
    i = 1
    while os.path.exists(new_file_name):
       new_file_name = f'{file_name}-{i}'
       i += 1
    
with open(file_name, 'w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(['Timestamp', 'Expected Protocol', 'Signal Strength (dB)', 'Scan Start Frequency (MHz)', 'Scan End Frequency (MHz)', 'Signal Start Frequency (MHz)', 'Signal End Frequency (MHz)', 'Bandwidth (MHz)', 'Application', 'Channel Number', 'Type'])
    
class Analyser(gr.sync_block):
    def __init__(self, sample_rate, threshold, current_frequency = None):
        gr.sync_block.__init__(
            self,
            name="Signal Analyser",
            in_sig=[np.complex64],
            out_sig=None)
        
        self.sample_rate = sample_rate
        self.frequency = current_frequency
        self.threshold = threshold
        self.protocol = None
        
    def save_to_csv(self, data):
        with open(file_name, 'a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(data)
        
    def set_frequency(self, current_frequency):
        self.frequency = current_frequency        
        
    def set_protocol(self, protocol):
        self.protocol = protocol
        
    def save_raw_data(self, raw_data, signal_info):
        # Generate a unique file name based on signal info or timestamp
        timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S%f")
        file_name = f"raw_data_{timestamp}_{signal_info}.npy"
        file_path = f"{raw_data_path}/{file_name}"
        # Save the raw data as a NumPy binary file
        np.save(file_path, raw_data)

    def work(self, input_items, output_items):
        protocol = self.protocol

        in0 = input_items[0]
        # Calculate the FFT of the input signal
        fft_data = np.fft.fftshift(np.fft.fft(in0))
        freqs = np.fft.fftshift(np.fft.fftfreq(len(fft_data), 1/self.sample_rate))

        # Calculate signal strength
        strength = 20 * np.log10(np.abs(np.mean(in0)))

        if strength > self.threshold:
            # Calculate the Power Spectral Density (PSD)
            psd = np.abs(fft_data) ** 2
            threshold = np.mean(psd) * 2
            signal_indices = np.where(psd > threshold)[0]

            if len(signal_indices) > 0:
                signal_identified = False
                save_signal = True

                start_freq = np.min(freqs[signal_indices])
                end_freq = np.max(freqs[signal_indices])
                signal_bandwidth = end_freq - start_freq

                real_start_freq = self.frequency + start_freq
                real_end_freq = self.frequency + end_freq
                real_middle_frequency = (real_start_freq + real_end_freq) / 2

                real_start_freq_mhz = real_start_freq / 1e6
                real_end_freq_mhz = real_end_freq / 1e6
                middle_frequency_mhz = real_middle_frequency / 1e6  # Convert to MHz
                signal_bandwidth_mhz = signal_bandwidth / 1e6  # Convert to MHz
                
                if signal_bandwidth_mhz < 0.01:
                       signal_identified = True
                       save_signal = False

                # Check the protocol type
                if protocol == 'Bluetooth':
                    for freq, info in bluetooth_channels.items():
                        if 0.1 < signal_bandwidth_mhz < 1.8 and abs(middle_frequency_mhz - freq) < 0.4:
                            bt_channel, bt_application = info["channel_number"], info["application"]
                            
                            self.save_to_csv([datetime.datetime.now(), 
                                              self.protocol, 
                                              strength, 
                                              self.frequency - 1/2*self.sample_rate, 
                                              self.frequency + 1/2*self.sample_rate, 
                                              real_start_freq / 1e6, 
                                              real_end_freq / 1e6, 
                                              signal_bandwidth_mhz, 
                                              'Bluetooth', 
                                              bt_channel, 
                                              bt_application])
                            
                            signal_identified = True
                            break

                elif protocol == 'Wi-Fi':
                    for freq, info in wifi_channels.items():
                        if 0.1 < signal_bandwidth_mhz < 20 and abs(middle_frequency_mhz - freq) < 2.5:
                            wifi_channel, wifi_application = info["channel_number"], info["application"]
                            
                            self.save_to_csv([datetime.datetime.now(), 
                                              self.protocol, 
                                              strength, 
                                              self.frequency - 1/2*self.sample_rate, 
                                              self.frequency + 1/2*self.sample_rate, 
                                              real_start_freq / 1e6, 
                                              real_end_freq / 1e6, 
                                              signal_bandwidth_mhz, 
                                              'Wi-Fi', 
                                              wifi_channel, 
                                              wifi_application])
                            
                            signal_identified = True
                            break

                elif protocol == 'LTE':
                    for freq, info in lte_bands.items():
                        for key in ['uplink_frequency_range', 'downlink_frequency_range']:
                            if key in info:
                                lower_frequency, upper_frequency = info[key]
                                
                                # Check if the signal falls within LTE frequency range
                                if abs(lower_frequency - real_start_freq_mhz) < 5 and abs(upper_frequency - real_end_freq_mhz) < 5:
                                    # Check if the signal bandwidth matches any of the LTE channel bandwidths
                                    for bandwidth in info['channel_bandwidths']:
                                        if abs(signal_bandwidth_mhz - bandwidth) < bandwidth * 0.05:
                                            band_number, band_name, band_mode = info['band_number'], info['name'], key
                                            
                                            self.save_to_csv([datetime.datetime.now(), 
                                                              self.protocol, 
                                                              strength, 
                                                              self.frequency - 1/2*self.sample_rate, 
                                                              self.frequency + 1/2*self.sample_rate, 
                                                              real_start_freq / 1e6, 
                                                              real_end_freq / 1e6, 
                                                              signal_bandwidth_mhz, 
                                                              'LTE', 
                                                              band_number, 
                                                              f'{band_name} {band_mode}'])
                                            
                                            signal_identified = True
                                            break

                if not signal_identified:
                    self.save_to_csv([datetime.datetime.now(), 
                                      self.protocol, 
                                      strength, 
                                      self.frequency - 1/2*self.sample_rate, 
                                      self.frequency + 1/2*self.sample_rate, 
                                      real_start_freq / 1e6, 
                                      real_end_freq / 1e6, 
                                      signal_bandwidth_mhz, 
                                      'Unknown', 
                                      '', 
                                      ''])
                    
                if save_signal:
                     signal_info = f"{self.protocol}"
                     self.save_raw_data(in0, signal_info)
                     
            else:
                pass
                
        return len(in0)
    
class Scanner(gr.top_block):
    def __init__(self, sample_rate, threshold, gain = 40, lna_gain = None):
        gr.top_block.__init__(self)
        
        self.sample_rate = sample_rate

        # Configure the SDR source with initial parameters
        self.sdr_source = osmosdr.source()
        self.sdr_source.set_sample_rate(sample_rate)  # Set Sampling Rate
        self.sdr_source.set_gain(gain)  # Set Gain (Amplification of the signal)
        
        # If an LNA gain is specified, set it. This is specific to devices like the HackRF
        if lna_gain is not None:
            # This is a device-specific call, since 'LNA' and 'AMP' are only valid gain names for the HackRF One in osmosdr
            self.sdr_source.set_gain(lna_gain, 'LNA')
            self.sdr_source.set_gain(10, 'AMP')

        # DC Blocker and Squelch setup (filter DC signal and everything below threshold)
        self.dc_blocker = dc_blocker_cc(32, True)
        self.squelch = analog.simple_squelch_cc(threshold, 1)
        
        # Setup the Analyser
        self.analyser = Analyser(sample_rate, threshold)
        
        # Connect the source to the blocker and squelch
        self.connect(self.sdr_source, self.dc_blocker)
        self.connect(self.dc_blocker, self.squelch)

        # Connect the output (squelch) to the analyser
        self.connect(self.squelch, self.analyser)

    def set_freq(self, frequency):
        # Set the scanner frequency
        center_frequency = frequency + (self.sample_rate / 2)
        
        # print(f'Center Frequency: {center_frequency}')
        self.sdr_source.set_center_freq(center_frequency)
        
        # Set the analyser frequency
        self.analyser.set_frequency(center_frequency)
        
    def set_protocol(self, protocol):
        self.analyser.set_protocol(protocol)
        
    def update_sample_rate(self, sample_rate):
        self.sample_rate = sample_rate
        self.sdr_source.set_sample_rate(sample_rate)
        self.analyser.sample_rate = sample_rate

def scan_frequencies(frequency_dict, duration_per_step, threshold, device = None):   
    # Before starting the tqdm loop, calculate total_steps
    total_steps = 0
    for frequencies, protocol in frequency_dict.items():
        lower_frequency_mhz, upper_frequency_mhz = frequencies
        lower_frequency, upper_frequency = int(lower_frequency_mhz*1e6), int(upper_frequency_mhz*1e6)
    
        # Adjust the sample_rate calculation as per your logic
        frequency_bandwidth_mhz = abs(lower_frequency_mhz - upper_frequency_mhz)
        if frequency_bandwidth_mhz > maximum_bandwidth:
               sample_rate = int(maximum_bandwidth*1e6)
        else:
               sample_rate = int(frequency_bandwidth_mhz*1e6)
        
        # Calculate the number of frequency steps for this range
        frequency_steps = np.ceil((upper_frequency - lower_frequency) / sample_rate)
        total_steps += frequency_steps * duration_per_step

    if device == 'HackRF One':
        tb = Scanner(maximum_bandwidth*1e6, threshold, 40, 40)  # Initialize the scanner
    else:
        tb = Scanner(maximum_bandwidth*1e6, threshold)  # Initialize the scanner
    tb.start()

    try:
        with tqdm(total=total_steps, desc="Don't touch devices, Scanning", 
                  bar_format='{desc}: {percentage:3.0f}%|{bar}| [{elapsed}<{remaining}]') as pbar:
            for frequencies, protocol in frequency_dict.items():
                lower_frequency_mhz, upper_frequency_mhz = frequencies
                lower_frequency, upper_frequency = int(lower_frequency_mhz*1e6), int(upper_frequency_mhz*1e6)
                
                # Calculate sample rate based on the maximum bandwidth
                frequency_bandwidth_mhz = abs(lower_frequency_mhz - upper_frequency_mhz)
                if frequency_bandwidth_mhz > maximum_bandwidth:
                    sample_rate = int(maximum_bandwidth*1e6)  #Maximum bandwidth, multiple steps (time-devision multiplexing)
                else:
                    sample_rate = int(frequency_bandwidth_mhz*1e6)  # Convert to Hz
                    
                tb.update_sample_rate(sample_rate)
                tb.set_protocol(protocol)
                    
                for frequency in range(lower_frequency, upper_frequency, sample_rate):
                    # print(f"Scanning frequency: {frequency} Hz at sample rate: {sample_rate}")
                    tb.set_freq(frequency)
                    
                    for _ in range(int(duration_per_step)):
                        time.sleep(1)
                        pbar.update(1)  # Update progress bar
            
    finally:
        print("Scan Complete.")
        tb.stop()
        tb.wait()
 
if __name__ == '__main__':   
    duration_per_step = 30  # 30 seconds per frequency
    threshold = -90  # 90dB threshold

    dual_device_mode = False
    device = 'HackRF One'
    # device = 'BladeRF'
    
    if dual_device_mode:
       freq_min = 300
       freq_max = 3800
    else:
       freq_min = 0
       freq_max = 1e6

    scan_dict_bladerf = dict()
    scan_dict_hackrf = dict()
    
    # Get Bluetooth frequencies
    for frequency, data in bluetooth_channels.items():
       protocol = 'Bluetooth'
       lower_frequency, upper_frequency = data['frequency_range']
       if lower_frequency > freq_min and upper_frequency < freq_max:
              scan_dict_bladerf[(lower_frequency, upper_frequency)] = protocol
       else:
              scan_dict_hackrf[(lower_frequency, upper_frequency)] = protocol
    
    # Get Wi-Fi frequencies
    for frequency, data in wifi_channels.items():
       protocol = 'Wi-Fi'
       lower_frequency, upper_frequency = data['frequency_range']
       if lower_frequency > freq_min and upper_frequency < freq_max:
              scan_dict_bladerf[(lower_frequency, upper_frequency)] = protocol
       else:
              scan_dict_hackrf[(lower_frequency, upper_frequency)] = protocol
    
    # Get LTE frequencies
    for frequency, data in lte_bands.items():
       protocol = 'LTE'
       
       if 'downlink_frequency_range' in data:
           lower_frequency, upper_frequency = data['downlink_frequency_range']
           if lower_frequency > freq_min and upper_frequency < freq_max:
              scan_dict_bladerf[(lower_frequency, upper_frequency)] = protocol
           else:
              scan_dict_hackrf[(lower_frequency, upper_frequency)] = protocol
       
       if 'uplink_frequency_range' in data:
           lower_frequency, upper_frequency = data['uplink_frequency_range']
           if lower_frequency > freq_min and upper_frequency < freq_max:
              scan_dict_bladerf[(lower_frequency, upper_frequency)] = protocol
           else:
              scan_dict_hackrf[(lower_frequency, upper_frequency)] = protocol
              
    # Get NFC
    for frequency, data in nfc_bands.items():
           lower_frequency, upper_frequency = data['frequency_range']
           if lower_frequency > freq_min and upper_frequency < freq_max:
              scan_dict_bladerf[(lower_frequency, upper_frequency)] = protocol
           else:
              scan_dict_hackrf[(lower_frequency, upper_frequency)] = protocol
    
    if dual_device_mode:
       print(f'{len(scan_dict_bladerf)} measurements will be performed using the BladeRF')
       input('Please connect the BladeRF and press enter')
       
       maximum_bandwidth = 28 # Maximum bandwidth in MHz for the BladeRF
       detected_frequencies = scan_frequencies(scan_dict_bladerf, duration_per_step, threshold, 'BladeRF')
    
       print(f'{len(scan_dict_hackrf)} measurements will be performed using the HackRF One')
       input('Please connect the HackRF One and press enter')
       
       maximum_bandwidth = 10 # Maximum bandwidth in MHz for the HackRF One
       detected_frequencies = scan_frequencies(scan_dict_hackrf, duration_per_step, threshold, 'HackRF One')
       
    else:
       if device == 'HackRF One':
              maximum_bandwidth = 10
       elif device == 'BladeRF':
              maximum_bandwidth = 28
       else:
              maximum_bandwidth = 1
              print('Selected Device is not supported, scanning will continue but may take significantly longer.')
       
       detected_frequencies = scan_frequencies(scan_dict_bladerf, duration_per_step, threshold, device)