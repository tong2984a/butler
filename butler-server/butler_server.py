import os
import re
import pathlib
from werkzeug.utils import secure_filename
import subprocess
from flask import Flask, Response, make_response, request, send_file, jsonify
import butler_llama_langchain
#import torch
from TTS.api import TTS

app = Flask(__name__)

PHOTOS_FOLDER = pathlib.Path(app.instance_path, "media/photos")
PHOTOS_TMP_FOLDER = pathlib.Path(app.instance_path, "media/photos/tmp")
PHOTOS_TRANSCRIPTION_FOLDER = pathlib.Path(app.instance_path, "media/photos/transcription")

def ask(question):
    # Make sure the model path is correct for your system!
    # model_path = "/Users/aleung370/backup/work-startup/langchain-notes/local-llama-langchain/models/nous-hermes-13b.ggmlv3.q4_0.bin" # <-------- enter your model path here 
    model_path = "/home/aleung/langchain-notes/local-llama-langchain/models/llama-2-7b-chat.Q2_K.gguf"

    template = """Question: {question}

    Answer: """

    prompt = PromptTemplate(template=template, input_variables=["question"])

    # Callbacks support token-wise streaming
    callback_manager = CallbackManager([StreamingStdOutCallbackHandler()])


    n_gpu_layers = 40  # Change this value based on your model and your GPU VRAM pool.
    n_batch = 512  # Should be between 1 and n_ctx, consider the amount of VRAM in your GPU.

    # llm = LlamaCpp(
    #     model_path=model_path,
    #     n_gpu_layers=n_gpu_layers,
    #     n_batch=n_batch,
    #     callback_manager=callback_manager,
    #     verbose=True,
    #     # temperature=1
    # )

    # Uncomment the code below if you want to run inference on CPU
    llm = LlamaCpp(
        model_path=model_path, callback_manager=callback_manager, verbose=True
    )

    llm_chain = LLMChain(prompt=prompt, llm=llm)

    # question = "Tell me a random joke "

    return llm_chain.run(question)

def get_chunk(filename, byte1=None, byte2=None):
    filesize = os.path.getsize(filename)
    yielded = 0
    yield_size = 1024 * 1024

    if byte1 is not None:
        if not byte2:
            byte2 = filesize
        yielded = byte1
        filesize = byte2

    with open(filename, 'rb') as f:
        content = f.read()

    while True:
        remaining = filesize - yielded
        if yielded == filesize:
            break
        if remaining >= yield_size:
            yield content[yielded:yielded+yield_size]
            yielded += yield_size
        else:
            yield content[yielded:yielded+remaining]
            yielded += remaining

def generate_tts_audio(text, file_path):
    # Get device
    #device = "cuda" if torch.cuda.is_available() else "cpu"
    device = "cpu"
    #tts = TTS(model_name="tts_models/de/thorsten/tacotron2-DDC", progress_bar=False).to(device)
    #iwav = tts.tts("This is a test! This is also a test!!")
    # Init TTS with the target model name
    tts = TTS(model_name="tts_models/en/ljspeech/tacotron2-DDC", progress_bar=False).to(device)

    # Run TTS
    tts.tts_to_file(text=text, file_path=file_path)

    def generate(answer):
        print(answer)
        with open(file_path, "rb") as fwav:
            data = fwav.read(1024)
            while data:
                yield data
                data = fwav.read(1024)
    return generate(text)

@app.route('/transcribe_photo', methods = ['POST'])
def transcribe_photo():
    upload_file = request.files['photo file']
    filename = secure_filename(upload_file.filename) # save file 
    print('filename', filename)
    photo_file = os.path.join(PHOTOS_FOLDER, filename)
    upload_file.save(photo_file)
    tmp_file = os.path.join(PHOTOS_TMP_FOLDER, filename.replace(".jpg", ".tmp"))
    with open(tmp_file, 'w') as f:
        f.write("")
    p = subprocess.run(["/home/aleung/llama.cpp/llava", "-m", "/home/aleung/llama.cpp/models/llava/ggml-model-q4_k.gguf", "--mmproj", "/home/aleung/llama.cpp/models/llava/mmproj-model-f16.gguf", "--image", photo_file, "--temp", "0.1", "-p", "tell me the primary color in this photo"], capture_output=True, text=True)
    print(p.stdout)
    print(p.stderr)
    txt_file = os.path.join(PHOTOS_TRANSCRIPTION_FOLDER, filename.replace(".jpg", ".txt"))
    with open(txt_file, 'w') as f:
        f.write(p.stdout)
    return p.stdout

