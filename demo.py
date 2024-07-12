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
from framefinder import framelabels
from sklearn.preprocessing import MinMaxScaler

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
base_model = "all-mpnet-base-v2"

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
framing_dimensions = framedimensions.FramingDimensions(
    base_model, dimensions, pole_names
)


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
                starting_with.add(filename.split("-")[0])
            for start in starting_with:
                content = ""
                for filename in os.listdir(directory):
                    if filename.startswith(start):
                        file_path = os.path.join(directory, filename)
                        with open(file_path, encoding="unicode_escape") as file:
                            content += file.read()
                articles.append(content)
                article_names.append(str(folder_names[i]) + "_" + str(start))
        else:
            content = ""
            for filename in os.listdir(directory):
                file_path = os.path.join(directory, filename)
                with open(file_path, encoding="unicode_escape") as file:
                    content += file.read()
            articles.append(content)
            article_names.append(folder_names[i])
    articles = tokenizeArticles(articles)
    return articles, article_names


def find_min_max_values(directory):
    # Mean
    all_values = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(".csv"):
                file_path = os.path.join(root, file)
                df = pd.read_csv(file_path, header=[0, 1])
                means = df.mean().values
                all_values.extend(means)
    min_v = min(all_values)
    max_v = max(all_values)
    return min_v - 1 / 20 * min_v, max_v + 1 / 20 * max_v


def normalize_files(input_dir, output_dir):
    min_v, max_v = find_min_max_values(input_dir)
    if max_v > abs(min_v):
        min_v = -max_v
    else:
        max_v = abs(min_v)
    os.makedirs(output_dir, exist_ok=True)

    for file in os.listdir(input_dir):
        if file.endswith(".csv"):
            input_path = os.path.join(input_dir, file)
            output_path = os.path.join(
                output_dir, f"{os.path.splitext(file)[0]}_norm.csv"
            )
            df = pd.read_csv(input_path, header=[0, 1])
            means = df.mean().values
            normalized_means = [
                2 * ((xi - min_v) / (max_v - min_v)) - 1 for xi in means
            ]
            norm_df = pd.DataFrame(columns=pd.MultiIndex.from_tuples(pole_names))
            norm_df.loc[0] = normalized_means
            norm_df.to_csv(output_path, index=False)

            g = framing_dimensions.visualize(norm_df)
            g.axes[0].set_axisbelow(True)
            g.axes[0].yaxis.grid(color="gray", linestyle="dashed")
            plt.title(
                'Normalized Frame Dimensions for "'
                + os.path.splitext(file)[0]
                + ' [-1,1]"'
            )
            plt.gcf().set_size_inches(10, 7)
            plt.xlim(-1, 1)
            plt.savefig(
                "plots/Press_ONG_OIG_Climate_change/normalized/scale_1_-1/"
                + os.path.splitext(file)[0],
                bbox_inches="tight",
            )


def processFraming(articles, article_names, path_to_plt_directory, scaling):
    print(f"Framing Dimensions: ")
    for i, article in enumerate(articles):
        labels = framing_dimensions(article)
        labels_df = pd.DataFrame(labels)
        labels_df.to_csv("dumps/df_dumps/" + article_names[i] + ".csv", index=False)
        g = framing_dimensions.visualize(labels_df)
        g.axes[0].set_axisbelow(True)
        g.axes[0].yaxis.grid(color="gray", linestyle="dashed")
        plt.title('Frame Dimensions for "' + article_names[i] + '"')
        plt.gcf().set_size_inches(10, 7)
        print(f"\t" + article_names[i])
        for scale in scaling:
            plt.xlim(-scale, scale)
            os.makedirs(path_to_plt_directory + "scale_" + str(scale), exist_ok=True)
            os.makedirs("dumps/plt_dumps/" + "scale_" + str(scale), exist_ok=True)
            plt.savefig(
                path_to_plt_directory
                + "scale_"
                + str(scale)
                + "/"
                + article_names[i]
                + "_scale_"
                + str(scale)[2:],
                bbox_inches="tight",
            )


def processLabels(articles, article_names, path_to_plt_directory):
    print(f"Framing Labels: ")
    for i, article in enumerate(articles):
        labels = framing_labels(article)
        labels_df = pd.DataFrame(labels)
        labels_df.to_csv(
            "dumps/df_dumps_labels/" + article_names[i] + ".csv", index=False
        )

        _, ax = framing_labels.visualize(
            labels_df.mean().to_dict(), xerr=labels_df.sem()
        )
        ax.xaxis.set_major_formatter(mticker.ScalarFormatter())
        plt.xticks([0.1, 0.5, 1])
        plt.title('Frame Labels for "' + article_names[i] + '"')
        plt.axvline(0.5, color="red")
        plt.gcf().set_size_inches(10, 7)
        print(f"\t" + article_names[i])
        plt.savefig(
            path_to_plt_directory + "/labels/" + article_names[i], bbox_inches="tight"
        )
        pickle.dump(plt.gcf(), open("dumps/plt_dumps/labels/" + article_names[i], "wb"))


def debug1(sub_folders, scaling, directories_to_frame):
    print(
        f"Processing: \n"
        + f"\tSub-folders: "
        + str(sub_folders)
        + "\n"
        + f"\tScaling: "
        + str(scaling)
    )
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


def compareCustom(df_paths, scale, custom_names=None, title=None):
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
    plt.savefig(
        "plots/Press_ONG_OIG_Climate_change/custom_compare/" + title + ".png",
        bbox_inches="tight",
    )
    pickle.dump(
        plt.gcf(),
        open(
            "dumps/plt_dumps/custom_compare/"
            + "compare_"
            + title
            + "_scale_"
            + str(scale)[2:],
            "wb",
        ),
    )


