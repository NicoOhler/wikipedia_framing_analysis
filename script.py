import pandas as pd
import matplotlib.pyplot as plt
import nltk
import os
from framefinder import framedimensions
from framefinder import framelabels
from sentence_transformers import SentenceTransformer
from tqdm import tqdm
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
    "Degredation: ...was depraved, degrading, impure, or unnatural.",
]
pole_names = [
    ("Care", "Harm"),
    ("Fairness", "Cheating"),
    ("Loyalty", "Betrayal"),
    ("Authority", "Subversion"),
    ("Sanctity", "Degredation"),
]
base_model = 'all-mpnet-base-v2'

candidate_labels = [
    "Economic: costs, benefits, or other financial implications",
    "Capacity and resources: availability of physical, human or financial resources, and capacity of current systems",
    "Morality: religious or ethical implications",
    "Fairness and equality: balance or distribution of rights, responsibilities, and resources",
    "Legality, constitutionality and jurisprudence: rights, freedoms, and authority of individuals, corporations, and government",
    "Policy prescription and evaluation: discussion of specific policies aimed at addressing problems",
    "Crime and punishment: effectiveness and implications of laws and their enforcement",
    "Security and defense: threats to welfare of the individual, community, or nation",
    "Health and safety: health care, sanitation, public safety",
    "Quality of life: threats and opportunities for the individual’s wealth, happiness, and well-being",
    "Cultural identity: traditions, customs, or values of a social group in relation to a policy issue",
    "Public opinion: attitudes and opinions of the general public, including polling and demographics",
    "Political: considerations related to politics and politicians, including lobbying, elections, and attempts to sway voters",
    "External regulation and reputation: international reputation or foreign policy of the U.S.",
    "Other: any coherent group of frames not covered by the above categories",
]

framing_labels = framelabels.FramingLabels("facebook/bart-large-mnli", candidate_labels)
framing_dimensions = framedimensions.FramingDimensions(base_model, dimensions, pole_names)

def listFolders(directories):
    folder_names = []
    folder_paths = []
    for directory in directories:
        for root, dirs, files in os.walk(directory):
            if not dirs:
                folder_name = os.path.basename(root)
                if folder_name.startswith("2") and len(folder_name) == 4:
                    second_to_last_folder = os.path.basename(os.path.dirname(os.path.dirname(root)))
                    new_folder_name = second_to_last_folder + '_' + folder_name
                    folder_names.append(new_folder_name)
                else:
                    folder_names.append(folder_name)
                folder_paths.append(root)
    return folder_paths, folder_names

def tokenizeArticles(articles):
    tokenized_articles = []
    for article in articles:
        tokenized_articles.append(nltk.sent_tokenize(article))
    return tokenized_articles

def processArticles(directories_to_frame, folder_names):
    articles = []
    article_names = []
    for i, directory in enumerate(directories_to_frame):
        # each different source should be framed for itself eg: FT,NYT,Guardian ...
        if directory[-4] != "2":
            starting_with = set()
            for filename in os.listdir(directory):
                starting_with.add(filename.split('-')[0])
            for start in starting_with:
                content = ""
                for filename in os.listdir(directory):
                    if filename.startswith(start):
                        file_path = os.path.join(directory, filename)
                        with open(file_path, encoding='unicode_escape') as file:
                            content += file.read()
                articles.append(content)
                article_names.append(str(folder_names[i]) + "_" + str(start))
        #frame/label each directory as a whole
        content = ""
        for filename in os.listdir(directory):
            file_path = os.path.join(directory, filename)
            with open(file_path, encoding='unicode_escape') as file:
                content += file.read()
        articles.append(content)
        article_names.append(folder_names[i])
    articles = tokenizeArticles(articles)
    return articles, article_names

def process(articles, article_names):
    os.makedirs("dumps/df_dumps/framing/", exist_ok=True)
    os.makedirs("dumps/df_dumps/lables/", exist_ok=True)
    print(f"Framing Dimensions: ")
    for i, article in enumerate(tqdm(articles, desc="Processing articles")):
        # Framing
        dimension = framing_dimensions(article)
        dimension_df = pd.DataFrame(dimension)
        dimension_df.to_csv(f"dumps/df_dumps/framing/{article_names[i]}_frame.csv", index=False)

        # Labels
        labels = framing_labels(article)
        labels_df = pd.DataFrame(labels)
        labels_df.to_csv(f"dumps/df_dumps/labels/{article_names[i]}_label.csv", index=False)


if __name__ == '__main__':
    directories_to_frame = ["COP"]
    directories_to_frame, folder_names = listFolders(directories_to_frame)
    articles, article_names = processArticles(directories_to_frame, folder_names)
    process(articles, article_names)

    print(articles)
    print(article_names)