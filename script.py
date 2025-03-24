#for FramingDimensions
from sentence_transformers import SentenceTransformer
import os
import nltk
nltk.download('punkt')
from tqdm import tqdm
import pandas as pd

#imports for FramingLabels
import torch
from transformers import pipeline
from functools import partial
import numpy as np

dimensions = [
    "Care: ...acted with kindness, compassion, or empathy, or nurtured another person.",
    "Harm: ...acted with cruelty, or hurt or harmed another person/animal and caused suffering.",
    "Fairness: ...acted in a fair manner, promoting equality, justice, or rights.",
    "Cheating: ...was unfair or cheated, or caused an injustice or engaged in fraud.",
    "Loyalty: ...acted with fidelity, or as a team player, or was loyal or patriotic.",
    "Betrayal: ...acted disloyal, betrayed someone, was disloyal, or was a traitor.",
    "Authority: ...obeyed, or acted with respect for authority or tradition.",
    "Subversion: ...disobeyed or showed disrespect, or engaged in subversion or caused chaos.",
    "Sanctity: ...acted in a way that was wholesome or sacred, or displayed purity or sanctity.",
    "Degradation: ...was depraved, degrading, impure, or unnatural.",
]

pole_names = [
    ("Care", "Harm"),
    ("Fairness", "Cheating"),
    ("Loyalty", "Betrayal"),
    ("Authority", "Subversion"),
    ("Sanctity", "Degradation"),
]
base_model = "all-mpnet-base-v2"

candidate_labels = [
    "Economic: costs, benefits, or other financial implications",
    "Capacity and resources: availability of physical, human or financial resources, and capacity of current systems",
    "Morality: religious or ethical implications",
    "Fairness and equality: balance or distribution of rights, responsibilities, and resources",
    "Legality constitutionality and jurisprudence: rights, freedoms, and authority of individuals, corporations, and government",
    "Policy prescription and evaluation: discussion of specific policies aimed at addressing problems",
    "Crime and punishment: effectiveness and implications of laws and their enforcement",
    "Security and defense: threats to welfare of the individual, community, or nation",
    "Health and safety: health care, sanitation, public safety",
    "Quality of life: threats and opportunities for the individual’s wealth, happiness, and well-being",
    "Cultural identity: traditions, customs, or values of a social group in relation to a policy issue",
    "Public opinion: attitudes and opinions of the general public, including polling and demographics",
    "Political: considerations related to politics and politicians, including lobbying, elections, and attempts to sway voters",
    "External regulation and reputation: international reputation or foreign policy of the U.S."
    #drop the "other" label (zero shot classfication)
    #"Other: any coherent group of frames not covered by the above categories",
]


class FramingLabels:
    def __init__(self, base_model, candidate_labels, batch_size=16):
        device = "cuda:0" if torch.cuda.is_available() else "cpu"
        self.base_pipeline = pipeline("zero-shot-classification", model=base_model, device=device)
        self.candidate_labels = candidate_labels
        self.classifier = partial(self.base_pipeline, candidate_labels=candidate_labels, multi_label=True, batch_size=batch_size)

    def order_scores(self, dic):
        indices_order = [dic["labels"].index(l) for l in self.candidate_labels]
        scores_ordered = np.array(dic["scores"])[indices_order].tolist()
        return scores_ordered

    def get_ordered_scores(self, sequence_to_classify):
        if type(sequence_to_classify) == list:
            res = []
            for out in tqdm(self.classifier(sequence_to_classify)):
                res.append(out)
        else:
            res = self.classifier(sequence_to_classify)
        if type(res) == list:
            scores_ordered = list(map(self.order_scores, res))
            scores_ordered = list(map(list, zip(*scores_ordered)))  # reorder
        else:
            scores_ordered = self.order_scores(res)
        return scores_ordered

    def get_label_names(self):
        label_names = [l.split(":")[0].split(" ")[0] for l in self.candidate_labels]
        return label_names

    def __call__(self, sequence_to_classify):
        scores = self.get_ordered_scores(sequence_to_classify)
        label_names = self.get_label_names()
        return dict(zip(label_names, scores))


