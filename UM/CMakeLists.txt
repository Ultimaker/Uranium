add_custom_target( UM2 SOURCES
    __init__.py
    Application.py
    ColorGenerator.py
    Controller.py
    Event.py
    Extension.py
    i18n.py
    InputDevice.py
    Job.py
    JobQueue.py
    Logger.py
    Message.py
    Platform.py
    PluginError.py
    PluginObject.py
    PluginRegistry.py
    Preferences.py
    Resources.py
    SaveFile.py
    Signal.py
    SortedList.py
    Tool.py
    Version.py
    )

subdirs( Backend )
subdirs( Math )
subdirs( Mesh )
subdirs( Operations )
subdirs( OutputDevice )
subdirs( Qt )
subdirs( Scene )
subdirs( Settings )
subdirs( View )
