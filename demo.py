import csv

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import pickle
import nltk
import os
import matplotlib.colors as mcolors
import matplotlib.patches as mpatches
from framefinder import framedimensions

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
framing_dimensions = framedimensions.FramingDimensions(base_model, dimensions, pole_names)


def listFolders(directories):
    folder_names = []
    folder_paths = []
    for directory in directories:
        for root, dirs, files in os.walk(directory):
            for folder in dirs:
                folder_paths.append(os.path.join(root, folder))
                folder_names.append(folder)
    debug2(folder_paths, folder_names)
    return folder_paths, folder_names


def tokenizeArticles(articles):
    tokenized_articles = []
    for article in articles:
        tokenized_articles.append(nltk.sent_tokenize(article))
    return tokenized_articles


def processArticles(directories_to_frame, folder_names, grouped_by_source=False):
    articles = []
    article_names = []
    for i, directory in enumerate(directories_to_frame):
        # each different source should be framed for itself eg: FT,NYT,Guardian ...
        if grouped_by_source:
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
        else:
            content = ""
            for filename in os.listdir(directory):
                file_path = os.path.join(directory, filename)
                with open(file_path, encoding='unicode_escape') as file:
                    content += file.read()
            articles.append(content)
            article_names.append(folder_names[i])
    articles = tokenizeArticles(articles)
    return articles, article_names


def processFraming(articles, article_names, path_to_plt_directory, scaling):
    print(f"Framing: ")
    for i, article in enumerate(articles):
        labels = framing_dimensions(article)
        labels_df = pd.DataFrame(labels)
        labels_df.to_csv("dumps/df_dumps/" + article_names[i] + ".csv", index=False)

        g = framing_dimensions.visualize(labels_df)
        g.axes[0].set_axisbelow(True)
        g.axes[0].yaxis.grid(color='gray', linestyle='dashed')
        plt.title('Frame Dimensions for "' + article_names[i] + '"')
        plt.gcf().set_size_inches(10, 7)
        print(f"\t" + article_names[i])
        for scale in scaling:
            plt.xlim(-scale, scale)
            os.makedirs(path_to_plt_directory + "scale_" + str(scale), exist_ok=True)
            os.makedirs("dumps/plt_dumps/" + "scale_" + str(scale), exist_ok=True)
            plt.savefig(
                path_to_plt_directory + "scale_" + str(scale) + "/" + article_names[i] + "_scale_" + str(scale)[2:],bbox_inches='tight')
            pickle.dump(plt.gcf(), open(
                "dumps/plt_dumps/" + "scale_" + str(scale) + "/" + article_names[i] + "_scale_" + str(scale)[2:], "wb"))


def debug1(sub_folders, scaling, directories_to_frame):
    print(f"Processing: \n" + f"\tSub-folders: " + str(sub_folders) + "\n" + f"\tScaling: " + str(scaling))
    print(f"\tDirectories: ")
    for directory in directories_to_frame:
        print(f"\t\t- " + str(directory))


def debug2(folder_paths, folder_names):
    print(f"\tSub-Folders: ")
    for folder in folder_paths:
        print(f"\t\t- " + str(folder))
    print(f"\tFolder names: ")
    for name in folder_names:
        print(f"\t\t- " + str(name))


def compareCustom(df_paths, scale, custom_names=None, title = None):
    print(f"\tComparing custom: ")
    dfs = []
    names = []
    for path in df_paths:
        dfs.append(pd.read_csv(path, header=[0, 1]))
        names.append(os.path.splitext(os.path.basename(path))[0])
    if custom_names is not None:
        names = custom_names
    if title is None:
        title = f"Comparing {names[0]}"
        for name in names[1:]:
            title += f" and {name}"
    g = compare_plots(dfs, names, scale)
    plt.title(title)
    print(f"\t\t- " + str(title))
    plt.savefig("plots/Press_ONG_OIG_Climate_change/custom_compare/" + title + ".png",bbox_inches='tight')
    pickle.dump(plt.gcf(),
                open("dumps/plt_dumps/custom_compare/" + "compare_" + title + "_scale_" + str(scale)[2:], "wb"))


