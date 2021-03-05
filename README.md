# Automated-TTS-dataset-builder
Automatically generates TTS dataset using audio and associated text. Make cuts under a custom length. Uses aeneas to force align text to audio. Create more source text and audio by splitting entries and combining end and beginning halves. Run dataset_gui.py for GUI tools.


# Setup
Linux environment is recommended. If using windows aeneas will not be able to make longer cuts due to memory issues. 
In linux, install aeneas and pydub:

wget https://raw.githubusercontent.com/readbeyond/aeneas/master/install_dependencies.sh

bash install_dependencies.sh
pip install numpy
pip install aeneas
test installation:  python -m aeneas.diagnostics
pip install pydub
pip install dearpygui
pip install google-cloud-speech
pip install google-cloud-storage

# Usage


# Recommendations

Several things will improve the quality of your cuts, although you should always proofread them before training. Currently this will only work with english language, but you can easily edit the aeneas command lines and character replacements to your need. Examine if things like chapter titles are included. Speakers with slow and even paced speech will make the cleanest cuts, while fast paced speakers tend to run words together and can cause some words, pieces of words, to be shifted into the next cut where it will have to be edited. Remove all music if able.
