import QtQuick 2.2
import QtQuick.Controls 1.1
import QtQuick.Layouts 1.1
import QtQuick.Dialogs 1.1
import QtQuick.Window 2.1
import UM 1.0 as UM
Window
{
    ColumnLayout
    {
        ProgressBar 
        {
            id: progressBar;

            minimumValue: 0;
            maximumValue: 100;

            Connections {
                target: UM.Backend;
                onProcessingProgress: progressBar.value = amount;
            }
        }
        RowLayout
        {
            CalibrationButton
            {
                text:"Board" 
                id:"board_button" 
                active:true
                key:"board"
            }
            
            CalibrationButton
            {
                text:"Camera" 
                id:"camera_focus_button" 
                key:"camera_focus"
            }
            
            CalibrationButton
            {
                text:"Projector" 
                id:"projector_button" 
                key:"projector_focus"
            }
            
            CalibrationButton
            {
                text:"exposure" 
                id:"camera_exposure_button" 
                key:"camera_exposure"
            }
            CalibrationButton
            {
                text:"Calibrate" 
                id:"calibrate_button" 
                key:"calibrate"
            }
        }
        
        Label
        {
            id:warning_label
            text:UM.ScannerEngineBackend.warningText
        }
        
        Image 
        {
            source: UM.ScannerEngineBackend.cameraImage
            width:250
            height:250
        }
    }
}