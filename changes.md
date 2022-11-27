## v0.0.6
Improvements
---
- Custom config browsers now restore when the UI is opened
- Added the ability to right click and archive a folder to a custom location.
- Added a restore archive to the custom browser config
- Some class cleanup etc

Fixes
---
- Custom config docs named incorrectly so when stacking on top of each other they were not showing fp


## v0.0.5
Improvements
---
- Themes now store in the QSettings
- Added an edit for the theme to change the base theme.json


## v0.0.4

Fixes
---
- Fix for the theme not passing along to the configWidget.
- Fixes the configWidget sharing the same name as the folderWidget.
- Stop the QSettings being created with vers number. This should see recent configs/files persist across version updates.


## v0.1.0
Fixes
---
- Fixed project path so you don't need the project name in it too.
- Basic drag and drop added for copy/move of files.


## v0.1.1
Fixes
---
- Fixed help info to remove projectName from the projectPath
