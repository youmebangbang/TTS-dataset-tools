# Automated-TTS-corpus-builder
Automatically generates TTS dataset using audio and associated text. Make cuts under a custom length. Uses aeneas to force align text to audio.

# Setup
Linux environment is recommended. If using windows aeneas will not be able to make longer cuts due to memory issues. 
In linux, install aeneas:

wget https://raw.githubusercontent.com/readbeyond/aeneas/master/install_dependencies.sh
bash install_dependencies.sh
pip install numpy
pip install aeneas
test installation:  python -m aeneas.diagnostics

pip install pydub

# Usage
Place .wav file of source audio and source text file inside main directory.  
Run python corpus_builder.py -input_text name_of_text_file -audio_name name_of_wav_file -output_wav_path output_wavefolder_name -index_start starting_index_number
