import math
import os
import ntpath
from pydub import AudioSegment
import csv
import argparse
import numpy as np
import re

def shifter(input_csv, input_wav_path, output_wav_path, index_start):
    
    if not os.path.exists("aeneas_prepped"):
        os.mkdir("aeneas_prepped")
    if not os.path.exists("aeneas_out"):
        os.mkdir("aeneas_out") 
    if not os.path.exists(output_wav_path):
        os.mkdir(output_wav_path)
    if not os.path.exists("csv_out"):
        os.mkdir("csv_out")         
    
    new_csv_file = open('csv_out/output.csv', 'w')
    newline = ""

    with open(input_csv, 'r') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter='|')

        first_entry = True
        index_count = index_start
        split_current = ["",""]
        split_previous = ["",""]
        wav_split_current = [0,0]
        wav_split_previous = [0,0]

        for row in csv_reader:             
            wav_filename_with_path = row[0] + ".wav" 
            wav_filename_no_path = ntpath.basename(wav_filename_with_path)
            wav_filename_no_ext = os.path.splitext(wav_filename_no_path)[0]
            wav_filename_with_input_path = input_wav_path + wav_filename_no_path
            text = row[1]
 
            if not text:
                print("Missing text in file " + input_csv)
                exit()

            if(first_entry):
                first_entry = False
                #Split sentence in half
                sentence_splits_bywhitespace = text.split()
                sen_len = len(sentence_splits_bywhitespace)
                split_point = math.floor(sen_len/2)
                print(f"split point of sentence is {split_point}\n")
                x = 0
                sentence_firsthalf_splits = []
                while x < split_point:
                    sentence_firsthalf_splits.append(sentence_splits_bywhitespace.pop(0))
                    x += 1

                split_current[0] = " ".join(sentence_firsthalf_splits)
                split_current[1] =  " ".join(sentence_splits_bywhitespace[:(sen_len-split_point)])

                print(f"first half: {split_current[0]}")
                print(f"second half: {split_current[1]}")           
        
                print(wav_filename_with_input_path)
               
                # check if wave file does not exist but is represented in csv...    
                if os.path.exists(wav_filename_with_input_path): 
                    #process both halves 
                                                     
                    with open('aeneas_prepped/' + wav_filename_no_ext, 'w') as f:                                                                   
                        f.write(split_current[0] + "\n")                                
                        f.write(split_current[1])
                    #build aeneas timestampped csv files from prepped text 
                    #create cuts with 50% of space between each                      
                    os.system('python -m aeneas.tools.execute_task ' + wav_filename_with_input_path  + ' aeneas_prepped/' + wav_filename_no_ext + ' "task_adjust_boundary_percent_value=50|task_adjust_boundary_algorithm=percent|task_language=en|is_text_type=plain|os_task_file_format=csv" ' + 'aeneas_out/' + wav_filename_no_ext + '.csv')
                    
                else:
                    print(wav_filename_with_input_path + " missing")
                    exit()    
    
                with open("aeneas_out/" + wav_filename_no_ext + ".csv", 'r') as csv_file:
                    csv_reader = csv.reader(csv_file, delimiter=',')
                    csv_reader = list(csv_reader) #convert to list
                    
                    first_half = csv_reader[0]
                    second_half = csv_reader[1]

                    first_half_beginning_cut = float(first_half[1])
                    first_half_end_cut = float(first_half[2])              
                    second_half_beginning_cut = float(second_half[1])
                    second_half_end_cut = float(second_half[2])

                    w = AudioSegment.from_wav(wav_filename_with_input_path)
                    wav_split_current[0] = w[(first_half_beginning_cut*1000):(first_half_end_cut*1000)]
                    new_wav_filename = str(index_count)
                    index_count += 1
                    wav_split_current[0].export(output_wav_path + new_wav_filename + ".wav", format="wav")
                    wav_split_current[1] = w[(second_half_beginning_cut*1000):(second_half_end_cut*1000)]

                new_csv_file.write("{}{}|{}".format(newline, new_wav_filename, split_current[0]))
                newline = '\n'    

                wav_split_previous[1] = wav_split_current[1]
                split_previous[1] = split_current[1]

            else:
                #after first entry
                #Split sentence in half
                sentence_splits_bywhitespace = text.split()
                sen_len = len(sentence_splits_bywhitespace)
                split_point = math.floor(sen_len/2)
                print(f"split point of sentence is {split_point}\n")
                x = 0
                sentence_firsthalf_splits = []
                while x < split_point:
                    sentence_firsthalf_splits.append(sentence_splits_bywhitespace.pop(0))
                    x += 1

                split_current[0] = " ".join(sentence_firsthalf_splits)
                split_current[1] =  " ".join(sentence_splits_bywhitespace[:(sen_len-split_point)])

                print(f"first half: {split_current[0]}")
                print(f"second half: {split_current[1]}")           
        
                print(wav_filename_with_input_path)
               
                # check if wave file does not exist but is represented in csv...    
                if os.path.exists(wav_filename_with_input_path): 
                    #process both halves 
                                           
                    with open('aeneas_prepped/' + wav_filename_no_ext, 'w') as f:                                                                   
                        f.write(split_current[0] + "\n")                                
                        f.write(split_current[1])
                    #build aeneas timestampped csv files from prepped text 
                    #create cuts with 50% of space between each                      
                    os.system('python -m aeneas.tools.execute_task ' + wav_filename_with_input_path  + ' aeneas_prepped/' + wav_filename_no_ext + ' "task_adjust_boundary_percent_value=50|task_adjust_boundary_algorithm=percent|task_language=en|is_text_type=plain|os_task_file_format=csv" ' + 'aeneas_out/' + wav_filename_no_ext + '.csv')
                    
                else:
                    print(wav_filename_with_input_path + " missing")
                    exit()    
    
                with open("aeneas_out/" + wav_filename_no_ext + ".csv", 'r') as csv_file:
                    csv_reader = csv.reader(csv_file, delimiter=',')
                    csv_reader = list(csv_reader) #convert to list
                    
                    first_half = csv_reader[0]
                    second_half = csv_reader[1]

                    first_half_beginning_cut = float(first_half[1])
                    first_half_end_cut = float(first_half[2])              
                    second_half_beginning_cut = float(second_half[1])
                    second_half_end_cut = float(second_half[2])

                    #create silence to mend wav files together
                    punc_silence = AudioSegment.silent(duration=200)
                    word_silence = AudioSegment.silent(duration=10)

                    w = AudioSegment.from_wav(wav_filename_with_input_path)
                    wav_split_current[0] = w[(first_half_beginning_cut*1000):(first_half_end_cut*1000)]
                    new_wav_filename = str(index_count)
                    index_count += 1

                    if split_previous[1].endswith((',', '.', '!', '?')):
                        print("adding punctuation length silence \n")
                        new_wav = wav_split_previous[1] + punc_silence + wav_split_current[0]
                    else:
                        new_wav = wav_split_previous[1] + word_silence + wav_split_current[0]

                    new_wav.export(output_wav_path + new_wav_filename + ".wav", format="wav")
                    wav_split_current[1] = w[(second_half_beginning_cut*1000):(second_half_end_cut*1000)]

                split_out = " ".join([split_previous[1].strip(), split_current[0].strip()])
                new_csv_file.write("{}{}|{}".format(newline, new_wav_filename, split_out))
                newline = '\n'   
                wav_split_previous[1] = wav_split_current[1]
                split_previous[1] = split_current[1]                         

    new_csv_file.close()

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-csv', '--csv_file', type=str,
                        help='csv filepath') 
    parser.add_argument('-output_wav_path', '--output_wav_path', type=str, default="wavs_out/",
                        help='output wav path, ex. outwavs/') 
    parser.add_argument('-input_wav_path', '--input_wav_path', type=str, default="wavs/",
                        help='input wav path, ex. wavs/') 
    parser.add_argument('-index_start', '--index_start', type=int, default="1",
                        help='index number to start on')                         
    args = parser.parse_args()

    shifter(args.csv_file, args.input_wav_path, args.output_wav_path, args.index_start)
