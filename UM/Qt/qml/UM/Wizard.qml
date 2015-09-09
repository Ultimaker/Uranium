// Copyright (c) 2015 Ultimaker B.V.
// Cura is released under the terms of the AGPLv3 or higher.

import QtQuick 2.2
import QtQuick.Controls 1.1
import QtQuick.Window 2.1
import QtQuick.Controls.Styles 1.1
import QtQuick.Layouts 1.1
import QtQml 2.2

import UM 1.1 as UM

UM.Dialog
{
    id: base

    property int currentPage: -1;
    property bool lastPage: currentPage == pagesModel.count - 1;
    property bool nextAvailable: false;

    property bool firstRun: false

    title: currentPage != -1 ? pagesModel.get(currentPage).title : ""

    signal nextClicked()
    signal backClicked()

    minimumWidth: UM.Theme.sizes.modal_window_minimum.width
    minimumHeight: UM.Theme.sizes.modal_window_minimum.height

    function appendPage(page, title)
    {
        pagesModel.append({"page": page, "title": title})
    }

    function insertPage(page, title, position)
    {
        pagesModel.insert(position, {"page": page, "title": title})
    }

    function removePage(index)
    {
        pagesModel.remove(index)
    }

    function getPageSource(index)
    {
        //returns the actual source of a page
        return pagesModel.get(index).page
    }

    function getPageCount()
    {
        return pagesModel.count;
    }

    Item
    {
        anchors.fill: parent;

        Rectangle
        {
            id: wizardProgress
            visible: pagesModel.count > 1 ? true : false
            width: visible ? UM.Theme.sizes.wizard_progress.width : 0;
            anchors.top: parent.top
            anchors.bottom: parent.bottom
            color: palette.light

            Component
            {
                id: wizardDelegate
                Item
                {
                    height: childrenRect.height
                    Button
                    {
                        id: progressButton
                        width: wizardProgress.width
                        text: title

                        property bool active: text == pagesModel.get(base.currentPage).title;

                        style: ButtonStyle
                        {
                            background: Rectangle
                            {
                                border.width: 0
                                color: "transparent"
                            }
                            label: Text
                            {
                                id: progressText
                                horizontalAlignment: Text.AlignHCenter
                                wrapMode: Text.Wrap
                                renderType: Text.NativeRendering
                                text: control.text
                                font.underline: control.active || control.hovered ? true : false
                                color: control.active ? palette.text : palette.mid
                            }
                        }
                        onClicked:
                        {
                            //console.log(title
                            for (var i = 0; i < pagesModel.count; i++)
                            {
                                if (pagesModel.get(i).title == title)
                                {
                                   base.currentPage = i
                                   break
                                }
                            }
                        }
                    }
                    Label
                    {
                        id: progressArrow
                        anchors.top: progressButton.bottom
                        x: (wizardProgress.width-progressArrow.width)/2
                        text: "▼"
                        visible: title != pagesModel.get(pagesModel.count - 1).title ? true : false
                        color: palette.mid
                    }
                }
            }
            ListView
            {
                model: ListModel { id: pagesModel; }
                delegate: wizardDelegate

                anchors.fill: parent
                anchors.topMargin: UM.Theme.sizes.default_margin.height
            }
        }

        Loader
        {
            id: pageLoader

            anchors {
                top: parent.top
                bottom: parent.bottom;
                left: wizardProgress.right;
                leftMargin: UM.Theme.sizes.default_margin.width;
                right: parent.right;
            }

            width: parent.width - wizardProgress.width - (2 *  UM.Theme.sizes.default_margin.width)
            source: pagesModel.get(base.currentPage).page;

            Binding {
                target: pageLoader.item;
                property: "wizard";
                value: base;
            }
        }

        Connections
        {
            target: pageLoader.item
            ignoreUnknownSignals: true
            onReloadModel:
            {
                base.wizardModel = newModel
            }
        }

        SystemPalette{ id: palette }
        UM.I18nCatalog { id: catalog; name: "uranium"; }
    }

    rightButtons: [
        Button
        {
            id: backButton
            text: catalog.i18nc("@action:button", "Back");
            iconName: "go-previous";
            enabled: base.currentPage <= 0 ? false : true
            onClicked:
            {
                base.backClicked()

                if (base.currentPage > 0)
                {
                    base.currentPage -= 1
                }
            }
        },
        Button
        {
            id: nextButton
            text: base.lastPage && !base.nextAvailable ? catalog.i18nc("@action:button", "Finish") : catalog.i18nc("@action:button", "Next")
            iconName: base.lastPage && !base.nextAvailable ? "dialog-ok" : "go-next";

            onClicked: {
                base.nextClicked()

                if (!base.lastPage)
                {
                    base.currentPage += 1
                }
                else
                {
                    base.visible = false;
                }
            }
        },
        Button
        {
            id: cancelButton
            text: catalog.i18nc("@action:button", "Cancel")
            iconName: "dialog-cancel";
            onClicked:
            {
                base.visible = false;
                var old_page_count = getPageCount()
                // Delete old pages (if any)
                for (var i = old_page_count - 1; i > 0; i--)
                {
                    removePage(i)
                }
                currentPage = 0
            }
            visible: base.firstRun ? false : true
        }
    ]
}
