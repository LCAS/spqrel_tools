# Description of data format #

A data recording session is stored in a folder, containing three typer of data:

- *keys.log* data from memory (sensors, excluding images and audio, and variables computed by modules)
- *TypeCamera*: images from cameras
- *asr_log*: audio files

Memory data are stored in a text file *keys.log* with the following format:
- first row: comma separated list of memory keys
- next rows: timestamp + "\n" + comma separated values corresponding to the keys

Audio files are stored in the *asr_log* folder both as wav and flac files with timestamp included in the name of the file.

Images are stored in *TypeCamera* folder in PNG format with timestamp included in the name of the file.
