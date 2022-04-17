# TTS-dataset-tools

Transcribe audio via Google Speech to Text API with speaker separation (diarisation/diarization). Automatically generate TTS datasets using audio and associated text. Uses Google API to transcribe cuts that have been split by the maximum silence break (recommended). Or use aeneas to force align text to audio. Quickly proofread and edit cuts.

For Google Speech to Text API you will need a Google Cloud Platform account. Your $GOOGLE_APPLICATION_CREDENTIALS env variable must point to your credentials JSON file path. Google is offering $300 worth of service and 3 months free on new accounts.

Run tools.py for GUI tools.

Current limitations are that you will need to adjust the column width of the proofreading section and when navigating entries you must take the focus off the current and next input textboxes or the text box will not update. The next version of "Dear PyGui" will solve these issues.

Using a VPN will interfere with long Google Speech to Text API requests.

![Dataset GUI](https://github.com/youmebangbang/Automated-TTS-dataset-builder/blob/master/example1.png)

![Dataset GUI](https://github.com/youmebangbang/Automated-TTS-dataset-builder/blob/master/example2.png)

Using the older version of "Dear PyGui" at the moment, I will migrate eventually.

# Installation

## Conda (Windows/Linux/Mac)

Install [Anaconda](https://www.anaconda.com/download/) or [Miniconda](https://conda.io/miniconda.html)

Create a new environment using the included `conda_environment.yml` file <br>
_You might need [Visual Studio 2019](https://visualstudio.microsoft.com/downloads/) or [Microsoft Build Tools For Visual Studio 2019](https://visualstudio.microsoft.com/downloads/) with the C++ installation option for pip to install simpleaudio with the environment file_

```
conda env create -f conda_environment.yml
```

This will create a new environment using the environment file included and install all of the required dependencies inside of the environment.
To activate the environment, run

```
conda activate ttstools
```

and to run the tool run `python tools.py`

## Windows (Python)

It's recommended to use a virtual environment to separate the dependencies from any other projects you might be running with Python.<br>
You can create one with the command below and it will save the virtual environment folder to the current work directory.

```bat
python -m venv environmentname
```

Then to activate it, run the `activate.bat` or `activate.ps1` inside of the virtual environment's Script folder. <br> For example: `environmentname/Scripts/activate.bat` or `environmentname/Scripts/activate.ps1`

Then run the following to install the dependencies needed to run the script.

```
pip install numpy
pip install pydub
pip install dearpygui==0.6.415
pip install google-cloud-speech
pip install google-cloud-storage
pip install simpleaudio
pip install sox
```

_You might need [Visual Studio 2019](https://visualstudio.microsoft.com/downloads/) or [Microsoft Build Tools For Visual Studio 2019](https://visualstudio.microsoft.com/downloads/) with the C++ installation option to install simpleaudio with pip_

To run the script, run `python tools.py`

## Linux (Python)

A Linux environment is recommended for the aeneas option. In Windows, aeneas will not be able to make longer cuts due to memory issues.

It's recommended to use a virtual environment to separate the dependencies from any other projects you might be running with Python.<br>
You can create one with the command below and it will save the virtual environment folder to the current work directory.

```sh
python3 -m venv environmentname
```

Then to activate it, run the following from the parent folder of the environment

```sh
source environmentname/bin/activate
```

Then run the following to install the dependencies needed to run the script.

```sh
pip install numpy
pip install aeneas
pip install pydub
pip install dearpygui==0.6.415
pip install google-cloud-speech
pip install google-cloud-storage
pip install simpleaudio
pip install sox
```

If you encounter a libpython error, install `libasound2-dev` (apt) or `alsa-lib-devel` (dnf/yum) depending on your package manager.

To run the script, run `python tools.py`

# Usage

Video tutorial: https://www.youtube.com/watch?v=tE7pUi2XEJE

# Recommendations

Several things will improve the quality of your cuts, although you should always proofread them before training. For languages other than English you can easily edit the aeneas command lines and character replacements to your need, and replace the google en-US languages codes with your language code (https://cloud.google.com/speech-to-text/docs/languages). Examine if things like chapter titles are included. Speakers with slow and even-paced speech will make the cleanest cuts, while fast-paced speakers tend to run words together and can cause some words, pieces of words, to be shifted into the next cut where it will have to be edited. Remove all music if able.
