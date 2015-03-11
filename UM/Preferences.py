from UM.Signal import Signal, SignalEmitter
from UM.Logger import Logger

import os
import configparser

class Preferences(SignalEmitter):
    def __init__(self):
        super().__init__()

        self._preferences = {}
    
    def addPreference(self, key, default_value):
        preference = self._findPreference(key)
        if preference:
            Logger.log('w', 'Preference %s already exists', key)
            return

        group = 'general'
        key = key

        if '/' in key:
            parts = key.split('/')
            group = parts[0]
            key = parts[1]

        if group not in self._preferences:
            self._preferences[group] = {}

        self._preferences[group][key] = _Preference(key, default_value)

    def setValue(self, key, value):
        preference = self._findPreference(key)

        if preference:
            preference.setValue(value)
            self.preferenceChanged.emit(key)
    
    def getValue(self, key):
        preference = self._findPreference(key)

        if preference:
            return preference.getValue()

        return None

    def resetPreference(self, key):
        preference = self._findPreference(key)

        if preference:
            preference.setValue(preference.getDefault())
            self.preferenceChanged.emit(key)

    def readFromFile(self, file):
        parser = configparser.ConfigParser()
        parser.read(file)

        if parser['general']['version'] != 1:
            os.remove(file)
            return

        for group, group_entries in parser:
            if not group in self._preferences:
                Logger.log('w', "Unknown preference group %s", group)
                continue

            for key, value in group_entries:
                if not key in self._preferences[group]:
                    Logger.log('w', "Unknown preference %s", key)
                    continue

                self._preferences[group][key].setValue(value)

    def writeToFile(self, file):
        parser = configparser.ConfigParser()
        for group, group_entries in self._preferences.items():
            parser[group] = {}
            for key, pref in group_entries.items():
                if pref.getValue() != pref.getDefault():
                    parser[group][key] = pref.getValue()

        parser['general']['version'] = '1'

        with open(file, 'wt') as f:
            parser.write(f)

    preferenceChanged = Signal()

    @classmethod
    def getInstance(cls):
        if not cls._instance:
            cls._instance = Preferences()

        return cls._instance

    def _findPreference(self, key):
        group = 'general'
        key = key

        if '/' in key:
            parts = key.split('/')
            group = parts[0]
            key = parts[1]

        if group in self._preferences:
            if key in self._preferences[group]:
                return self._preferences[group][key]

        return None

    _instance = None

class _Preference:
    def __init__(self, name, default, value = None):
        self._name = name
        self._default = default
        self._value = default if value == None else value

    def getName(self):
        return self._name

    def getValue(self):
        return self._value

    def getDefault(self):
        return self._default

    def setValue(self, value):
        self._value = value
