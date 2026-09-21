Option Explicit

Dim shell
Dim fso
Dim projectRoot
Dim pythonExe
Dim listener
Dim command

Set shell = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")

projectRoot = fso.GetParentFolderName(WScript.ScriptFullName)
pythonExe = projectRoot & "\jarvis_env\Scripts\python.exe"
listener = projectRoot & "\clap_listener.py"

If Not fso.FileExists(pythonExe) Then
    pythonExe = "python"
End If

command = """" & pythonExe & """ """ & listener & """"
shell.Run command, 0, False

Set fso = Nothing
Set shell = Nothing
