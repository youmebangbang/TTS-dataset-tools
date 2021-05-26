import datetime
from pathlib import Path
import numpy
import simpleaudio as sa
import io
import math
from pydub import AudioSegment, silence
from pydub.utils import mediainfo
from pydub.playback import play
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
#from google.cloud import speech as speech
from google.cloud import speech_v1p1beta1 as speech

def to_millis(timestamp):
    timestamp = str(timestamp)
    hours, minutes, seconds = (["0", "0"] + timestamp.split(":"))[-3:]
    hours = int(hours)
    minutes = int(minutes)
    seconds = float(seconds)
    miliseconds = int(3600000 * hours + 60000 * minutes + 1000 * seconds)
    return miliseconds

class Dataset_builder:
    def __init__(self):    
        self.project_name = None
        self.speaker_text_path = None
        self.wav_file_path = None
        self.index_start = None
        self.cut_length = None
        self.split_method = None
    
    def set_values(self, project_name, speaker_text_path, wav_file_path, index_start, cut_length, split_method):    
        self.project_name = project_name
        self.speaker_text_path = speaker_text_path
        self.wav_file_path = wav_file_path
        self.index_start = index_start
        self.cut_length = float(cut_length)
        self.split_method = split_method

    def build_dataset(self):
        output_wav_path = "{}/wavs/".format(self.project_name)

        if not os.path.exists(self.project_name):
            os.mkdir(self.project_name)
        
        if not os.path.exists(output_wav_path):
            os.mkdir(output_wav_path) 

        if self.split_method == 0:
            #Google API mode
            audio_name = self.wav_file_path   
            w = AudioSegment.from_wav(audio_name)

            s_len = 1000
            def split_wav(w, l):
                c = silence.split_on_silence(w, min_silence_len=l, silence_thresh=-45, keep_silence=True)
                return c

            silence_cuts = split_wav(w, s_len)
            cuts = []
            final_cuts = []


            # print(silences)
            # for i, e in enumerate(silences):
            #     e.export("{}/{}.wav".format(self.project_name, i), format="wav")
            
            c_split_len = 1
            s_len_temp = s_len - 100

            for c in silence_cuts:
                if (c.duration_seconds * 1000) > (self.cut_length * 1000):
                    # cut again, too long 
                    #print("cutting again...")
                    while c_split_len == 1:      
                        #print(s_len_temp)  
                        c_split = split_wav(c, s_len_temp)
                        c_split_len = len(c_split)
                        s_len_temp -= 100   #reduce split time for hopefully more cuts
                    c_split_len = 1
                    s_len_temp = s_len - 100
                    for i in c_split:
                        cuts.append(i)                       
                else:
                    cuts.append(c)

            # rebuild small cuts into larger, but below split len        
            temp_cuts = AudioSegment.empty()
            prev_cuts = AudioSegment.empty()

            for i, c in enumerate(cuts):
                prev_cuts = temp_cuts             
                temp_cuts = temp_cuts + c

                if i == (len(cuts) - 1):
                    #on final entry
                    if (temp_cuts.duration_seconds * 1000)  > (self.cut_length * 1000):
                        final_cuts.append(prev_cuts)
                        final_cuts.append(c)
                    else:
                        final_cuts.append(temp_cuts)
                else:
                    if ((temp_cuts.duration_seconds * 1000) + (cuts[i+1].duration_seconds * 1000)) > (self.cut_length * 1000):
                        # combine failed, too long, add what has already been concatenated
                        final_cuts.append(temp_cuts)
                        temp_cuts = AudioSegment.empty()               
            
            if not os.path.exists("{}/wavs".format(self.project_name)):
                os.mkdir("{}/wavs".format(self.project_name))

            for i, w in enumerate(final_cuts):
                w.export("{}/wavs/{}.wav".format(self.project_name, i), format="wav")
            
            # Process each cut into google API and add result to csv
            with open("{}/output.csv".format(self.project_name), 'w') as f:
                bucket_name = get_value("input_storage_bucket")
                newline = ''
                for i, c in enumerate(final_cuts):
                    print(f"Transcribing entry {i}")
                    self.upload_blob(bucket_name, "{}/wavs/{}.wav".format(self.project_name, i), "temp_audio.wav")
                    gcs_uri = "gs://{}/temp_audio.wav".format(bucket_name)

                    client = speech.SpeechClient()

                    audio = speech.RecognitionAudio(uri=gcs_uri)

                    info = mediainfo("{}/wavs/{}.wav".format(self.project_name, i))
                    sample_rate = info['sample_rate']
                
                    config = speech.RecognitionConfig(
                        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
                        sample_rate_hertz=int(sample_rate),
                        language_code="en-US",
                        enable_automatic_punctuation=True,
                        enable_word_time_offsets=False, 
                        enable_speaker_diarization=False,
                    )

                    operation = client.long_running_recognize(config=config, audio=audio)
                    response = operation.result(timeout=28800)    

                    for result in response.results:
                        text = result.alternatives[0].transcript
                    print(text)
                    set_value("label_build_status", text)

                    f.write("{}wavs/{}.wav|{}".format(newline, i, text))
                    newline = '\n'
            print('\a') #system beep 
            set_value("label_build_status", "Done!")
            print("Done running builder!")

            
        else:
            # Aeneas mode
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

                            #save the current cut wav file to run on aeneas again
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
                                new_wav_filename = "wavs/" + str(index_count) + ".wav"                        
                                new_csv_file.write("{}{}|{}".format(newline, new_wav_filename, text_out))
                                wav_cut.export("{}/{}".format(self.project_name, new_wav_filename), format="wav")
                                index_count += 1
                                newline = '\n'

                            csv_file_temp.close()                        
                                        
                        else:
                            w = AudioSegment.from_wav(audio_name)
                            wav_cut = w[(beginning_cut*1000):(end_cut*1000)]
                            new_wav_filename =  "wavs/" + str(index_count) + ".wav"
                            new_csv_file.write("{}{}|{}".format(newline, new_wav_filename, text_out))
                            wav_cut.export("{}/{}".format(self.project_name, new_wav_filename), format="wav")
                            index_count += 1
                            newline = '\n'

                new_csv_file.close()
                set_value("label_build_status", "Building dataset done!")
                #Remove temporary directories
                shutil.rmtree("aeneas_prepped")
                shutil.rmtree("aeneas_out")
                print('\a') #system beep 
                print("Done with Aeneas!")


    def upload_blob(self, bucket_name, source_file_name, destination_blob_name):

        #storage_client = storage.Client.from_service_account_json(json_credentials_path='C:\TTS-corpus-builder\My First Project-b660c6889e30.json')
        storage_client = storage.Client()

        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(destination_blob_name)
        blob.upload_from_filename(source_file_name)
        #print("File {} uploaded to {}.".format(source_file_name, destination_blob_name))


    def diarization(self, wavfile, bucket_name, project_name):
        if not os.path.exists(project_name):
            os.mkdir(project_name)
        print("Uploading {} to google cloud storage bucket".format(wavfile))
        set_value("label_wav_file_transcribe", "Uploading file to cloud storage bucket...")    
        self.upload_blob(bucket_name, wavfile, "temp_audio.wav")
        gcs_uri = "gs://{}/temp_audio.wav".format(bucket_name)
        set_value("label_wav_file_transcribe", "Finished uploading.")    

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
            enable_word_time_offsets=True, 
            enable_speaker_diarization=True,
            diarization_speaker_count=int(get_value("input_diarization_num")),
        )

        operation = client.long_running_recognize(config=config, audio=audio)
        print("Waiting for operation to complete, this may take several minutes...")
        set_value("label_wav_file_transcribe", "Waiting for operation to complete, this may take several minutes...")    
        response = operation.result(timeout=28800)    

        result_array = []

        result = response.results[-1]
        words = result.alternatives[0].words     

        active_speaker = 1
        text = []
        transcript = []
        current_cut = 0
        previous_cut = 0
        speaker_wavs = []

        for x in range(int(get_value("input_diarization_num"))):
            speaker_wavs.append(AudioSegment.empty())
            transcript.append("")

        w = AudioSegment.from_wav(wavfile)

        for word in words:
            if word.speaker_tag == active_speaker:
                end_time = word.end_time                
                current_cut = end_time.total_seconds() * 1e3
                #print(current_cut)
                transcript[active_speaker-1] += word.word + ' '
            else:
                #speaker has changed
                transcript[active_speaker-1] += word.word + ' '
                w_cut = w[(previous_cut):current_cut]
                previous_cut = current_cut
                speaker_wavs[active_speaker-1] = speaker_wavs[active_speaker-1] + w_cut
                active_speaker = word.speaker_tag

        #finish last wav cut
        w_cut = w[previous_cut:current_cut]
        speaker_wavs[active_speaker-1] = speaker_wavs[active_speaker-1] + w_cut

        for i, wave in enumerate(speaker_wavs):
            speaker_wavs[i].export("{}/speaker_{}.wav".format(project_name, i+1), format="wav")

        for i, text in enumerate(transcript):
            f = open("{}/speaker_{}.txt".format(project_name, i+1), 'w')
            f.write(transcript[i])
            f.close()

        set_value("label_wav_file_transcribe", "Done!")   
        print("Done with diarization!")
        print('\a') #system beep 