def compareAll(scale, starts_with=""):
    print(f"\tComparing all plots: ")
    path = "dumps/df_dumps/"
    filenames = os.listdir(path)
    dfs = []
    pairs = []
    compare = []
    names = set()
    for filename in filenames:
        if filename.endswith(".csv"):
            if starts_with != "":
                if not filename.startswith(starts_with):
                    continue
            name = filename.rsplit("_", 1)[-1].split(".")[0]
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
            g = compare_plots(dfs[i], pairs[i], scale, compare=compare[i], save=True)
            plt.title(f"Comparing {compare[i]}")
            print(f"\t\t- " + str({compare[i]}))
            plt.savefig(
                "plots/Press_ONG_OIG_Climate_change/compare/" + compare[i] + ".png",
                bbox_inches="tight",
            )
            pickle.dump(
                plt.gcf(),
                open(
                    "dumps/plt_dumps/compare/"
                    + "compare_"
                    + compare[i]
                    + "_scale_"
                    + str(scale)[2:],
                    "wb",
                ),
            )
        else:
            print(f"\t\tskipping- " + str({compare[i]}))


def compare_plots(
    dfs, titles, scale, colors=list(mcolors.TABLEAU_COLORS), save=False, compare=None
):
    name_left = dfs[0].columns.map(lambda x: x[1])
    name_right = dfs[0].columns.map(lambda x: x[0])
    means = [df.mean() for df in dfs]
    intens = [(df.var().fillna(0) + 0.001) * 50_000 for df in dfs]
    if save:
        path = "dumps/df_dumps/grouped_by_name/grouped_by_" + compare + ".csv"
        dfs[0].to_csv(path, index=False)
        for df in dfs[1:]:
            df.to_csv(path, index=False, header=False, mode="a")

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


def process_dimension_files(directory, plot_directory):
    if not os.path.exists(directory):
        print(f"Directory {directory} does not exist")
        return
    files = [f for f in os.listdir(directory) if f.endswith(".csv")]
    if not files:
        print(f"No CSV files found in {directory}")
        return
    os.makedirs(plot_directory, exist_ok=True)
    for file in files:
        file_path = os.path.join(directory, file)
        df = pd.read_csv(file_path, header=[0, 1])

        g = framing_dimensions.visualize(df)
        g.axes[0].set_axisbelow(True)
        g.axes[0].yaxis.grid(color="gray", linestyle="dashed")
        plt.title('Frame Dimensions for "' + os.path.splitext(file)[0] + '"')
        plt.gcf().set_size_inches(10, 7)
        plt.xlim(-0.12, 0.12)
        plot_path = os.path.join(plot_directory, f"{os.path.splitext(file)[0]}.png")
        plt.savefig(plot_path, bbox_inches="tight")
        plt.close()


def process_label_files(input_dir, output_dir):
    if not os.path.exists(input_dir):
        print(f"Input directory {input_dir} does not exist")
        return
    os.makedirs(output_dir, exist_ok=True)
    files = [f for f in os.listdir(input_dir) if f.endswith(".csv")]
    if not files:
        print(f"No CSV files found in {input_dir}")
        return

    for file in files:
        file_path = os.path.join(input_dir, file)
        df = pd.read_csv(file_path)
        df = df.drop(columns=df.columns[0])
        _, ax = framing_labels.visualize(df.mean().to_dict(), xerr=df.sem())
        ax.xaxis.set_major_formatter(mticker.ScalarFormatter())
        plt.xticks([0.1, 0.5, 1])
        plt.title(f'Frame Labels for "{os.path.splitext(file)[0]}"')
        plt.axvline(0.5, color="red")
        plot_path = os.path.join(output_dir, f"{os.path.splitext(file)[0]}.png")
        plt.savefig(plot_path, bbox_inches="tight")
        plt.close()


if __name__ == "__main__":
    read = False
    frame = False
    label = False
    custom_compare = False
    sub_folders = False
    compare_all = False
    normalize = False
    cluster = True

    if read:
        path_to_plt_directory = "plots/Press_ONG_OIG_Climate_change/"
        directories_to_frame = ["COP/Unordered_Year/NGO", "COP/Unordered_Year/Presse"]
        scaling = [0.1]
        debug1(sub_folders, scaling, directories_to_frame)
        if sub_folders:
            directories_to_frame, folder_names = listFolders(directories_to_frame)
        else:
            folder_names = []
            for folder_name in directories_to_frame:
                folder_names.append(folder_name.split("/")[-1])
        articles, article_names = processArticles(
            directories_to_frame, folder_names, True
        )
        if frame:
            processFraming(articles, article_names, path_to_plt_directory, scaling)
        if label:
            processLabels(articles, article_names, path_to_plt_directory)
    if compare_all:
        scale = 0.1
        compareAll(scale)
    if normalize:
        normalize_files("dumps/cluster/dimensions", "plots/cluster/dimensions")
    if cluster:
        process_label_files("dumps/cluster/labels", "plots/cluster/labels")
        process_dimension_files("dumps/cluster/dimensions", "plots/cluster/dimensions")
    if custom_compare:
        paths = [
            "dumps/df_dumps/OIG_COP15.csv",
            "dumps/df_dumps/OIG_COP21.csv",
            "dumps/df_dumps/OIG_COP25_26.csv",
            "dumps/df_dumps/ONG_COP15.csv",
            "dumps/df_dumps/ONG_COP21.csv",
            "dumps/df_dumps/ONG_COP25_26.csv",
        ]
        compareCustom(paths, 0.1, title="IGOs vs NGOs")
