
import os
import ntpath
from pydub import AudioSegment
import csv
import argparse
import numpy as np

def trim(input_csv, input_wav_path, min_length):
    
    if not os.path.exists("csv_out"):
        os.mkdir("csv_out")   

    input_csv_no_ext = os.path.splitext(input_csv)[0]    
    csv_new = open(f"csv_out/{input_csv_no_ext}_trimmed.csv", 'w')

    with open(input_csv, 'r') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter='|')
        for row in csv_reader: 
            #wav_filename should include path to wav file
            wav_filename_with_path = row[0] 
            text = row[1]
            if os.path.exists(wav_filename_with_path):
                w = AudioSegment.from_wav(wav_filename_with_path)
                wav_length = w.duration_seconds
                if wav_length > min_length:
                    csv_new.write(f"{wav_filename_with_path}|{text}\n")
                else:
                    print(f"{wav_filename_with_path} too short, being removed")
                    os.remove(wav_filename_with_path)
            else:
                print(f"Wav file {wav_filename_with_path} already removed")


    print("Done")
    csv_new.close()

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-csv', '--csv_file', type=str,
                        help='csv filepath') 
    parser.add_argument('-input_wav_path', '--input_wav_path', type=str, default="wavs/",
                        help='input wav path, ex. wavs/') 
    parser.add_argument('-min_length', '--min_length', type=float, default=1.0,
                        help='min wav file length in float seconds')                         
    args = parser.parse_args()

    trim(args.csv_file, args.input_wav_path, args.min_length)
