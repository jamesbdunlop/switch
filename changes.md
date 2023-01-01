## v0.1.8
Improvements
---
- Better error handling with a popup widget to feedback what went wrong.
- Changes to splash image

Fixes
---
- Fixes to saving the nested custom docks correctly for re-opening app in previous state.

## v0.1.7
Improvements
---
- Adds a splash screen
- Changes right click menu in custom browser to show only when valid selections exist
- Fixes themes not switching on custom browsers


## v0.1.6
Improvements
---
- Custom config browsers now restore when the UI is opened
- Added the ability to right click and archive a folder to a custom location.
- Added a restore archive to the custom browser config
- Some class cleanup etc

Fixes
---
- Custom config docs named incorrectly so when stacking on top of each other they were not showing fp


## v0.1.5
Improvements
---
- Themes now store in the QSettings
- Added an edit for the theme to change the base theme.json


## v0.1.4

Fixes
---
- Fix for the theme not passing along to the configWidget.
- Fixes the configWidget sharing the same name as the folderWidget.
- Stop the QSettings being created with vers number. This should see recent configs/files persist across version updates.


## v0.1.2
Fixes
---
- Fixed project path so you don't need the project name in it too.
- Basic drag and drop added for copy/move of files.


## v0.1.1
Fixes
---
- Fixed help info to remove projectName from the projectPath
