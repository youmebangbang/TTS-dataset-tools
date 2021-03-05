import io
import math
from pydub import AudioSegment
from pydub.utils import mediainfo
from dearpygui.core import *
from dearpygui.simple import *
import os
import ntpath
import csv
import argparse
import numpy as np
import re
import shutil
from google.cloud import storage
from google.cloud import speech as speech

class Project:
    def __init__(self, project_name, speaker_text_path, wav_file_path, index_start, cut_length, contains_punc):    
        self.project_name = project_name
        self.speaker_text_path = speaker_text_path
        self.wav_file_path = wav_file_path
        self.index_start = index_start
        self.cut_length = cut_length
        self.contains_punc = contains_punc

    def build_dataset(self):
        output_wav_path = "{}/wavs/".format(self.project_name)

        if not os.path.exists(self.project_name):
            os.mkdir(self.project_name)
        
        if not os.path.exists(output_wav_path):
            os.mkdir(output_wav_path) 

        if not os.path.exists("aeneas_out"):
            os.mkdir("aeneas_out")
        else:
            shutil.rmtree("aeneas_out")
            os.mkdir("aeneas_out")  

        if not os.path.exists("aeneas_prepped"):
            os.mkdir("aeneas_prepped")
        else:
            shutil.rmtree("aeneas_prepped")
            os.mkdir("aeneas_prepped")  

        audio_name = self.wav_file_path   

        with open(self.speaker_text_path, 'r', encoding="utf8") as f:
            text = f.read()
            text = text.replace(';', '.')
            text = text.replace(':', '.')
            text = text.replace('-', ' ')
            text = text.replace('”', '')
            text = text.replace('“', '')
            text = text.replace('"', '.')
            text = text.replace('—', ' ')
            text = text.replace('’', '\'')
            text = text.replace(' –', '.')
            text = text.strip('\n')

            if self.contains_punc:
                #remove any duplicate whitespace between words
                text = " ".join(text.split())

                phrase_splits = re.split(r'(?<=[\.\!\?])\s*', text)   #split on white space between sentences             
                phrase_splits = list(filter(None, phrase_splits))  #remove empty splits
            else:                
                #no punctuation from speech to text, so we must divid text by word count
                phrase_splits = []
                temp_line = []
                text_split = text.split()
                word_count_limit = 16
         
                while len(text_split) > 0:
                    while len(temp_line) < word_count_limit and len(text_split) > 0:
                        temp_line.append(text_split.pop(0))
                    phrase_splits.append(" ".join(temp_line))
                    temp_line = []

            with open('aeneas_prepped/split_text', 'w') as f:
                    newline = ''
                    for s in phrase_splits: 
                        if s:   
                            stripped = s.strip()   #remove whitespace                        
                            f.write(newline + stripped) 
                            newline = '\n'          
            #os.system('python -m aeneas.tools.execute_task ' + audio_name  + ' aeneas_prepped/split_text "task_adjust_boundary_percent_value=50|task_adjust_boundary_algorithm=percent|task_language=en|is_text_type=plain|os_task_file_format=csv" ' + 'aeneas_out/' + audio_name_no_ext + '.csv')
            os.system('python -m aeneas.tools.execute_task ' + audio_name  + ' aeneas_prepped/split_text "task_adjust_boundary_percent_value=50|task_adjust_boundary_algorithm=percent|task_language=en|is_text_type=plain|os_task_file_format=csv" ' + 'aeneas_out/' + self.project_name + '.csv')

            output_exists = False
            if os.path.exists("{}/output.csv".format(self.project_name)):
                #if file exists then prepare for append
                output_exists = True

            new_csv_file = open("{}/output.csv".format(self.project_name), 'a')
            if output_exists:
                new_csv_file.write("\n") 
            
            with open('aeneas_out/' + self.project_name + '.csv', 'r') as csv_file:
                
                index_count = int(self.index_start)
                csv_reader = csv.reader(csv_file, delimiter=',')
                csv_reader = list(csv_reader) #convert to list
                row_count = len(csv_reader) 
            
                newline = ""
                     
                for row in csv_reader:   
                    beginning_cut = float(row[1])
                    end_cut = float(row[2])
                    text_out = row[3]
                    text_out = text_out.strip()  
                    print("{} {} {} ".format(beginning_cut, end_cut, text_out))
                    c_length = end_cut - beginning_cut
            
                    #if cut is longer than cut length then split it even more
                    cut_length = float(self.cut_length)
                    if c_length > cut_length:    
                                        
                        more_cuts = open("aeneas_prepped/temp.csv", 'w')

                        #export the current cut wav file to run on aeneas again
                        w = AudioSegment.from_wav(audio_name)
                        wav_cut = w[(beginning_cut*1000):(end_cut*1000)]
                        wav_cut.export("aeneas_prepped/tempcut.wav", format="wav")

                        split_list = []                    
                        num_cuts = math.ceil(c_length / cut_length)                        
                        text_list = text_out.split()
                        text_list_len = len(text_list)
                        split_len = math.ceil(text_list_len / num_cuts)
                        print("too long, making extra {} cuts. with length {}".format(num_cuts, split_len))
                        for i in range(1, num_cuts+1):
                            words = []
                            for j in range(0, split_len):
                                if not text_list:
                                    break
                                words.append(text_list.pop(0))
                            split_list.append(" ".join(words))  
                        print(split_list)
                        print()
                        
                        newline_splits = ''
                        for phrase in split_list:
                            more_cuts.write(newline_splits + phrase)
                            newline_splits = '\n'
                        more_cuts.close()  

                        os.system('python -m aeneas.tools.execute_task ' + "aeneas_prepped/tempcut.wav"  + ' aeneas_prepped/temp.csv "task_adjust_boundary_percent_value=50|task_adjust_boundary_algorithm=percent|task_language=en|is_text_type=plain|os_task_file_format=csv" ' + 'aeneas_out/temp_out.csv')

                        csv_file_temp = open('aeneas_out/temp_out.csv', 'r')
                        csv_reader_temp = csv.reader(csv_file_temp, delimiter=',')
                        csv_reader_temp = list(csv_reader_temp) #convert to list
                        row_count = len(csv_reader_temp)
    
                        w = AudioSegment.from_wav("aeneas_prepped/tempcut.wav")

                        for row in csv_reader_temp:   
                            beginning_cut = float(row[1])
                            end_cut = float(row[2])
                            text_out = row[3]
                            text_out = text_out.strip() 

                            wav_cut = w[(beginning_cut*1000):(end_cut*1000)]
                            new_wav_filename = str(index_count) + ".wav"                        
                            new_csv_file.write("{}{}|{}".format(newline, new_wav_filename, text_out))
                            wav_cut.export(output_wav_path + new_wav_filename, format="wav")
                            index_count += 1
                            newline = '\n'

                        csv_file_temp.close()
                        
                                    
                    else:
                        w = AudioSegment.from_wav(audio_name)
                        wav_cut = w[(beginning_cut*1000):(end_cut*1000)]
                        new_wav_filename =  str(index_count) + ".wav"
                        new_csv_file.write("{}{}|{}".format(newline, new_wav_filename, text_out))
                        wav_cut.export(output_wav_path + new_wav_filename, format="wav")
                        index_count += 1
                        newline = '\n'

            new_csv_file.close()
            set_value("label_build_status", "Building dataset done!")


