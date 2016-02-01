add_custom_target( UM1 SOURCES
    ApplicationMenu.qml
    Dialog.qml
    #FilePanel.qml
    MessageStack.qml
    qmldir
    RecolorImage.qml
    TooltipArea.qml
    Wizard.qml
)

subdirs( Preferences )
subdirs( Settings )
