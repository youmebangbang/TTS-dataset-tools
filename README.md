# Automated-TTS-corpus-builder
Automatically generates TTS dataset using audio and associated text. Make cuts under a custom length. Uses aeneas to force align text to audio.

# Setup
Linux environment is recommended. If using windows aeneas will not be able to make longer cuts due to memory issues. 
In linux, install aeneas and pydub:

wget https://raw.githubusercontent.com/readbeyond/aeneas/master/install_dependencies.sh

bash install_dependencies.sh

pip install numpy

pip install aeneas

test installation:  python -m aeneas.diagnostics

pip install pydub

# Usage
Place .wav file of source audio and source text file inside main directory.  

Run python corpus_builder.py -input_text name_of_text_file -audio_name name_of_wav_file -output_wav_path output_wavefolder_name -index_start starting_index_number

New .wav files will be wrote to output_wav_path.  Csv file of cuts will be wrote to /csv_out

# Recommendations

Several things will improve the quality of your cuts, although you should always proofread them before training. Currently this will only work with english language, but you can easily edit the aeneas command lines and character replacements to your need. Examine if things like chapter titles are included. Speakers with slow and even paced speech will make the cleanest cuts, while fast paced speakers tend to run words together and can cause some words, pieces of words, to be shifted into the next cut where it will have to be edited.
