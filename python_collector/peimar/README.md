**r** = ***call response "Get Inverter device status info"***  
**cf** = ***floating comma for r values (divider = 10 raised to the cf power)***

Mapping table between r and cf values (the values of r are examples):

| idx | r value | r description | cf | divider |
| :--- | :--- | :--- | :--- | :--- |
| 0  | 1 | (not used) | 0 | 10^0 |	
| 1  | 5077	| Total generated (KWh) | 2 | 10^2 |
| 2  | 488 | Total Running Time (h)	| 1 | 10^1 |
| 3  | 1890 | Today generated (KWh)	| 2 | 10^2 |
| 4  | 106 | Today Running Time (h)	| 1 | 10^1 |
| 5  | 3124	| DC Input - PV1 Voltage (V) | 1 | 10^1 |
| 6  | 502 | DC Input - PV1 Current (A)	| 2 | 10^2 |
| 7  | 0 | DC Input - PV2 Voltage (V) | 1 | 10^1 |
| 8  | 65535 | DC Input - PV2 Current (A)	[65535 = N/A] | 2 | 10^2 |
| 9  | 65535 | DC Input - PV3 Voltage (V)	[65535 = N/A] | 1 | 10^1 |
| 10 | 65535 | DC Input - PV3 Current (A)	[65535 = N/A] | 2 | 10^2 |
| 11 | 0 | DC Input - PV1 StrCurr1 (not used) | 2 | 10^2 |
| 12 | 0 | DC Input - PV1 StrCurr2 (not used) | 2 | 10^2 |
| 13 | 0 | DC Input - PV1 StrCurr3 (not used) | 2 | 10^2 |
| 14 | 0 | DC Input - PV1 StrCurr4 (not used) | 2 | 10^2 |
| 15 | 0 | DC Input - PV2 StrCurr1 (not used) | 2 | 10^2 |
| 16 | 0 | DC Input - PV2 StrCurr2 (not used) | 2 | 10^2 |
| 17 | 0 | DC Input - PV2 StrCurr3 (not used) | 2 | 10^2 |
| 18 | 0 | DC Input - PV2 StrCurr4 (not used) | 2 | 10^2 |
| 19 | 0 | DC Input - PV3 StrCurr1 (not used) | 2 | 10^2 |
| 20 | 0 | DC Input - PV3 StrCurr2 (not used) | 2 | 10^2 |
| 21 | 0 | DC Input - PV3 StrCurr3 (not used) | 2 | 10^2 |
| 22 | 0 | DC Input - PV3 StrCurr4 (not used) | 2 | 10^2 |
| 23 | 1498	| AC Output - Grid-connected Power (W) | 0 | 10^0 |
| 24 | 5006	| AC Output - Grid-connected Frequency (Hz) | 2 | 10^2 |
| 25 | 2343	| Line1 Voltage (V) | 1 | 10^1 |
| 26 | 640 | Line1 Current (A) | 2 | 10^2 |
| 27 | 65535 | Line2 Voltage (V)	[65535 = N/A] | 1 | 10^1 |
| 28 | 65535 | Line2 Current (A)	[65535 = N/A] | 2 | 10^2 |
| 29 | 65535 | Line3 Voltage (V)	[65535 = N/A] | 1 | 10^1 |
| 30 | 65535 | Line3 Current (A)	[65535 = N/A] | 2 | 10^2 |
| 31 | 3686	| Bus Voltage (V) | 1 | 10^1 |
| 32 | 514 | Device Temperature (°C) | 1 | 10^1 |
| 33 | 398 | CO2 emission reduction (Kg) | 1 | 10^1 |
| 34 | 2 | Running State (1 = Waiting, 2 = Normal, 3 = Error) | | |


