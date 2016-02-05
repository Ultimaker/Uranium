add_custom_target( Qt1 SOURCES
    __init__.py
    Duration.py
    ListModel.py
    QtApplication.py
    QtKeyDevice.py
    QtMouseDevice.py
    QtRenderer.py
)

subdirs( Bindings )
subdirs( GL )
subdirs( qml )