def upload_blob(bucket_name, source_file_name, destination_blob_name):

    #storage_client = storage.Client.from_service_account_json(json_credentials_path='C:\TTS-corpus-builder\My First Project-b660c6889e30.json')
    storage_client = storage.Client()

    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)
    blob.upload_from_filename(source_file_name)
    print("File {} uploaded to {}.".format(source_file_name, destination_blob_name))


def transcribe_file(wavfile, bucket_name, project_name):
    if not os.path.exists(project_name):
        os.mkdir(project_name)
    print("Uploading {} to google cloud storage bucket".format(wavfile))
    set_value("label_wav_file_transcribe", "Uploading file to cloud storage bucket...")    
    upload_blob(bucket_name, wavfile, "temp_audio.wav")
    gcs_uri = "gs://{}/temp_audio.wav".format(bucket_name)
    set_value("label_wav_file_transcribe", "Finished uploading.")    

    #break wav file into < 10mb chunks
    # wavs = []
    # w = AudioSegment.from_wav(speech_file)
    # w_len = len(w)
    # wav_cut_length = 50 * 1000    #5 minutes
    # num_cuts = math.floor(w_len/wav_cut_length) + 1
    # if num_cuts == 0:
    #     wavs.append(w)
    # else:            
    #     for x in range(0, num_cuts):
    #         print("making cut")
    #         if x == num_cuts:
    #             wavs.append(w[x*wav_cut_length :])  
    #             wavs[x].export(str(x) + ".wav", format="wav")      
    #         else:
    #             wavs.append(w[x*wav_cut_length : (x+1)*wav_cut_length])
    #             wavs[x].export(str(x) + ".wav", format="wav")    
    # newline = ""
    # print("{} chunks to be processed...".format(len(wavs)))        
    #print("processing chunk# {}".format(count))

    client = speech.SpeechClient()

    audio = speech.RecognitionAudio(uri=gcs_uri)

    info = mediainfo(wavfile)
    sample_rate = info['sample_rate']
    print("Transcribing {} with audio rate {}".format(wavfile, sample_rate))
  
  
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=int(sample_rate),
        language_code="en-US",
        enable_automatic_punctuation=True,
    )

    operation = client.long_running_recognize(config=config, audio=audio)

    print("Waiting for operation to complete, this may take several minutes...")
    set_value("label_wav_file_transcribe", "Waiting for operation to complete, this may take several minutes...")    

    response = operation.result(timeout=28800)    

        # for word_info in words_info:
        #     print(u"word: '{}', speaker_tag: {}".format(word_info.word, word_info.speaker_tag))
        #     f.write(newline + str(word_info.word) + " " + str(word_info.speaker_tag))
        #     newline = '\n'

    result_array = []
    newline = ""
    #word_info_array = []
    if not os.path.exists(project_name):
        os.mkdir(project_name)
        
    with open ("{}/transcribed.txt".format(project_name), 'w') as f:
        for result in response.results:            
            result_array.append(result.alternatives[0].transcript)
            #word_info_array.append(result.alternatives[0].words)
            
            print("Transcript: {}".format(result.alternatives[0].transcript))
            #print("Confidence: {}".format(result.alternatives[0].confidence))                    
        f.write("".join(result_array))
            
    set_value("label_wav_file_transcribe", "Done!")    


