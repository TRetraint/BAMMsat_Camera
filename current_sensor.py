# SPDX-FileCopyrightText: 2021 ladyada for Adafruit Industries
# SPDX-License-Identifier: MIT


import time
import board
from adafruit_ina219 import ADCResolution, BusVoltageRange, INA219
import adafruit_ina260
from datetime import datetime
from time import sleep


i2c_bus = board.I2C()

ina219_battery = INA219(i2c_bus)
ina219_heat = INA219(i2c_bus,0x41)
ina260_raspberry = adafruit_ina260.INA260(i2c_bus,0x44)



# optional : change configuration to use 32 samples averaging for both bus voltage and shunt voltage
ina219_battery.bus_adc_resolution = ADCResolution.ADCRES_12BIT_32S
ina219_battery.shunt_adc_resolution = ADCResolution.ADCRES_12BIT_32S
# optional : change voltage range to 16V
ina219_battery.bus_voltage_range = BusVoltageRange.RANGE_16V


def get_curent_ina(ina):
    # measure and display loop
    bus_voltage = ina.bus_voltage  # voltage on V- (load side)
    shunt_voltage = ina.shunt_voltage  # voltage between V+ and V- across the shunt
    current = ina.current  # current in mA
    power = ina.power  # power in watts

    # INA219 measure bus voltage on the load side. So PSU voltage = bus_voltage + shunt_voltage
    print("Voltage (VIN+) : {:6.3f}   V".format(bus_voltage + shunt_voltage))
    print("Voltage (VIN-) : {:6.3f}   V".format(bus_voltage))
    print("Shunt Voltage  : {:8.5f} V".format(shunt_voltage))
    print("Shunt Current  : {:7.4f}  A".format(current / 1000))
    print("Power Calc.    : {:8.5f} W".format(bus_voltage * (current / 1000)))
    print("Power Register : {:6.3f}   W".format(power))
    print("")
    return [bus_voltage+ shunt_voltage,current/1000,power]

def get_current_260(ina):
    return [ina.voltage, ina.current, ina.power]


def save_current(filename):
    with open(filename,mode="a") as csv_file:
            csv_file.write("{0},{1},{2},{3},{4},{5},{6},{7},{8},{9}\n".format("Date","Tension Batterie","Intensite Batterie","Puissance Batterie","Tension Heat","Itensite Heat","Puissance Heat","Tension Rasp","Itensite Rasp","Puissance Rasp"))
            while True:
                current1 = get_curent_ina(ina219_battery)
                current2 = get_curent_ina(ina219_heat)
                current3 = get_current_260(ina260_raspberry)
                csv_file.write("{0},{1},{2},{3},{4},{5},{6},{7},{8},{9}\n".format(str(datetime.now()),str(current1[0]),str(current1[1]),str(current1[2]),str(current2[0]),str(current2[1]),str(current2[2]),str(current3[0]),str(current3[1]),str(current3[2])))
                csv_file.flush()
                sleep(2)

save_current('current.csv')
    
