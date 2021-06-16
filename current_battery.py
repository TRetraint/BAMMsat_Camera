# SPDX-FileCopyrightText: 2021 ladyada for Adafruit Industries
# SPDX-License-Identifier: MIT
"""
import time
import board
import adafruit_ina260
from time import sleep

i2c = board.I2C()
ina260 = adafruit_ina260.INA260(i2c,0x44)
def get_current_battery():
    print("Current: %.2f mA Voltage: %.2f V Power:%.2f mW"% (ina260.current, ina260.voltage, ina260.power))
    sleep(2)
    return [ina260.voltage, ina260.current, ina260.power]
    

while True:
    get_current_battery()
"""
# SPDX-FileCopyrightText: 2021 ladyada for Adafruit Industries
# SPDX-License-Identifier: MIT

import time
import board
import adafruit_ina260

i2c = board.I2C()
ina260 = adafruit_ina260.INA260(i2c)
while True:
    print(
        "Current: %.2f mA Voltage: %.2f V Power:%.2f mW"
        % (ina260.current, ina260.voltage, ina260.power)
    )
    time.sleep(1)