def open_speaker_txt_file_callback(sender, data):
    open_file_dialog(add_speaker_txt_file)

def open_wav_file_callback(sender, data):
    open_file_dialog(add_speaker_wav_file)    
   
def open_wav_file_transcribe_callback(sender, data):
    open_file_dialog(add_wav_file_transcribe) 

def add_wav_file_transcribe(sender, data):
    #open working wav for transcribing
    set_value("label_wav_file_transcribe", "{}/{}".format(data[0], data[1]))    

def run_google_speech_callback(sender, data):
    #run transcription
    transcribe_file(get_value("label_wav_file_transcribe"), get_value("input_storage_bucket"), get_value("input_project_name_transcribe"))     

def run_dataset_builder_callback(sender, data):
    #check to see if txt and wav file was selected
    set_value("label_build_status", "Running builder...")
    if get_value("input_project_name") and get_value("label_speaker_text_path") and get_value("label_wav_file_path"):
        print("running")
        myproject = Project(get_value("input_project_name"), get_value("label_speaker_text_path")
        , get_value("label_wav_file_path"), get_value("input_starting_index"), get_value("input_cut_length"), get_value("input_contains_punc"))
        myproject.build_dataset()
    else:
        print("error: enter inputs")

def add_speaker_txt_file(sender, data):
    #open working speaker text
    set_value("label_speaker_text_path", "{}/{}".format(data[0], data[1]))

