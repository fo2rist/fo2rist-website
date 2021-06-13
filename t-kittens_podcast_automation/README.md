# Scripts that automate T-Kittens podcast production

Main files' names represent the sequence of steps (00 being first, 01 potentially next, etc.)
Other files are the collection of utils.

## More about automation
The data about episodes is stored at [airtable](https://airtable.com)
The recording is done via [zencastr.com](https://zencastr.com) which stores files to Google Drive folder
The sound pre-production is done by [auphonic.com](https://auphonic.com) which take files from another Google Drive folder and store results there
The final production is done locally with files produced by auphonic.

Automation steps:
* prepare episode folder with template file
* take audio from recording folder and description from filled template and initiate pre-production
* take pre-produced audio, move it to episode folder and do the final production (intro, fade out, background music)
