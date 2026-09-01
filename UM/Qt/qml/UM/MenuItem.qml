import QtQuick 2.12
import QtQuick.Layouts 1.12
import QtQuick.Controls 2.12
import UM 1.5 as UM

MenuItem
{
    id: root

    property bool indicatorVisible: root.icon.source.length > 0 || root.checkable
    height: visible ? UM.Theme.getSize("context_menu").height : 0
    property int contentWidth:
    {
        // This is the width of all the items in the contentItem except the filler
        return leftSpacer.width + label.width + middleSpacer.width + shortcutLabel.width + rightSpacer.width
    }

    Shortcut
    {
        // This objects exists only to get the shortcut native text, it is always disabled
        id: dummyShortcut
        enabled: false
        sequences: root.action !== null ? [root.action.shortcut] : []
    }

    function replaceText(txt)
    {
        var index = txt.indexOf("&")
        if(index >= 0)
        {
            txt = txt.replace(txt.substr(index, 2), "<u>" + txt.substr(index + 1, 1) + "</u>")
        }
        return txt
    }

    arrow: Image
    {
        source: UM.Theme.getIcon("ChevronSingleRight")
    }

    contentItem: RowLayout
    {
        spacing: 0
        opacity: root.enabled ? 1 : 0.5

        Item
        {
            // Left side margin
            id: leftSpacer
            width: root.indicatorVisible ? root.indicator.width + UM.Theme.getSize("default_margin").width : UM.Theme.getSize("default_margin").width
        }

        UM.Label
        {
            id: label
            text: replaceText(root.text)
            Layout.fillHeight:true
            elide: Label.ElideRight
            wrapMode: Text.NoWrap
        }

        Item
        {
            Layout.fillWidth: true
        }

        Item
        {
            // Middle margin
            id: middleSpacer
            width: (dummyShortcut.nativeText !== "" || root.subMenu) ? UM.Theme.getSize("default_margin").width : 0
        }

        UM.Label
        {
            id: shortcutLabel
            Layout.fillHeight: true
            text: dummyShortcut.nativeText
            color: UM.Theme.getColor("text_lighter")
        }

        Item
        {
            // Right side margin
            id: rightSpacer
            width: UM.Theme.getSize("default_margin").width
        }
    }
}
