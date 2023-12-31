import torch
import transformers
import json
import csv
from tqdm.auto import tqdm
from transformers import pipeline
from transformers import (
    CONFIG_MAPPING,
    MODEL_MAPPING,
    AutoConfig,
    AutoModelForMultipleChoice,
    AutoModelForQuestionAnswering,
    AutoTokenizer,
    DataCollatorWithPadding,
    EvalPrediction,
    SchedulerType,
    default_data_collator,
    get_scheduler,
)
import sys

context_file_dir = sys.argv[1]
test_file_dir = sys.argv[2]
output_file_dir = sys.argv[3]
mc_model_dir = sys.argv[4]
qa_model_dir = sys.argv[5]

# with open("data/context.json", "r") as f:
with open(context_file_dir, "r") as f:
    context_file = json.load(f)

# with open("data/test.json", "r") as f:
with open(test_file_dir, "r") as f:
    test_file = json.load(f)

# file = open("mbl_n2.csv", 'w', newline='')
file = open(output_file_dir, 'w', newline='')
output_file = csv.writer(file)
output_file.writerow(["id","answer"])

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"device: {device}")
## multiple choice
tokenizer = AutoTokenizer.from_pretrained(mc_model_dir)
model = AutoModelForMultipleChoice.from_pretrained(mc_model_dir).to(device)
model.eval()


prompt = []
candidate = []
for ques in test_file:
    prompt.append(ques["question"])
    context = []
    for para in ques["paragraphs"]:
        context.append(context_file[para])
    candidate.append(context)
it = len(prompt)
# it = 10
# turn on evaluation mode for inference
prediction = []
for i in tqdm(range(it)):
    input = []
    for j in range(4):
        input.append([prompt[i], candidate[i][j]])
    inputs = tokenizer(input, return_tensors="pt", padding=True, truncation=True, max_length=512)
    labels = torch.tensor(0).unsqueeze(0).to(device)
    outputs = model(**{k: v.unsqueeze(0).to(device) for k, v in inputs.items()}, labels=labels)
    logits = outputs.logits
    predicted_class = logits.argmax().item()
    # print(candidate[i][predicted_class])
    prediction.append(candidate[i][predicted_class])

## question answer
from transformers import pipeline

question_answerer = pipeline("question-answering", model=qa_model_dir, device=0)
for i in tqdm(range(it)):
    str = question_answerer(question=prompt[i], context=prediction[i])["answer"]
    # print([test_file[i]["id"], str])
    output_file.writerow([test_file[i]["id"], str])

file.close()