@app.route('/photo_transcription_status', methods = ['GET'])
def photo_transcription_status():
    filename = request.args.get('filename')
    if filename is None:
        return {'filename': "", 'status_ready': False, 'status_pending': False, 'status_has_photo': False}
    photo_file = os.path.join(PHOTOS_FOLDER, filename)
    txt_file = os.path.join(PHOTOS_TRANSCRIPTION_FOLDER, filename.replace(".jpg", ".txt"))
    tmp_file = os.path.join(PHOTOS_TMP_FOLDER, filename.replace(".jpg", ".tmp"))
    if os.path.exists(txt_file):
        return {'filename': photo_file, 'status_ready': True, 'status_pending': False, 'status_has_photo': False}
    elif os.path.exists(tmp_file):
        return {'filename': photo_file, 'status_ready': False, 'status_pending': True, 'status_has_photo': False}
    elif os.path.exists(photo_file):
        return {'filename': photo_file, 'status_ready': False, 'status_pending': False, 'status_has_photo': True}
    else:
        return {'filename': photo_file, 'status_ready': False, 'status_pending': False, 'status_has_photo': False}

@app.route('/photo_transcription', methods = ['GET'])
def photo_transcription():
    print('args', request.args)
    filename = request.args.get('filename')
    txt_file = os.path.join(PHOTOS_TRANSCRIPTION_FOLDER, filename.replace(".jpg", ".txt"))
    tmp_file = os.path.join(PHOTOS_TMP_FOLDER, filename.replace(".jpg", ".tmp"))
    if os.path.exists(txt_file):
        with open(txt_file, 'r') as f:
            text = f.read()
        paragraphs = text.split('\n\n')
        prompt_index = next((i for i, paragraph in enumerate(paragraphs) if paragraph.startswith('prompt:')), None)
        main_index = next((i for i, paragraph in enumerate(paragraphs) if paragraph.startswith('main:')), None)
        extracted_paragraphs = ""
        if prompt_index is not None and main_index is not None:
            extracted_paragraphs = '\n\n'.join(paragraphs[prompt_index+1:main_index])
        if len(extracted_paragraphs.strip()) == 0:
            os.remove(txt_file)
            os.remove(tmp_file)
            return "Cannot extract file content", 404
        OUTPUT_PATH="/home/aleung/transcribe.wav"
        audio_data = generate_tts_audio(extracted_paragraphs, OUTPUT_PATH)
        return Response(audio_data, mimetype="audio/x-wav", status=200)
    else:
        if os.path.exists(tmp_file):
            os.remove(tmp_file)
        return 'File not found', 404

@app.route("/video")
def video():
    filename = request.get_data().decode('UTF-8')
    filesize = os.path.getsize(filename)
    range_header = request.headers.get('Range', None)

    if range_header:
        byte1, byte2 = None, None
        match = re.search(r'(\d+)-(\d*)', range_header)
        groups = match.groups()

        if groups[0]:
            byte1 = int(groups[0])
        if groups[1]:
            byte2 = int(groups[1])

        if not byte2:
            byte2 = byte1 + 1024 * 1024
            if byte2 > filesize:
                byte2 = filesize

        length = byte2 + 1 - byte1

        resp = Response(
            get_chunk(filename, byte1, byte2),
            status=206, mimetype='video/mp4',
            content_type='video/mp4',
            direct_passthrough=True
        )

        resp.headers.add('Content-Range',
                         'bytes {0}-{1}/{2}'
                         .format(byte1,
                                 length,
                                 filesize))
        return resp

    return Response(
        get_chunk(filename),
        status=200, mimetype='video/mp4'
    )

@app.after_request
def after_request(response):
    response.headers.add('Accept-Ranges', 'bytes')
    return response

@app.route("/ask_llm")
def streamllm():
    print("ask llm")
    question = request.get_data().decode('UTF-8')
    print(question)
    answer = butler_llama_langchain.ask(question)
    # Get device
    #device = "cuda" if torch.cuda.is_available() else "cpu"
    device = "cpu"
    #tts = TTS(model_name="tts_models/de/thorsten/tacotron2-DDC", progress_bar=False).to(device)
    #iwav = tts.tts("This is a test! This is also a test!!")
    # Init TTS with the target model name
    tts = TTS(model_name="tts_models/en/ljspeech/tacotron2-DDC", progress_bar=False).to(device)

    # Run TTS
    OUTPUT_PATH="/home/aleung/answer.wav"
    tts.tts_to_file(text=answer, file_path=OUTPUT_PATH)

    def generate(answer):
        print(answer)
        with open(OUTPUT_PATH, "rb") as fwav:
            data = fwav.read(1024)
            while data:
                yield data
                data = fwav.read(1024)
    return Response(generate(answer), mimetype="audio/x-wav")

if __name__ == "__main__":
    app.run(debug=True)