def compareAll(scale, starts_with=""):
    print(f"\tComparing all plots: ")
    path = "dumps/df_dumps/"
    filenames = os.listdir(path)
    dfs = []
    pairs = []
    compare = []
    names = set()
    for filename in filenames:
        if starts_with != "":
            if not filename.startswith(starts_with):
                continue
        name = filename.rsplit('_', 1)[-1].split('.')[0]
        if name.startswith("COP"):
            continue
        names.add(name)
    for name in names:
        df = []
        pair = []
        for filename in filenames:
            if filename.endswith(name + ".csv"):
                df.append(pd.read_csv(path + filename, header=[0, 1]))
                pair.append(filename.split(".csv")[0])
        dfs.append(df)
        pairs.append(pair)
        compare.append(name)
    for i, df in enumerate(dfs):
        if len(df) != 1:
            g = compare_plots(dfs[i], pairs[i], scale, compare= compare[i], save= True)
            plt.title(f'Comparing {compare[i]}')
            print(f"\t\t- " + str({compare[i]}))
            plt.savefig("plots/Press_ONG_OIG_Climate_change/compare/" + compare[i] + ".png",bbox_inches='tight')
            pickle.dump(plt.gcf(),
                        open("dumps/plt_dumps/compare/" + "compare_" + compare[i] + "_scale_" + str(scale)[2:], "wb"))


def compare_plots(dfs, titles, scale, colors=list(mcolors.TABLEAU_COLORS),save = False, compare = None):
    name_left = dfs[0].columns.map(lambda x: x[1])
    name_right = dfs[0].columns.map(lambda x: x[0])
    means = [df.mean() for df in dfs]
    intens = [(df.var().fillna(0) + 0.001) * 50_000 for df in dfs]
    if save:
        l = len(means)
        framing_values = 5*[0]
        for i in range(l):
            framing_values[0] += means[i].values[0]
            framing_values[1] += means[i].values[1]
            framing_values[2] += means[i].values[2]
            framing_values[3] += means[i].values[3]
            framing_values[4] += means[i].values[4]
        for i in range(5):
            framing_values[i] = framing_values[i] / l
        path = "dumps/df_dumps/grouped_by_name/grouped_by_" + compare +".csv"
        with open(path, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["Care", "Fairness", "Loyalty", "Authority", "Sanctity"])
            writer.writerow(["Harm", "Cheating", "Betrayal", "Subversion", "Degredation"])
            writer.writerow(framing_values)
            #writer.writerow(str(framing_values[0])+","+str(framing_values[1])+","+str(framing_values[2])+","+str(framing_values[3])+","+str(framing_values[4]))
    legend_entries = [mpatches.Patch(color=colors[0], label=titles[0])]

    fig = plt.figure()
    ax = fig.add_subplot(111)
    plt.scatter(x=means[0], y=name_left, s=intens[0], c=colors[0])
    plt.axvline(0)
    plt.gca().invert_yaxis()
    ax.twinx().set_yticks(ax.get_yticks(), labels=name_right)
    fig.axes[0].set_axisbelow(True)
    fig.axes[0].yaxis.grid(color="gray", linestyle="dashed")
    plt.xlim(-scale, scale)  # ! arbitrary range
    for i in range(1, len(dfs)):
        legend_entries.append(mpatches.Patch(color=colors[i], label=titles[i]))
        plt.scatter(x=means[i], y=name_left, s=intens[i], c=colors[i])

    plt.gcf().set_size_inches(10, 7)
    plt.tight_layout()
    plt.legend(handles=legend_entries)
    return fig


if __name__ == '__main__':
    frame = True
    custom_compare = False
    sub_folders = True
    compare_all = True
    if frame:
        path_to_plt_directory = "plots/Press_ONG_OIG_Climate_change/"
        directories_to_frame = ["data/Corpus-Presse","data/Corpus-ONG (NGOs)","data/Corpus-OIG (IGOs)"]
        scaling = [0.1, 0.05, 0.075]
        debug1(sub_folders, scaling, directories_to_frame)
        if sub_folders:
            directories_to_frame, folder_names = listFolders(directories_to_frame)
        else:
            folder_names = []
            for folder_name in directories_to_frame:
                folder_names.append(folder_name.split('/')[-1])
        articles, article_names = processArticles(directories_to_frame, folder_names, True)
        processFraming(articles, article_names, path_to_plt_directory, scaling)
    if compare_all:
        scale = 0.1
        compareAll(scale)
    if custom_compare:
        paths = ["dumps/df_dumps/grouped_by_name/grouped_by_WB.csv","dumps/df_dumps/grouped_by_name/grouped_by_UNEP.csv","dumps/df_dumps/grouped_by_name/grouped_by_WMO.csv"]
        compareCustom(paths,0.1)
    pass