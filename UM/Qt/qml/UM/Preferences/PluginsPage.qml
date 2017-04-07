// Copyright (c) 2015 Ultimaker B.V.
// Uranium is released under the terms of the AGPLv3 or higher.

import QtQuick 2.1
import QtQuick.Controls 1.1
import QtQuick.Window 2.1
import QtQuick.Controls.Styles 1.1
import QtQuick.Dialogs 1.2

import UM 1.0 as UM

import ".."

PreferencesPage
{
    id: preferencesPage

    resetEnabled: false;

    title: catalog.i18nc("@title:tab", "Plugins");
    contents: Item
    {
        anchors.fill: parent
        Button
        {
            id: installButton
            onClicked: openDialog.open()
            text: catalog.i18nc("@action:button", "Install new plugin")

        }
        ScrollView
        {
            anchors
            {
                left: parent.left
                right: parent.right
                top: installButton.bottom
                bottom: pluginsNote.top
            }
            frameVisible: true
            ListView
            {
                id:pluginList
                delegate: pluginDelegate
                model: UM.PluginsModel { }
                section.delegate: Label { text: section }
                section.property: "type"
                anchors.fill:parent
            }
        }
        Label
        {
            id: pluginsNote

            text: catalog.i18nc("@label", "You will need to restart the application before changes in plugins have effect.")
            wrapMode: Text.WordWrap
            font.italic: true

            anchors.bottom: parent.bottom
        }
    }
    Item
    {
        SystemPalette { id: palette }

        Component
        {
            id: pluginDelegate
            Rectangle
            {
                width: pluginList.width;
                height: childrenRect.height;
                color: index % 2 ? palette.base : palette.alternateBase

                CheckBox
                {
                    id: pluginCheckbox
                    checked: model.enabled
                    onClicked: pluginList.model.setEnabled(model.id, checked)
                    enabled: !model.required
                    anchors.verticalCenter: pluginText.verticalCenter
                    x: y
                }
                Button
                {
                    id: pluginText //is a button so the user doesn't have te click inconvenientley precise to enable or disable the checkbox
                    text: model.name
                    onClicked:
                    {
                        pluginCheckbox.checked = !pluginCheckbox.checked;
                        pluginCheckbox.clicked();
                    }
                    tooltip: model.description + (model.required ? ("\n" + catalog.i18nc("@label", "This plugin is required for the application to run.")) : "")
                    anchors.left: pluginCheckbox.visible ? pluginCheckbox.right : parent.left
                    anchors.right: pluginIcon.left
                    style: ButtonStyle
                    {
                        background: Item {}
                        label: Label
                        {
                            renderType: Text.NativeRendering
                            horizontalAlignment: Text.AlignLeft
                            text: control.text
                        }
                    }
                }
                Button
                {
                    id: pluginIcon
                    text: catalog.i18nc("@label", "Info...")
                    anchors.right: parent.right
                    iconName: "help-about"
                    onClicked:
                    {
                        about_window.about_text = model.description
                        about_window.author_text = model.author
                        about_window.plugin_name = model.name
                        about_window.version_text = model.version
                        about_window.visibility = 1
                    }
                }
            }
        }

        MessageDialog
        {
            id: messageDialog
            title: catalog.i18nc("@window:title", "Install Plugin");
            standardButtons: StandardButton.Ok
            modality: Qt.ApplicationModal
        }

        FileDialog
        {
            id: openDialog;

            title: catalog.i18nc("@title:window", "Open file(s)")
            modality: UM.Application.platform == "linux" ? Qt.NonModal : Qt.WindowModal;
            nameFilters: PluginRegistry.supportedPluginExtensions
            onAccepted:
            {
                var result = PluginRegistry.installPlugin(fileUrl)

                messageDialog.text = result.message
                if(result.status == "ok")
                {
                    messageDialog.icon = StandardIcon.Information
                }
                else if(result.status == "duplicate")
                {
                    messageDialog.icon = StandardIcon.Warning
                }
                else
                {
                    messageDialog.icon = StandardIcon.Critical
                }
                messageDialog.open()

            }
            onRejected:
            {
                console.log("Canceled")
            }
        }

        Dialog
        {
            id: about_window

            //: Default description for plugin
            property variant about_text: catalog.i18nc("@label", "No text available")

            property variant author_text: "John doe"
            property variant plugin_name: ""
            property variant version_text: ""

            title: catalog.i18nc("@title:window", "About %1").arg(plugin_name)

            minimumWidth: Screen.devicePixelRatio * 320
            minimumHeight: Screen.devicePixelRatio * 240
            width: minimumWidth
            height: minimumHeight

            Label
            {
                id: pluginTitle
                text: about_window.plugin_name
                font.pointSize: 18
                width: parent.width
                wrapMode: Text.WordWrap
            }

            Label
            {
                id: pluginCaption
                text: about_window.about_text
                height: about_window.about_text ? undefined : 0 //if there is no pluginCaption the row height is 0 for layout purposes
                width: parent.width
                wrapMode: Text.WordWrap
                font.italic: true
                anchors.top: pluginTitle.bottom
                anchors.topMargin: about_window.about_text ? 3 : 0 //if there is no pluginCaption the topMargin is 0 for layout purposes
            }

            Label
            {
                id: pluginAuthorLabel
                //: About plugin dialog author label
                text: catalog.i18nc("@label", "Author:");
                width: 0.4 * parent.width
                wrapMode: Text.WordWrap
                anchors.top: pluginCaption.bottom
                anchors.topMargin: 10
            }

            Label
            {
                id: pluginAuthor;
                text: about_window.author_text
                width: 0.6 * parent.width
                wrapMode: Text.WordWrap
                anchors.top: pluginCaption.bottom
                anchors.left: pluginAuthorLabel.right
                anchors.topMargin: 10
            }

            Label
            {
                id: pluginVersionLabel
                //: About plugin dialog version label
                text: catalog.i18nc("@label", "Version:");
                width: 0.4 * parent.width
                wrapMode: Text.WordWrap
                anchors.top: pluginAuthor.bottom
            }

            Label
            {
                id: pluginVersion
                text: about_window.version_text
                width: 0.6*parent.width
                anchors.top: pluginAuthor.bottom
                anchors.left: pluginVersionLabel.right
            }

            rightButtons: Button
            {
                //: Close "about plugin" dialog button
                text: catalog.i18nc("@action:button", "Close");
                onClicked: about_window.visible = false;
            }
        }
    }
}
