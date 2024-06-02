from transformers import AutoFeatureExtractor, ASTForAudioClassification

# from datasets import load_dataset
import torch
import librosa

import glob

from tqdm import tqdm
import plotly.express as px

feature_extractor = AutoFeatureExtractor.from_pretrained(
    "MIT/ast-finetuned-audioset-10-10-0.4593"
)
model = ASTForAudioClassification.from_pretrained(
    "MIT/ast-finetuned-audioset-10-10-0.4593"
)

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
device

import os

xingu_path = (
    "G:\\.shortcut-targets-by-id\\1Om1xrl8GrY7dADTjuyuKQ6uWkpaLUFCt\\Audio\\Xingu"
)

xingu_subpaths = [
    os.path.join(xingu_path, subpath) + "\\" for subpath in os.listdir(xingu_path)
]


xingu_subpaths

all_audio_paths = [
    #'D:\\hackathon\\primary1 - including ultrasonic\\',
    "D:\\hackathon\\primary2 - including ultrasonic\\",
    "G:\\.shortcut-targets-by-id\\1Om1xrl8GrY7dADTjuyuKQ6uWkpaLUFCt\\Audio\\Ingles\\landing - including ultrasonic\\",
    "G:\\.shortcut-targets-by-id\\1Om1xrl8GrY7dADTjuyuKQ6uWkpaLUFCt\\Audio\\Ingles\inn2\\",
    "G:\\.shortcut-targets-by-id\\1Om1xrl8GrY7dADTjuyuKQ6uWkpaLUFCt\\Audio\\Ingles\\inn3\\",
    "G:\\.shortcut-targets-by-id\\1Om1xrl8GrY7dADTjuyuKQ6uWkpaLUFCt\\Audio\\ParqueDasTribos\\parque das Tribos\\",
    "G:\\.shortcut-targets-by-id\\1Om1xrl8GrY7dADTjuyuKQ6uWkpaLUFCt\\Audio\\\Inhaa-Be\\Inhaa-Be Audiomoth 1\\",
    "G:\\.shortcut-targets-by-id\\1Om1xrl8GrY7dADTjuyuKQ6uWkpaLUFCt\\Audio\\\Inhaa-Be\\Inhaa-Be Audiomoth 2\\",
] + xingu_subpaths

import os
import pandas as pd

sampling_rate = 16000


window_rate = 5  # seconds
window_size = 10  # seconds

for path in all_audio_paths:

    LIMIT = -1

    # path_to_audio = path
    paths_to_audio = glob.glob(path + "*.wav")

    print("Processing", path)

    inputs = []

    filenames = []

    res_list = []

    json_data = {}

    results = []

    model = model.to(device)

    test_df = {"filename": [], "start_time": [], "end_time": [], "result": []}

    for path_to_audio in tqdm(paths_to_audio):
        if LIMIT == 0:
            break
        LIMIT -= 1

        try:
            filename = path_to_audio.split("\\")[-1]
            filenames.append(filename)

            # filenames.append(filename)
            y, s = librosa.load(path_to_audio, sr=16000)

            y_split = [
                y[i : i + sampling_rate * window_size]
                for i in range(0, len(y), sampling_rate * window_rate)
            ]

            input = [
                feature_extractor(
                    snippet, sampling_rate=sampling_rate, return_tensors="pt"
                )["input_values"]
                for snippet in y_split
            ]
            # print(input,input.shape)
            input = torch.cat(input, dim=0)

            input = input.to(device)

            pred = []
            print(input.shape)
            with torch.no_grad():
                logits = model(input).logits
            result = torch.nn.functional.softmax(logits, dim=-1).tolist()

            sorted_indexes = torch.argsort(logits, dim=-1, descending=True)
            prediction = []
            for j in range(logits.shape[0]):

                predicted_labels = [
                    (model.config.id2label[index], format(result[j][index], ".5f"))
                    for index in sorted_indexes[j].tolist()[:100]
                ]
                result_dict = {k: v for k, v in predicted_labels}

                p = [
                    (index, format(result[j][index], ".5f"))
                    for index in sorted_indexes[j].tolist()[:200]
                ]
                prediction.append(predicted_labels[0])
                # res_list.append({"start_time":j*window_rate,"end_time":j*window_rate+window_size,"result":result[j]})
                test_df["filename"].append(filename)
                test_df["start_time"].append(j * window_rate)
                test_df["end_time"].append(j * window_rate + window_size)
                test_df["result"].append([format(r, ".5f") for r in result[j]])
                pred.append(p)

        except Exception as e:
            print(e)
            continue

        # print(res_list)
        # print(filenames[i],prediction)
        ##json_data[filename] = res_list
        # results.append(prediction)
        # inputs.append(input)

    # inputs = torch.cat(inputs,dim=0)

    # print(len(inputs),inputs[0].shape)

    # json_data

    test_df = pd.DataFrame(test_df)

    folder_name = path.split("\\")[-2]

    test_df.to_csv(f"results_AST_{folder_name}.csv")
