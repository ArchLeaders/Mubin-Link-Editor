# Mubin-Link-Editor

A Blender addon made for editing BotW mubin links.

### Current Features -
> _Import/Export_

Creating new templates.<br>
Exporting and saving new templates.<br>
<br>

> _Actors_

Autofill parameters.<br>
Copying actor parameters.<br>
Importing Ice-Spear JSON or actor parameters.<br>
Placing actors in 3D (additional setup required)<br>
<br>

> _Links_

Autofill parameters.<br>
<br>

> _Settings_

Add new actor nodes.<br>
Edit ignored properties.<br>
<br>

### WIP Features -
> _Import/Export_

Verify parameters.<br>
<br>

> _Actors_

Reference info in 3D viewport.<br>
<br>

> _Settings_

Exported models path and setup.<br>
<br>

## Setup

Download the [source code](https://github.com/ArchLeaders/Mubin-Link-Editor/archive/refs/heads/master.zip) as a zip file and install it with Blender.<br>
Make sure Blender is running as administrator before you enable the addon or oead will not install correctly.

To import the correct actor models, add a new file to `%LOCALAPPDATA%\mubin_link_editor` named `config.json` with the contents:
```json
{
    "exported": "path\\to\\exported\\models"
}
```
`path\\to\\exported\\models` should point to the directory containing the vanilla model files exported as dae.<br>
You can use [this tool](https://github.com/ArchLeaders/Botw-Modding-Toolkit/blob/master/Scripts/C%23/win-x64.7z) to export the vanilla files as dae. BCML must be installed and setup. DotNET 6.0 Runtime must also be installed.

The tool spits out a folder named `export`, place it anywhere; the export folder is what needs to be referenced in the `config.json` file. (It doesn't need to be named export.)

> Please report any errors you encounter with as much detail as you can provide.<br>
> Errors can be reported as a GitHub [issue](https://github.com/ArchLeaders/Mubin-Link-Editor/issues/new/choose) or on my [Discord](https://discord.gg/cbA3AWwfJj).