def add_speaker_wav_file(sender, data):
    #open working speaker text
    set_value("label_wav_file_path", "{}/{}".format(data[0], data[1]))

set_main_window_size(1200,800)
set_main_window_title("DeepVoice Dataset Creator 1.0 by YouMeBangBang")
set_global_font_scale(1.5)


set_theme("Dark")
#set_theme_item(mvGuiCol_WindowBg, 0, 0, 200, 200)

with window("mainWin"):

    with tab_bar("tb1"):
        with tab("tab0", label="Transcribe Audio"):
            add_spacing(count=5)
            add_text("For Google Speech to Text API you will need a Google Cloud Platform account.\n Your $GOOGLE_APPLICATION_CREDENTIALS must point to your credentials JSON file.")
            add_spacing(count=5)
            add_text("Enter name of project: ")
            add_same_line(spacing=10)
            add_input_text("input_project_name_transcribe", width=200, default_value="MyProject", label="") 

            add_spacing(count=5)
            add_text("Enter name of your clould storage bucket: ")
            add_same_line(spacing=10)
            add_input_text("input_storage_bucket", width=200, default_value="my_bucket", label="") 

            add_spacing(count=5)
            add_text("Select the wav file to transcribe (must be mono)")
            add_button("open_wav_file_transcribe", callback=open_wav_file_transcribe_callback, label="Open wav file") 
            add_spacing(count=5)
            add_button("run_google_speech", callback=run_google_speech_callback, label="Run Google Speech to Text") 
            add_spacing(count=5)
            add_label_text("label_wav_file_transcribe", label="")



        with tab("tab1", label="Build Dataset"):

            add_spacing(count=5)
            add_text("Enter name of project: ")
            add_same_line(spacing=10)
            add_input_text("input_project_name", width=200, default_value="myproject", label="") 
            add_spacing(count=5)
            add_text("Enter starting index (default is 1): ")
            add_same_line(spacing=10)
            add_input_text("input_starting_index", width=200, default_value="1", label="")     
            add_spacing(count=5)
            add_text("Enter max cut length in seconds (default is 11.0): ")
            add_same_line(spacing=10)
            add_input_text("input_cut_length", width=200, default_value="11.0", label="")            
            add_spacing(count=5)

            add_text("Does the text have proper punctuation? ")
            add_same_line(spacing=10)
            add_checkbox("input_contains_punc", default_value=1, label="")                         
            add_spacing(count=5)            
            add_text("Select speaker text file to open: ")
            add_same_line(spacing=10)
            add_button("open_speaker_text", callback=open_speaker_txt_file_callback, label="Open txt file") 
            add_spacing(count=5)
            add_label_text("label_speaker_text_path", label="")
            add_spacing(count=5)
            add_text("Select speaker audio wav file to open: ")
            add_same_line(spacing=10)
            add_button("open_wav_file", callback=open_wav_file_callback, label="Open wav file") 
            add_label_text("label_wav_file_path", label="")
            add_spacing(count=5)
            add_button("run_dataset_builder", callback=run_dataset_builder_callback, label="Run dataset builder") 
            add_spacing(count=5)
            add_label_text("label_build_status", label="")



        with tab("tab2", label="Proofread Dataset"):
            add_spacing(count=5)
            add_text("Choose a csv file to proofread and edit wavs")

        with tab("tab3", label="Increase Dataset"):
            add_spacing(count=5)
            


start_dearpygui(primary_window="mainWin")