import QtQuick 2.2
import QtQuick.Controls 1.1
import QtQuick.Layouts 1.1
import QtQuick.Dialogs 1.1
import QtQuick.Window 2.1

import UM 1.0 as UM
UM.MainWindow 
{
    id: base
    visible: true

    width: 1280
    height: 768

    Item 
    {
        id: background_item;
        anchors.fill: parent;

        UM.ApplicationMenu 
        {
            id: menu
            window: base

            Menu 
            {
                title: '&File';

                MenuItem { action: load_file_action; }
                MenuItem { action: save_file_action; }

                MenuSeparator { }

                MenuItem { action: quit_action; }
            }

            Menu 
            {
                title: '&Edit';

                MenuItem { action: undo_action; }
                MenuItem { action: redo_action; }
                MenuSeparator { }
                MenuItem { action: delete_action; }
            }

            Menu 
            {
                title: "&Machine";

                MenuSeparator { }
                MenuItem{text: "UltiScanTastic"; enabled: false;}
            }

            Menu 
            {
                title: '&Settings';

                MenuItem { action: preferences_action; }
                MenuItem { action: plugin_action; }
                MenuItem { action: settings_action; }
            }

            Menu 
            {
                title: '&Help';

                MenuItem { action: helpAction; enabled: false; }
                MenuItem { action: aboutAction; enabled: false; }
            }
        }

        Item 
        {
            id: contentItem;

            y: menu.height
            width: parent.width;
            height: parent.height - menu.height;

            Keys.forwardTo: menu

            DropArea 
            {
                anchors.fill: parent

                onDropped: {
                    if(drop.urls.length > 0) 
                    {
                        for(var i in drop.urls) 
                        {
                            UM.Controller.addMesh(drop.urls[i]);
                        }
                    }
                }
            }
            
            Toolbar {
                id: toolbar;

                anchors {
                    left: parent.left;
                    right: parent.right;
                    top: parent.top;
                }

            }

            UM.MeshListPanel 
            {
                id: mesh_list_panel;
                anchors.topMargin:5
                anchors.leftMargin:5
                anchors.left: parent.left
                anchors.top:toolbar.bottom
            }

            //Setting / Wizard menu (HARDCODED for wizard stuff)
            Loader 
            {
                
                anchors.top:toolbar.bottom;
                anchors.topMargin:5;
                anchors.rightMargin:5;
                anchors.right:parent.right
                source: switch(UM.ToolbarData.wizardActive ? UM.ToolbarData.state: -1)
                {
                    case -1:
                        return "SettingsPane.qml" //Stetings pane
                    case 0:
                        return ""
                    case 1:
                        return "WizardSetup1.qml"
                    case 2:
                        return "WizardSetup2.qml"
                    case 3:
                        return "WizardSetup3.qml"
                    case 4:
                        return "WizardSetup4.qml"
                    case 5:
                        return "WizardSetup5.qml"
                    case 6:
                        return "WizardSetup6.qml"
                    case 7:
                        return "WizardSetup7.qml"
                    case 8:
                        return "WizardSetup8.qml"
                    case 9:
                        return "WizardSetup9.qml"
                    case 10:
                        return "WizardSetup10.qml"
                    case 11:
                        return "WizardSetup11.qml"
                    case 12:
                        return "WizardSetup12.qml"
                    case 13:
                        return "WizardSetup13.qml"
                }
            }


            /*UM.SettingsPanel 
            {
                anchors.right: parent.right;
                anchors.verticalCenter: parent.verticalCenter

                onSettingConfigurationRequested: 
                {
                    preferences.visible = true;
                    preferences.setPage(1);
                }
            }*/

            UM.JobList { anchors.left: parent.left; anchors.bottom: parent.bottom; width: parent.width / 10; height: parent.height / 5; }
        
            Image 
            { 
                source:UM.Resources.getIcon("poweredbyultimakersmall.png")
                anchors.bottom: parent.bottom;
                anchors.left:parent.left;
            } 
            
            /*ProgressBar 
            {
                id: progressBar;
                anchors.bottom:parent.bottom
                anchors.horizontalCenter:parent.horizontalCenter
                minimumValue: 0;
                maximumValue: 100;
                visible: (!UM.ToolbarData.wizardActive && UM.ToolbarData.state == 3 || UM.ToolbarData.state == 10)

                Connections 
                {
                    target: UM.Backend;
                    onProcessingProgress: progressBar.value = amount;
                }
            }*/
            
            Rectangle 
            {
                id: firstTimeStartup
                width: 750
                height: (!UM.ScannerEngineBackend.processing && UM.ToolbarData.state == 1 && !UM.ToolbarData.wizardActive) ? parent.height / 2 :0
                anchors.horizontalCenter:parent.horizontalCenter
                anchors.topMargin: 5
                anchors.top:toolbar.bottom
                border.width:1
                //visible: (!UM.ScannerEngineBackend.processing && UM.ToolbarData.state == 1 && !UM.ToolbarData.wizardActive) //Anything changes, user pressed a button so hide the wizard
                opacity: (!UM.ScannerEngineBackend.processing && UM.ToolbarData.state == 1 && !UM.ToolbarData.wizardActive) ? 1:0
                Behavior on opacity { NumberAnimation { } }
                Behavior on height {NumberAnimation {}}
                RowLayout
                {
                    //anchors.fill: parent;
                    width: parent.width - 2
                    height:parent.height 
                    anchors.horizontalCenter:parent.horizontalCenter
                    ColumnLayout 
                    {
                        Image
                        {
                            source:"placeholder.png"
                        }
                        WizardButton
                        {
                            text:"Start wizard"
                            onClicked:
                            {
                                UM.ToolbarData.setWizardState(true);
                                firstTimeStartup.opacity = 0;
                                firstTimeStartup.height = 0;
                            }
                        }
                    }
                    Text
                    {
                        id:introText
                        text: "<b>First time startup</b><br>Omg zomg wtf bbq! Proin eu felis ante. Curabitur blandit nibh eget feugiat aliquam. Duis neque erat, vehicula at tempus id, lobortis vitae turpis. Maecenas venenatis diam a ornare consectetur. Aenean ac nibh id orci dignissim sollicitudin id ac odio. Sed sem erat, hendrerit eu congue sit amet, euismod eget mi. Aliquam erat volutpat. "
                        wrapMode: Text.Wrap
                        Layout.fillWidth: true
                    }
                    ColumnLayout
                    {
                        Image
                        {
                            source:"placeholder.png"
                            
                        }
                        WizardButton
                        {
                            text:"Start advanced"
                            onClicked:
                            {
                                UM.ToolbarData.setWizardState(false);
                                firstTimeStartup.opacity = 0;
                                firstTimeStartup.height = 0;
                            }
                        }
                    }
                }
            }
            Image
            {
                width:640
                height:360
                id:cameraImage
                anchors.horizontalCenter: parent.horizontalCenter;
                y: 205
                anchors.topMargin:5
                source: UM.ScannerEngineBackend.cameraImage
                Behavior on opacity { NumberAnimation{}}
                opacity: (UM.ToolbarData.state < 4 ? false :UM.ToolbarData.state > 8 ? false:true  && UM.ScannerEngineBackend.processing) ? 1:0
                rotation: -90
            }
        }
    }
    /*AnimatedImages
    {
        source:"inProgress.gif"
        anchors.horizontalCenter:parent.horizontalCenter
        anchors.bottom:parent.bottom
        visible:UM.ScannerEngineBackend.processing
    }*/

    UM.PreferencesDialog { id: preferences }

    Action 
    {
        id: undo_action;
        text: "Undo";
        iconName: "edit-undo";
        shortcut: StandardKey.Undo;
        onTriggered: UM.OperationStack.undo();
        enabled: UM.OperationStack.canUndo;
    }

    Action 
    {
        id: redo_action;
        text: "Redo";
        iconName: "edit-redo";
        shortcut: StandardKey.Redo;
        onTriggered: UM.OperationStack.redo();
        enabled: UM.OperationStack.canRedo;
    }

    Action 
    {
        id: quit_action;
        text: "Quit";
        iconName: "application-exit";
        shortcut: StandardKey.Quit;
        onTriggered: Qt.quit();
    }

    Action 
    {
        id: preferences_action;
        text: "Preferences";
        iconName: "configure";
        onTriggered: preferences.visible = true;
    }
    
    Action
    {   
        id: plugin_action;
        text: "Plugins";
        onTriggered: 
        {
            preferences.visible = true;
            preferences.setPage(2);  
        }
    }
    
    Action
    {   
        id: settings_action;
        text: "Settings";
        onTriggered: 
        {
            preferences.visible = true;
            preferences.setPage(1);  
        }
    }

    Action 
    {
        id: helpAction;
        text: "Show Manual";
        iconName: "help-contents";
        shortcut: StandardKey.Help;
    }

    Action 
    {
        id: aboutAction;
        text: "About...";
        iconName: "help-about";
    }

    Action 
    {
        id: delete_action;
        text: "Delete Selection";
        iconName: "edit-delete";
        shortcut: StandardKey.Delete;
        onTriggered: UM.Controller.removeSelection();
    }

    Action 
    {
        id: load_file_action;
        text: "Open...";
        iconName: "document-open";
        shortcut: StandardKey.Open;
        onTriggered: open_file_dialog.open()
    }

    Action 
    {
        id: save_file_action;
        text: "Save...";
        iconName: "document-save";
        shortcut: StandardKey.Save;
        onTriggered: UM.Controller.saveWorkspace();
    }

    Menu 
    {
        id: contextMenu;

        MenuItem { action: delete_action; }
    }
   
    FileDialog 
    {
        id: open_file_dialog

        title: "Choose files"
        modality: Qt.NonModal
        //TODO: Support multiple file selection, workaround bug in KDE file dialog
        //selectMultiple: true

        onAccepted: 
        {
            UM.Controller.addMesh(fileUrl)
        }
    }

    
    
    

}
