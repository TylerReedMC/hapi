#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
HAPI Asset Interface - v1.0
Release: May 2017, Beta Milestone
Copyright 2016 Maya Culpa, LLC

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''
#https://github.com/switchdoclabs/RTC_SDL_DS3231/blob/master/SDL_DS3231.py

import SDL_DS3231
import sys
import datetime
import logging

SM_LOGGER = "smart_module"

TYPE_ADDRESS = 0
TYPE_LEN = 2
ID_ADDRESS = TYPE_ADDRESS + TYPE_LEN
ID_LEN = 16
CONTEXT_ADDRESS = ID_ADDRESS + ID_LEN
CONTEXT_LEN = 16

class RTCInterface(object):
    '''Interface for DS3231 Real-time Clock with internal temp sensor and AT24C32 EEPROM
    '''

    def __init__(self, mock=False):
        '''
        Args:
            mock (bool): Pass as True if a hardware RTC is not connected
        '''

        self.mock = mock
        self.logger = logging.getLogger(SM_LOGGER)

        if self.mock:
            return

        try:
            self.ds3231 = SDL_DS3231.SDL_DS3231(1, 0x68, 0x57)
        except Exception, excpt:
            self.logger.exception("Error initializing RTC. %s", excpt)

    def get_datetime(self):
        '''Gets the current date/time from the attached RTC
        Returns:
            datetime: Current date/time from RTC if mock is False. Current Python datetime if mock is True
        '''
        if self.mock:
            return datatime.datetime.now()

        try:
            return self.ds3231.read_datetime()
        except Exception, excpt:
            self.logger.exception("Error getting RTC date/time. %s", excpt)

    def set_datetime(self):
        '''Writes the system datetime to the attached RTC (mock is False)
        '''

        if self.mock:
            return

        try:
            self.ds3231.write_now()
        except Exception, excpt:
            self.logger.exception("Error writing date/time to RTC. %s", excpt)

    def get_temp(self):
        '''Gets the internal temperature from the RTC component
        Returns:
            float: Current RTC internal temperature sensor value if mock is False. 20.0 if mock is True
        '''

        if self.mock:
            return float(random.randrange(8, 34, 1))

        try:
            return self.ds3231.getTemp()
        except Exception, excpt:
            self.logger.exception("Error getting the temperature from the RTC. %s", excpt)

    def get_type(self):
        '''Gets the modules sensor type from the EEPROM
        Returns:
            str: 2-byte Type data as String if mock is False. "wt" if mock is True
        '''

        if self.mock:
            return "wt"

        try:
            byte0 = self.ds3231.read_AT24C32_byte(0)
            byte1 = self.ds3231.read_AT24C32_byte(1)
            return str(chr(byte0) + chr(byte1)).strip()
        except Exception, excpt:
            self.logger.exception("Error reading type from EEPROM. %s", excpt)

    def write_eeprom(self, s, address, length, name):
        '''Write length bytes of s to EEPROM
        starting at EEPROM address.
        s is padded with spaces if shorter than length.
        If exception, cites name.
        '''

        if self.mock:
            return

        s = s[:length]  # Trim to maximum length.
        s = s.ljust(length)  # Pad to correct length.
        for i, c in enumerate(s):
            try:
                self.ds3231.write_AT24C32_byte(address + i, ord(c))
            except Exception, excpt:
                self.logger.exception("Error writing %s to EEPROM. %s", name, excpt)
                return

    def set_type(self, type_):
        '''Writes the modules %s-byte sensor type to EEPROM
        Args:
            type_ (str): Sensor Type to write to EEPROM
        ''' % TYPE_LEN

        self.write_eeprom(type_, TYPE_ADDRESS, TYPE_LEN, 'Sensor Type')

    def get_id(self):
        '''Gets the Smart Module ID from the attached EEPROM
        Returns:
            str: 16-byte module ID if mock is False. "HSM-WT123-MOCK" if mock is True
        '''

        if self.mock:
            return "HSM-WT123-MOCK"

        try:
            #Concatenate the 16 byte module ID
            id_data = ""
            for x in range(ID_ADDRESS, ID_ADDRESS + ID_LEN):
                id_data = id_data + chr(self.ds3231.read_AT24C32_byte(x))
            return str(id_data).strip()
        except Exception, excpt:
            self.logger.exception("Error reading Module ID from EEPROM. %s", excpt)

    def set_id(self, id_):
        '''Writes the module id to EEPROM
        Args:
            id_ (str): The ID of the Smart Module to write to EEPROM      
        Returns:
            None
        '''

        self.write_eeprom(id_, ID_ADDRESS, ID_LEN, 'Module ID')

    def get_context(self):
        '''Gets the module context from the attached EEPROM
        Returns:
            str: 16-byte sensor context if mock is False. "Environment" if mock is True
        '''

        if self.mock:
            return "Environment"

        try:
            #Read the 16 byte asset context
            context = ""
            for x in range(CONTEXT_ADDRESS, CONTEXT_ADDRESS + CONTEXT_LEN):
                context = context + chr(self.ds3231.read_AT24C32_byte(x))
            return str(context).strip()
        except Exception, excpt:
            self.logger.exception("Error reading Module context from EEPROM. %s", excpt)

    def set_context(self, context):
        '''Writes the modules sensor context to the attached EEPROM
        Args:
            context (str): The context of the Smart Modules sensor (Water, Light, etc)
        Returns:
            None
        '''

        self.write_eeprom(context, CONTEXT_ADDRESS, CONTEXT_LEN, 'Module context')
