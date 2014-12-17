class Preferences:
    _preference_list = {}
    
    def addPreference(key, default_value):
        if key not in Preferences._preference_list:
            Preferences._preference_list[key] = default_value
            
    def setPreference(key, value):
        if key in Preferences._preference_list:
            Preferences._preference_list[key] = value
    
    def getPreference(key):
        if key in Preferences._preference_list:
            return Preferences._preference_list[key]
        else:
            return None