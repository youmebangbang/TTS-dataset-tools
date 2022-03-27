# TTS-dataset-tools
Transcribe audio via Google Speech to Text API with speaker separation (diarization). Automatically generate TTS datasets using audio and associated text. Uses Google API to transcribe cuts that have been split by the maximum silence break (recommended). Or use aeneas to force align text to audio. Quickly proofread and edit cuts.

For Google Speech to Text API you will need a Google Cloud Platform account. Your $GOOGLE_APPLICATION_CREDENTIALS env variable must point to your credentials JSON file path. Google is offering $300 worth of service and 3 months free on new accounts.

Run tools.py for GUI tools. 

Current limitations are that you will need to adjust column width of the proofreading section and when navigating entries you must take the focus off the current and next input text boxes or the text box will not update. Next version of dearpy gui will solve these issues.

Using a VPN will interfere with long Google Speech to Text API requests.

![Dataset GUI](https://github.com/youmebangbang/Automated-TTS-dataset-builder/blob/master/example1.png)

![Dataset GUI](https://github.com/youmebangbang/Automated-TTS-dataset-builder/blob/master/example2.png)

Using the older version of dearpygui at the momement, I will migrate eventually.

# Windows Setup
pip install numpy --user

pip install pydub --user

pip install dearpygui==0.6.415 --user

pip install google-cloud-speech --user

pip install google-cloud-storage --user

pip install simpleaudio --user

*If you can't build simpleaudio make sure you have gcc installed: sudo apt-get update , sudo apt-get install build-essentials

pip install sox --user

# Linux Setup
Linux environment is recommended for Aeneas option, in windows aeneas will not be able to make longer cuts due to memory issues. 

wget https://raw.githubusercontent.com/readbeyond/aeneas/master/install_dependencies.sh

bash install_dependencies.sh

pip install numpy --user

pip install aeneas --user

test installation:  python -m aeneas.diagnostics

pip install pydub --user

pip install dearpygui==0.6.415 --user

pip install google-cloud-speech --user

pip install google-cloud-storage --user

pip install simpleaudio --user

pip install sox --user

If you get libpython error: 

sudo apt install libasound2-dev

edit your bashrc file by typing: sudo nano ~/.bashrc

Then add the line at the end with your info depending where your package was installed: 

export LD_LIBRARY_PATH="/[yourhomepath]/anaconda3/envs/[yourenv]/lib/"

OR

export LD_LIBRARY_PATH="/[yourhomepath]/.conda/envs/[yourenv]/lib/"

OR if base environment

export LD_LIBRARY_PATH="/[yourhomepath]/anaconda3/lib/"

Press CTRL+o to export the updated file. Then CTRL+x to exit.

Type source ~/.bashrc to enable the new path.

# Usage

Video tutorial: https://www.youtube.com/watch?v=tE7pUi2XEJE

# Recommendations

Several things will improve the quality of your cuts, although you should always proofread them before training. For languages other than english you can easily edit the aeneas command lines and character replacements to your need, and replace the google en-US languages codes with your language code (https://cloud.google.com/speech-to-text/docs/languages). Examine if things like chapter titles are included. Speakers with slow and even paced speech will make the cleanest cuts, while fast paced speakers tend to run words together and can cause some words, pieces of words, to be shifted into the next cut where it will have to be edited. Remove all music if able.
