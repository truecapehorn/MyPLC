#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pymodbus.client.sync import ModbusSerialClient as ModbusClient
from pymodbus.constants import Endian
from pymodbus.payload import BinaryPayloadDecoder
from pymodbus.payload import BinaryPayloadBuilder
from collections import OrderedDict
import time
import numpy as np


class Api():
    ''' Obsłoga Modbus RTU'''

    def __init__(self, method='rtu', port='', speed=0, stopbits=1, parity='N', bytesize=8, timeout=1):
        self.method = method
        self.port = port
        self.speed = speed
        self.stopbits = stopbits
        self.parity = parity
        self.bytesize = bytesize
        self.timeout = timeout

    def connection(self):
        client = ModbusClient(method=self.method, port=self.port, baudrate=self.speed, stopbits=self.stopbits,
                              parity=self.parity, bytesize=self.bytesize, timeout=self.timeout)

        print(
            "   Connection:\nmethod = {},\nport = {},\nbaudrate = {},\nstopbits = {},\nparity = {},\nbytesize = {},\ntimeout = {},\n".format(
                self.method,
                self.port,
                self.speed,
                self.stopbits,
                self.parity,
                self.bytesize,
                self.timeout))

        time.sleep(1)
        return client

    def read_holding(self, unit, reg_start, reg_lenght, data_type, qty=5):
        data = []
        client = self.connection()
        connection = client.connect()
        print("Odczyt adresow holding reg od {} do {} dla urzadzen {} predkosc {}: {}".format(reg_start,
                                                                                   reg_start + reg_lenght,
                                                                                   unit,self.speed,
                                                                                   connection))
        sesion = 1
        while connection and sesion <= qty:
            print("Sesja nr: ", sesion)
            time.sleep(0.3)
            for i in unit:
                try:
                    client.connect()
                    massure = client.read_holding_registers(reg_start, reg_lenght+1, unit=i)
                    if data_type == 'ui16':
                        data = massure.registers[0:]
                        print('Rejestry {} dla adresu {}'.format(data_type, i))
                        for c ,v in enumerate(data,0):
                            print('Adres: {} - {}'.format(c,v))
                    elif data_type == 'float':
                        massure.registers[0::2], massure.registers[1::2] = massure.registers[1::2], massure.registers[
                                                                                                    0::2]
                        data_arr = np.array([massure.registers[0:]], dtype=np.int16)
                        data_as_float = data_arr.view(dtype=np.float32)
                        data = data_as_float
                        print('Rejestry {} dla adresu {}'.format(data_type, i))
                        for c ,v in enumerate(data,0):
                            print('Adres: {} - {}'.format(c,v))
                    client.close()
                    time.sleep(0.3)
                except AttributeError:
                    print('Połaczenie z adresem {} nie udane'.format(i))
                    continue
                except KeyboardInterrupt:
                    print('Przerwanie przez urzytkownika')
                    client.close()
                    break
            client.close()

            sesion += 1
            print("\n")
        if len(data) != 0:
            return data
        else:
            print('Error:  Nie mozna polaczyc sie z adresem\n')
            exit()

    def read_input(self, unit, reg_start, reg_lenght, data_type, qty=5):
        data = []
        client = self.connection()
        connection = client.connect()
        if data_type == 'float':
            reg_lenght += 2
        print("Odczyt adresow holding reg od {} do {} dla urzadzen {} predkosc {}: {}".format(reg_start,
                                                                                   reg_start + reg_lenght,
                                                                                   unit,self.speed,
                                                                                   connection))
        sesion = 1
        while connection and sesion <= qty:
            print("Sesja nr: ", sesion)
            time.sleep(0.3)
            massure = []
            for i in unit:
                try:
                    client.connect()
                    massure = client.read_input_registers(reg_start, reg_lenght, unit=i)
                    data = massure.registers[0:]

                    if data_type == 'ui16':
                        print('Rejestry {} dla adresu {}'.format(data_type, i))
                        for c ,v in enumerate(data,0):
                            print(c,v)
                    elif data_type == 'float':
                        massure.registers[0::2], massure.registers[1::2] = massure.registers[1::2], massure.registers[
                                                                                                    0::2]
                        data_arr = np.array([massure.registers[0:]], dtype=np.int16)
                        data_as_float = data_arr.view(dtype=np.float32)
                        data = data_as_float
                        print('Rejestry {} dla adresu {}'.format(data_type, i))
                        for c ,v in enumerate(data,0):
                            print('Adres: {} - {}'.format(c,v))
                    client.close()
                except AttributeError:
                    print('Połaczenie z adresem {} nie udane'.format(i))
                    continue
                except KeyboardInterrupt:
                    print('Przerwanie przez urzytkownika')
                    client.close()
                    break

            sesion += 1
            print("\n")
        if len(data) != 0:
            return data
        else:
            print('Error:  Nie mozna polaczyc sie z adresem\n')
            exit()

    def write_register(self, reg_add, val, mod_adress):
        client = self.connection()
        connection = client.connect()
        try:
            time.sleep(0.3)
            client.write_register(reg_add, val, unit=mod_adress)
        except AttributeError:
            print('Połaczenie z adresem {} nie udane'.format(mod_adress))
            client.close()
        client.close()
        return print('Nowa wartosc zapisana')

    def appar_add_change(self,unitAdd ,valOld, valNew, data_type):
        unit = []
        unit.append(unitAdd)
        reg = self.read_holding(unit, 0, 30, data_type, 5)
        print('Stary adres = ', reg[28])
        if reg[28] == valOld:
            testVar = input("Czy chcesz zmienic adres z {} na {} ( t/n).".format(valOld, valNew))
            if testVar == "t" or testVar == 'T':
                print('Zmieniam adres z {} na {}'.format(valOld, valNew))
                self.write_register(28, valNew, valOld)
                time.sleep(0.5)
                unit = []
                print('Przeprowadzono zmiane adresu z {} na {}'.format(valOld, valNew))
                unit.append(valNew)
                self.read_holding(unit, 0, 30, data_type, 5)
        else:
            print('Error: Adres inny niz ', valOld)
        print('\n')

    def fif_add_change(self,unitAdd ,valOld, valNew, data_type):
        unit = []
        unit.append(unitAdd)
        reg = self.read_holding(unit, 256, 4, data_type, 5)
        print('Stary adres = ', reg[0])
        if reg[0] == valOld:
            testVar = input("Czy chcesz zmienic adres z {} na {} ( t/n).".format(valOld, valNew))
            if testVar == "t" or testVar == 'T':
                print('Zmieniam adres z {} na {}'.format(valOld, valNew))
                self.write_register(256, valNew, valOld)
                time.sleep(0.5)
                unit = []
                print('Przeprowadzono zmiane adresu z {} na {}'.format(valOld, valNew))
                unit.append(valNew)
                self.read_holding(unit, 256, 4, data_type, 5)
        else:
            print('Error: Adres inny niz ', valOld)
        print('\n')

    def appar_speed_change(self, unitAdd,valOld, valNew, data_type):
        unit = []
        unit.append(unitAdd)
        reg = self.read_holding(unit, 0, 30, data_type, 5)
        print('Stara predkosc = ', reg[29])
        if reg[29] == valOld:
            testVar = input("Czy chcesz zmienic predkosc z {} na {} ( t/n).".format(valOld, valNew))
            if testVar == "t" or testVar == 'T':
                print('Zmieniam predkosc z {} na {}'.format(valOld, valNew))
                self.write_register(29, valNew, unitAdd)
                time.sleep(0.5)
                unit = []
                print('Przeprowadzono zmiane predkosci z {} na {}'.format(valOld, valNew))
        else:
            print('Error: Predkosc inna niz ', valOld)
        print('\n')


if __name__ == '__main__':
    rtu = Api(port='com2', speed=2400)
    fifek = Api(speed=2400)
    print(Api.__doc__)
    unith = [2]
    uniti = [64]
    fif = [1]
    readholding = rtu.read_holding(unith, 0, 29, 'ui16', 10)

    # readinput1 = rtu.read_input(uniti, 0, 10, 'ui16', 5)
    # readinput2 = fifek.read_input(fif, 0, 70, 'float', 5)
    #writereg = rtu.appar_add_change(1,1, 11, 'ui16')
    #fifchenge = rtu.fif_add_change(11,11, 23, 'ui16')
    #speedchenge=rtu.appar_speed_change(1,9600,2400,'ui16')