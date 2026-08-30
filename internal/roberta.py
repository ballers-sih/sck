import os
import sys
import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer
from internal import parse_eml

MODEL = os.environ["ROBERTA_MODEL"]

tokenizer = AutoTokenizer.from_pretrained(MODEL)
model = AutoModelForSequenceClassification.from_pretrained(MODEL)
model.eval()


def scan_email(subject: str, body: str) -> dict:
    text = f"Subject: {subject}\n\n{body}"

    inputs = tokenizer(
        text,
        return_tensors="pt",
        max_length=512,
        truncation=True,
        padding=True,
    )

    with torch.no_grad():
        outputs = model(**inputs)
        probabilities = torch.softmax(outputs.logits, dim=-1)[0]

    fraud_probability = probabilities[1].item()
    normal_probability = probabilities[0].item()

    return {
        "fraud": fraud_probability >= 0.5,
        "fraud_probability": fraud_probability,
        "normal_probability": normal_probability,
    }


def main():
    path = sys.argv[1]
    with open(path, "rb") as file:
        data = file.read()
    email = parse_eml.parse_eml(data)
    print(scan_email(email.subject, email.message))


if __name__ == "__main__":
    main()