class FramingDimensions:
    def __init__(self, base_model, dimensions, pole_names):
        self.encoder = SentenceTransformer(base_model)
        self.dimensions = dimensions
        self.dim_embs = self.encoder.encode(dimensions, normalize_embeddings=True)
        self.pole_names = pole_names
        self.axis_names = list(map(lambda x: x[0] + "/" + x[1], pole_names))
        axis_embs = []
        for pole1, pole2 in pole_names:
            p1 = self.get_dimension_names().index(pole1)
            p2 = self.get_dimension_names().index(pole2)
            # ? should the embeddings already be normalized before subtraction?
            axis_emb = self.dim_embs[p1] - self.dim_embs[p2]
            # ! FIX: normalized the axis to have unit length
            axis_emb = axis_emb / np.linalg.norm(axis_emb)
            axis_embs.append(axis_emb)
        self.axis_embs = np.stack(axis_embs)

    def get_dimension_names(self):
        dimension_names = [l.split(":")[0].split(" ")[0] for l in self.dimensions]
        return dimension_names

    def __call__(self, sequence_to_align):
        embs = self.encoder.encode(sequence_to_align, normalize_embeddings=True)
        scores = embs @ self.axis_embs.T
        named_scores = dict(zip(self.pole_names, scores.T))
        return named_scores


framing_labels = FramingLabels("facebook/bart-large-mnli", candidate_labels)
framing_dimensions = FramingDimensions(
    base_model, dimensions, pole_names
)

def tokenizeArticles(articles):
    tokenized_articles = []
    for article in articles:
        try:
            tokenized_articles.append(nltk.sent_tokenize(article))
        except Exception as e:
            print(f"Tokenization error:\n{e}")
            continue
    print(f"Tokenized {len(articles)} articles.")
    return tokenized_articles

def preprocessArticles(directories_to_frame):
    articles = []
    article_names = []
    folder_name = []
    for i, directory in enumerate(directories_to_frame):
        for filename in os.listdir(directory):
            file_path = os.path.join(directory, filename)
            with open(file_path, errors="ignore") as file:
                articles.append(file.read())
                article_names.append(filename)
                folder_name.append(directory.split("\\")[-1])
    print(f"Found {len(articles)} articles.")
    articles = tokenizeArticles(articles)
    return articles, article_names, folder_name

def listFolders(directories):
    folder_paths = []
    for directory in directories:
        for root, dirs, files in os.walk(directory):
            if not dirs:
                folder_name = os.path.basename(root)
                folder_paths.append(root)
    return folder_paths


def frame(articles, article_names, folder_name,dump_path="COP/"):
    os.makedirs(dump_path + "/dimensions/", exist_ok=True)
    for name in folder_name:
        os.makedirs(dump_path + "/dimensions/"+ name, exist_ok=True)
    os.makedirs(dump_path + "/labels/", exist_ok=True)
    for name in folder_name:
        os.makedirs(dump_path + "/labels/"+ name, exist_ok=True)

    print("Computing frame dimensions and labels")
    for i, article in enumerate(tqdm(articles, desc="Framing articles\n")):
        print(article_names[i])
        try:
            dimension = framing_dimensions(article)
            dimension_df = pd.DataFrame(dimension)
            dimension_df.to_csv(
                f"{dump_path}/dimensions/{folder_name[i]}/{article_names[i].split(".")[0]}_dimensions.csv", index=False
            )
            labels = framing_labels(article)
            labels_df = pd.DataFrame(labels)
            labels_df.to_csv(
                f"{dump_path}/labels/{folder_name[i]}/{article_names[i].split(".")[0]}_label.csv", index=False
            )
        except Exception as e:
            print(f"Article: {article_names[i]} could not be framed.\n{e}")
            continue


if __name__ == "__main__":
    directories_to_frame = ["COP/articles/by_org"]
    directories_to_frame = listFolders(directories_to_frame)
    articles, article_names, folder_name = preprocessArticles(directories_to_frame)
    frame(articles,article_names,folder_name,dump_path="COP/")
