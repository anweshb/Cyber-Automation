# param ($logfile, $saveas)
# C:/Users/tingwei/Desktop/ProcessMonitor/Procmon.exe /Quiet /OpenLog $logfile /SaveAs $saveas

param ($procmonlocation, $logfile, $saveas)
$procmonlocation /Quiet /OpenLog $logfile /SaveAs $saveas