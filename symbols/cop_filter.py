# %%
import re  

def filter_special_characters(text, remove_newlines=True):
    # (A|C|B|D)\.( )?((1|2|3|4|5|6|7|8|9)(\.(1|2|3|4|5|6|7|8|9))?)? for B.3.2
    # remove lines without letters in them
    text = re.sub(r"^[^a-zA-Z]*$", "", text)
    # remove numbers followed by a dot if at the beginning of a line e.g. or "1. sentence\n1.1. sentence\n1.1.1. sentence"
    text = re.sub(r"^\d+(\.\d*)*", "", text)
    # remove quotes such as "
    text = re.sub(r"\"", "", text)
    # remove non-ascii characters, purposely replaced with space since sometimes situations like "word1�word2" occur
    text = re.sub(r"�", " ", text)  
    # fuse split words in multiple lines e.g. "syllab-\nle"
    text = re.sub(r"-\n", "", text)  
    # remove references and links e.g. {3.6, 10.3}, {see Box3} or {FAQ 9.2, Figure 1}
    text = re.sub(r"\{.*?\}", "", text)

    # remove enumerations
    # purposely remove the space after the hyphen to prevent splitting of words like "co-sponsored"
    text = re.sub(r"\*|•|■|▪|- |❖|►|»»|>>||<<|□□", "", text)
    if remove_newlines:
        # fuses titles, headers, footers, etc. to as single sentence => better normalization
        # also prevent single sentences from being split to multiple ones by newlines
        text = re.sub(r"\n|\t", " ", text)

        # ? should %, $, £, € be removed?
    return text


# %%
import os

# read all files in the directory and its subdirectories
# for each file, read its content and filter out special characters
# overwrite the file with the filtered content
def filter_directory(directory): 
    for subdir, dirs, files in os.walk(directory):
        for file in files:
            filepath = subdir + os.sep + file
            if filepath.endswith(".txt"):
                with open(filepath, "r", encoding='unicode_escape') as f:
                    text = f.read()
                filtered_text = filter_special_characters(text)
                with open(filepath, "w") as f:
                    f.write(filtered_text)
                print(f"Filtered {filepath}")

# %%
filter_directory("./COP/NGO")


