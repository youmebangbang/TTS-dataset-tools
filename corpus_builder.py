import aeneas
import os
import ntpath
from pydub import AudioSegment
import csv
import argparse
import re
import math

def build(input_text, audio_name, output_wav_path, cut_length, index_start):
    
    if not os.path.exists(output_wav_path):
        os.mkdir(output_wav_path)      
    if not os.path.exists("aeneas_out"):
        os.mkdir("aeneas_out")
    if not os.path.exists("aeneas_prepped"):
        os.mkdir("aeneas_prepped")
    if not os.path.exists("csv_out"):
        os.mkdir("csv_out")   
    audio_name_no_ext = os.path.splitext(audio_name)[0]
 

    with open(input_text, 'r', encoding="utf8") as f:
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
        #remove any duplicate whitespace between words
        text = " ".join(text.split())

        phrase_splits = re.split(r'(?<=[\.\!\?])\s*', text)   #split on white space between sentences             
        phrase_splits = list(filter(None, phrase_splits))  #remove empty splits
        with open('aeneas_prepped/split_text', 'w') as f:
                newline = ''
                for s in phrase_splits: 
                    if s:   
                        stripped = s.strip()   #remove whitespace                        
                        f.write(newline + stripped) 
                        newline = '\n'          
        os.system('python -m aeneas.tools.execute_task ' + audio_name  + ' aeneas_prepped/split_text "task_adjust_boundary_percent_value=50|task_adjust_boundary_algorithm=percent|task_language=en|is_text_type=plain|os_task_file_format=csv" ' + 'aeneas_out/' + audio_name_no_ext + '.csv')

        new_csv_file = open('csv_out/output.csv', 'w')

        with open('aeneas_out/' + audio_name_no_ext + '.csv', 'r') as csv_file:
            
            index_count = index_start
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

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-input_text', '--input_text', type=str,
                        help='name of input text file') 
    parser.add_argument('-audio_name', '--audio_name', type=str,
                        help='name of audio file to split')                         
    parser.add_argument('-output_wav_path', '--output_wav_path', type=str, default="wavs/",
                        help='output wav path, ex. outwavs/') 
    parser.add_argument('-cut_length', '--cut_length', type=float, default=12,
                        help='float max length of cuts, default 12sec')                        
    parser.add_argument('-index_start', '--index_start', type=int, default=0,
                        help='index number to start from, not 0 if continuing set')      
    args = parser.parse_args()

    build(args.input_text, args.audio_name, args.output_wav_path, args.cut_length, args.index_start)
