add_custom_target( Settings1 SOURCES
    __init__.py
    MachineDefinition.py
    MachineInstance.py
    MachineManager.py
    MachineSettings.py
    Profile.py
    ProfileOverrideDecorator.py
    ProfileReader.py
    ProfileWriter.py
    Setting.py
    SettingOverrideDecorator.py
    SettingsCategory.py
    SettingsError.py
)

subdirs( Validators )
