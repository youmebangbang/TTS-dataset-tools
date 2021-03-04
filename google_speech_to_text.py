import io
import math
from pydub import AudioSegment
from google.cloud import storage
from google.cloud import speech as speech

#client = storage.Client.from_service_account_json(json_credentials_path='C:\TTS-corpus-builder\My First Project-b660c6889e30.json')

def upload_blob(bucket_name, source_file_name, destination_blob_name):

    storage_client = storage.Client.from_service_account_json(json_credentials_path='C:\TTS-corpus-builder\My First Project-b660c6889e30.json')
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)
    blob.upload_from_filename(source_file_name)
    print("File {} uploaded to {}.".format(source_file_name, destination_blob_name))


def transcribe_file(wavfile):
    print("Uploading {} to google cloud storage bucket".format(wavfile))
    #upload_blob("youmebangbang_bucket", wavfile, "temp_audio.wav")
    gcs_uri = "gs://youmebangbang_bucket/temp_audio.wav"

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

    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=16000,
        language_code="en-US",
        enable_automatic_punctuation=True,
    )

    operation = client.long_running_recognize(config=config, audio=audio)

    print("Waiting for operation to complete, this may take several minutes...")
    response = operation.result(timeout=28800)    

        # for word_info in words_info:
        #     print(u"word: '{}', speaker_tag: {}".format(word_info.word, word_info.speaker_tag))
        #     f.write(newline + str(word_info.word) + " " + str(word_info.speaker_tag))
        #     newline = '\n'

    result_array = []
    #word_info_array = []
    with open ("output.txt", 'a') as f:   
        for result in response.results:            
            result_array.append(result.alternatives[0].transcript)
            #word_info_array.append(result.alternatives[0].words)
            
            print("Transcript: {}".format(result.alternatives[0].transcript))
            #print("Confidence: {}".format(result.alternatives[0].confidence))
        newline = ""
        for x in range(0, len(result_array)-1):             
            f.write(newline + result_array[x])
            newline = '\n'

transcribe_file("beastinfection.wav")
