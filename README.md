# Automated-TTS-corpus-builder
Automatically generates TTS dataset using audio and associated text. Make cuts under a custom length. Uses aeneas to force align text to audio. The extender increases tacotron2 corpus by splitting text at , . ? and ! , then producing associated audio splits with aeneas. Use the trimmer to remove any cuts under a certain length.


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
## corpus_builder.py: ##

Place .wav file of source audio and source text file inside repo directory.  

Run python corpus_builder.py -input_text (name of text_file) -audio_name (name of wav file) -output_wav_path (output wavefolder name) -cut_length (max length of cuts in seconds) -index_start (starting index number)

New .wav files will be wrote to output_wav_path.  Csv file of cuts will be wrote to /csv_out

## corpus_trimmer.py ##

Copy wave files directory into repo directory

Copy source text csv file into directory. 

Run py corpus_trimmer.py -csv (name of csv file) -min_length (minimum cut length in float seconds)

New csv file will be created in /csv_out

Wav files in directory that are too short will be deleted


# Recommendations

Several things will improve the quality of your cuts, although you should always proofread them before training. Currently this will only work with english language, but you can easily edit the aeneas command lines and character replacements to your need. Examine if things like chapter titles are included. Speakers with slow and even paced speech will make the cleanest cuts, while fast paced speakers tend to run words together and can cause some words, pieces of words, to be shifted into the next cut where it will have to be edited.
