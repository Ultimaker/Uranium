import QtQuick 2.12
import QtQuick.Controls 2.12

import UM 1.5 as UM

Menu
{
    id: root

    // This is a work around for menu's not actually being visual items. Upon creation, a visual item is created
    // The work around is based on the suggestion given in https://stackoverflow.com/questions/59167352/qml-how-to-hide-submenu
    property bool shouldBeVisible: true
    onParentChanged: handleVisibility()
    function handleVisibility()
    {
        if(parent)
        {
            root.parent.visible = shouldBeVisible
            root.parent.height = shouldBeVisible ? UM.Theme.getSize("menu").height : 0
        }
    }

    // Automatically set the width to fit the widest MenuItem
    // https://martin.rpdev.net/2018/03/13/qt-quick-controls-2-automatically-set-the-width-of-menus.html
    width:
    {
        var result = 0;
        var padding = 0;
        for (var i = 0; i < count; ++i) {
            var item = itemAt(i);
            result = Math.max(item.contentItem.implicitWidth, result);
            padding = Math.max(item.padding, padding);
        }
        return result + padding * 2;
    }

    Component.onCompleted: handleVisibility()
    onShouldBeVisibleChanged: handleVisibility()
}