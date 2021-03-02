from dearpygui.core import *
from dearpygui.simple import *
import math
import os
import ntpath
from pydub import AudioSegment
import csv
import argparse
import numpy as np
import re

class Project:
    def __init__(self, project_name, speaker_text_path, wav_file_path, index_start, cut_length, contains_punc):    
        self.project_name = project_name
        self.speaker_text_path = speaker_text_path
        self.wav_file_path = wav_file_path
        self.index_start = index_start
        self.cut_length = cut_length
        self.contains_punc = contains_punc

    def build_dataset(self):
        output_wav_path = "{}_wavs/".format(self.project_name)
        if not os.path.exists(output_wav_path):
            os.mkdir(output_wav_path)      
        if not os.path.exists("aeneas_out"):
            os.mkdir("aeneas_out")
        if not os.path.exists("aeneas_prepped"):
            os.mkdir("aeneas_prepped")
        if not os.path.exists("csv_out"):
            os.mkdir("csv_out")   

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
            new_csv_file = open('csv_out/output.csv', 'w')
            
            with open('aeneas_out/' + self.project_name + '.csv', 'r') as csv_file:
                
                index_count = int(self.index_start)
                csv_reader = csv.reader(csv_file, delimiter=',')
                csv_reader = list(csv_reader) #convert to list
                row_count = len(csv_reader) 
            
                newline = ''                      
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
                            new_csv_file.write("{}{}{}|{}".format(newline, output_wav_path, new_wav_filename, text_out))
                            wav_cut.export(output_wav_path + new_wav_filename, format="wav")
                            index_count += 1
                            newline = '\n'

                        csv_file_temp.close()
                        
                                    
                    else:
                        w = AudioSegment.from_wav(audio_name)
                        wav_cut = w[(beginning_cut*1000):(end_cut*1000)]
                        new_wav_filename =  str(index_count) + ".wav"
                        new_csv_file.write("{}{}{}|{}".format(newline, output_wav_path, new_wav_filename, text_out))
                        wav_cut.export(output_wav_path + new_wav_filename, format="wav")
                        index_count += 1
                        newline = '\n'

            new_csv_file.close()


def open_speaker_txt_file_callback(sender, data):
    open_file_dialog(add_speaker_txt_file)

def open_wav_file_callback(sender, data):
    open_file_dialog(add_speaker_wav_file)    
   
def run_dataset_builder_callback(sender, data):
    #check to see if txt and wav file was selected
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

set_theme("Gold")

with window("mainWin"):

    with tab_bar("tb1"):

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
            add_checkbox("input_contains_punc", default_value=0, label="")                         
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



        with tab("tab2", label="Proofread Corpus"):
            add_spacing(count=5)
            add_text("Choose a csv file to proofread and edit wavs")

        with tab("tab3", label="Shift Corpus"):
            add_spacing(count=5)
            


start_dearpygui(primary_window="mainWin")