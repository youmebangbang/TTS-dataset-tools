
import os
import ntpath
from pydub import AudioSegment
import csv
import argparse
import numpy as np
import re

def splitter(input_csv, input_wav_path, output_wav_path):
    
    if not os.path.exists("aeneas_prepped"):
        os.mkdir("aeneas_prepped")
    if not os.path.exists("aeneas_out"):
        os.mkdir("aeneas_out") 
    if not os.path.exists(output_wav_path):
        os.mkdir(output_wav_path)
    if not os.path.exists("csv_out"):
        os.mkdir("csv_out")         
    
    with open(input_csv, 'r') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter='|')

        for row in csv_reader: 
            #wav_filename should include path to wav file
            wav_filename_with_path = row[0] 
            wav_filename_no_path = ntpath.basename(wav_filename_with_path)
            wav_filename_no_ext = os.path.splitext(wav_filename_no_path)[0]

            text = row[1]
 
            if not text:
                print("Missing text in file " + wav_filename)
                exit()
                
            #break the sentence into aeneas ready text
            phrase_splits = re.split(r'(?<=[\,\.\!\?])\s*', text)   #split on white space              
            phrase_splits = list(filter(None, phrase_splits))  #remove empty splits     

            print(phrase_splits)            
            
            #save file of separated phrases
            # check if wave file does not exist but is represented in csv...    
            if os.path.exists(wav_filename_with_path):
                with open('aeneas_prepped/' + wav_filename_no_ext, 'w') as f:
                    newline = ''
                    for s in phrase_splits: 
                        if s:   #end of regex list may be empty
                            stripped = s.strip()   #remove whitespace                        
                            f.write(newline + stripped) 
                            newline = '\n'                
                #build aeneas timestampped csv files from prepped text 
                #create cuts with 50% of space between each                      
                os.system('python -m aeneas.tools.execute_task ' + wav_filename_with_path  + ' aeneas_prepped/' + wav_filename_no_ext + ' "task_adjust_boundary_percent_value=50|task_adjust_boundary_algorithm=percent|task_language=en|is_text_type=plain|os_task_file_format=csv" ' + 'aeneas_out/' + wav_filename_no_ext + '.csv')
            else:
                print(wav_filename + ".wav" + " missing")
                exit()

              
    #begin splitting
    
    input_csv_no_ext = os.path.splitext(input_csv)[0]
    new_csv_file = open("csv_out/" + input_csv_no_ext + "_new.csv", 'w')
    newline = ''      
    index_count = 0

    for file in os.scandir('aeneas_out'):
        
        with open(file, 'r') as csv_file:
            print("file number " + file.name)
            csv_reader = csv.reader(csv_file, delimiter=',')
            csv_reader = list(csv_reader) #convert to list
            row_count = len(csv_reader)
            # csv_file.seek(0)    #reset list pointer
                        
            file_name_no_ext = os.path.splitext(file.name)[0]   
            combined_text = ""                          

            if row_count > 1:    

                for r in range(0, row_count):   
                    #output new wav files of cuts
                    row = csv_reader[r]

                    beginning_cut = float(row[1])
                    end_cut = float(row[2])
                    text_out = row[3]
                    text_out = text_out.strip()  

                    if r > 0:
                        w = AudioSegment.from_wav(input_wav_path + file_name_no_ext + ".wav")
                        wav_cut = w[(beginning_cut*1000):(end_cut*1000)]
                        new_wav_filename = input_csv_no_ext + "_" + str(index_count) + ".wav"
                        wav_cut.export(output_wav_path + new_wav_filename, format="wav")

                        #build new csv file for text
                        new_csv_file.write("{}{}{}|{}".format(newline, output_wav_path, new_wav_filename, text_out))
                        index_count += 1   
                        print(text_out)

                        if r < row_count - 1:
                            #ouput a combined line from start of wav
                            combined_text = combined_text + " " + text_out
                            wav_cut = w[:(end_cut*1000)]
                            new_wav_filename = input_csv_no_ext + "_" + str(index_count) + ".wav"
                            wav_cut.export(output_wav_path + new_wav_filename, format="wav")

                            #build new csv file for text
                            combined_text = combined_text.strip()
                            new_csv_file.write("{}{}{}|{}".format(newline, output_wav_path, new_wav_filename, combined_text))

                            newline = '\n'    
                            index_count += 1 
                            print(combined_text)

                    else:
                        w = AudioSegment.from_wav(input_wav_path + file_name_no_ext + ".wav")
                        wav_cut = w[(beginning_cut*1000):(end_cut*1000)]
                        new_wav_filename = input_csv_no_ext + "_" + str(index_count) + ".wav"
                        wav_cut.export(output_wav_path + new_wav_filename, format="wav")

                        #build new csv file for text
                        new_csv_file.write("{}{}{}|{}".format(newline, output_wav_path, new_wav_filename, text_out))
                        newline = '\n'    
                        index_count += 1 
                        print(text_out)
                        combined_text = text_out                 

            else:
                print("nothing to split, skipping file")

    new_csv_file.close()

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-csv', '--csv_file', type=str,
                        help='csv filepath') 
    parser.add_argument('-output_wav_path', '--output_wav_path', type=str, default="wavs_out/",
                        help='output wav path, ex. outwavs/') 
    parser.add_argument('-input_wav_path', '--input_wav_path', type=str, default="wavs/",
                        help='input wav path, ex. wavs/') 
    args = parser.parse_args()

    splitter(args.csv_file, args.input_wav_path, args.output_wav_path)
