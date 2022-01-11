import QtQuick 2.12
import QtQuick.Controls 2.12

import UM 1.5 as UM

Menu
{
    id: root

    // This is a work around for menu's not actually being visual items. Upon creation, a visual item is created
    // The work around is based on the suggestion given in https://stackoverflow.com/questions/59167352/qml-how-to-hide-submenu
    property bool shouldBeVisible: true
    onParentChanged:  handleVisibility()
    function handleVisibility()
    {
        if(parent)
        {
            root.parent.visible = shouldBeVisible
            root.parent.height = shouldBeVisible ? UM.Theme.getSize("setting_control").height + UM.Theme.getSize("narrow_margin").height: 0
        }
    }
    Component.onCompleted: handleVisibility()
    onShouldBeVisibleChanged: handleVisibility()
}