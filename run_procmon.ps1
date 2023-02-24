#param ($configfile, $backingfile)
param ($procmonlocation, $configfile, $backingfile)
#C:\Users\tingwei\Desktop\ProcessMonitor\Procmon.exe /Quiet /LoadConfig $configfile /BackingFile $backingfile
&$procmonlocation /Quiet /LoadConfig $configfile /BackingFile $backingfile