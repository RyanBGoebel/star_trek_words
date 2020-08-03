"""
Generates a word cloud with words used in Star Trek series at a higher
frequency than they are used in the English language.
"""

import requests
import json
import string
from wordfreq import word_frequency
from wordcloud import WordCloud, STOPWORDS, ImageColorGenerator
import enchant
import matplotlib.pyplot as plt
from PIL import Image



def clean_script(ep):
    """
    Removes header, footer, character directions, and scene settings.
    """
    # Remove header based on location of "Original Airdate"
    orig_airdate_loc = scripts[ep].find('Original Airdate')
    scripts[ep] = scripts[ep][orig_airdate_loc +  35:]

    # Remove footer based on location of "<Back" or "To Be Continued..."
    end_loc = scripts[ep].find('To Be Continued...')
    if end_loc > 0:
        scripts[ep] = scripts[ep][ :end_loc]
    else:
        end_loc = scripts[ep].find('<Back')
        scripts[ep] = scripts[ep][ :end_loc]

    # Remove all non-dialogue text between brackets and parenthesis
    # (script directions) and [script settings]
    # {} and : take into account some script inconsistencies or typos
    ep_without_bracketed_text = ''
    bracket_status = 0
    for char in scripts[ep]:
        if char == '[' or char == '(' or char == '{':
            bracket_status = 1
        elif char == ']' or char == ')' or char == '}' or char == ':':
            bracket_status = 0
        elif bracket_status == 0:
            ep_without_bracketed_text += char
    scripts[ep] = ep_without_bracketed_text


def contractions(ep):
    """
    Removes contractions, but leaves root word so total word count is less affected.
    Also, removes or modifies some other words with unique punctuation.
    """
    apostrophe_count = scripts[ep].count("'")
    scripts[ep] = scripts[ep].replace("won't", "will")
    scripts[ep] = scripts[ep].replace("don't", "do")
    scripts[ep] = scripts[ep].replace("Won't", "will")
    scripts[ep] = scripts[ep].replace("Don't", "do")
    scripts[ep] = scripts[ep].replace("'t", " ")
    scripts[ep] = scripts[ep].replace("'re", " ")
    scripts[ep] = scripts[ep].replace("'t", " ")
    scripts[ep] = scripts[ep].replace("'s", " ")
    scripts[ep] = scripts[ep].replace("'ll", " ")
    scripts[ep] = scripts[ep].replace("'d", " ")
    scripts[ep] = scripts[ep].replace("'ve", " ")
    scripts[ep] = scripts[ep].replace("'", " ")
    scripts[ep] = scripts[ep].replace("co-ordinates", "coordinates")
    scripts[ep] = scripts[ep].replace("ah-wraith", " ")
    scripts[ep] = scripts[ep].replace("ah wraith", " ")

def speaking_characters(words):
    """
    In the scripts, the speaker is always shown in all caps, so function finds
    all words that are all caps and adds them to proper_list (which will be
    ignored in the program's final output)
    """
    for word in words:
        if (word.isupper() == True):
            if word.lower() not in proper_list:
                proper_list.append(word.lower())


def gb2us(words):
    """
    Convert words in script from British English to American English to more
    accurately reflect the word usage frequency in English.
    Note: us2gb-dictionary.txt file from:
    https://gist.github.com/rcortini/0d05417339bc74300ce3a971442a4d3c#file-us2gb-dictionary-txt
    Had to modify flyer/flier flier/flyer line in text file (could also delete)
    """
    gb2us_dict = {}
    with open("../data/us2gb-dictionary.txt") as f:
        for line in f:
            (key, val) = line.split()
            gb2us_dict[key] = val
    for word in words:
        if word in gb2us_dict.keys():
            word = gb2us_dict[word]



def is_english_word(word):
    """
    Uses PyEnchant spellchecking library to determine if word is an English word.
    Note:  I used the GB dictionary, since several words in TNG scripts seem to
    use the British spellings (ie, "neutralise" instead of "neutralize")
    """
    us_eng_dict = enchant.Dict("en_US")
    result = False
    if us_eng_dict.check(word) == True:
        result = True
    #elif us_eng_dict.check(word) == False:
    #    result = False
    return result


def purge_words(word_count_dict, star_trek_series):
    """
    Removes all character names and additional words from manually-entered
    list of proper nouns and number words: "words_to_purge".
    """
    words_to_purge = (['twenty', 'thirty', 'forty', 'fifty', 'sixty',
                    'seventy', 'eighty', 'ninety', 'eleven', 'twelve',
                    'thirteen', 'fourteen', 'fifteen', 'sixteen', 'seventeen',
                    'eighteen', 'nineteen', 'one', 'two', 'three', 'four',
                    'five', 'six', 'seven', 'eight', 'nine']
                    )

    words_to_purge += proper_list
    if star_trek_series == 'TNG':
        words_to_purge.remove('sickbay')
    for word in word_count_dict:
        if is_english_word(word) == False:
            words_to_purge.append(word)
    for word in words_to_purge:
        try: del word_count_dict[word]
        except: pass



### Open JSON file with all Star Trek series scripts
### Downloaded from: https://www.kaggle.com/gjbroughton/start-trek-scripts
with open("../data/all_scripts_raw.json") as json_file:
    all_scripts = json.load(json_file)

json.dumps(all_scripts, sort_keys=True, indent=4)


# Choose which series to analyze
series_options = ['tos', 'tas', 'tng', 'ds9', 'voy', 'ent']

scripts = None

while scripts is None:
    star_trek_series = input("""\nWhich series would you like to analyze?\n
Please input:\n"TOS" for The Original Series,\n"TAS" for The Animated Series,
"TNG" for The Next Generation,\n"DS9" for Deep Space 9,\n"VOY" for Voyager,
"ENT" for Enterprise\n""")
    try:
        star_trek_series = star_trek_series.upper()
        scripts = all_scripts[star_trek_series]
        print("Engage {}!".format(star_trek_series))
    except:
        print("\n\n--- HIGHLY ILLOGICAL INPUT ERROR.  PLEASE TRY AGAIN. ---\n")


# List of proper nouns to be removed from counts since some names are English words (ie, "Data")
# Lieutenant Marla ASTER and Jeremy ASTER, U.S.S. Enterprise & U.S.S. STARGAZER,
# CRUSHERS (Beverly and Wesley), Lieutenant Reginald Barclay (aka 'REG')
# Lieutenant Romaine from The Original Series episode "The Lights Of Zetar"
# Includes characters, titles, and other proper nouns for exclusion
# I'm sure there are some missing ones here and/or a better way to do this.
proper_list = (['aster', 'crushers', 'stargazer', 'enterprise', 'reg',
                  'voyager', 'lawgiver', 'lawgivers', 'mister', 'commander',
                  'proconsul', 'fuhrer', 'counsellor', 'ensign', 'captain',
                  'doctor', 'lieutenant', 'romaine', 'helmsman', 'commodore',
                  'utopia', 'planitia', 'sublieutenant', 'saurian', 'master',
                  'thrall', 'emissary', 'pah', 'badlands', 'trill', 'babel',
                  'reptilians'])

# create a dictionary with words and respective counts from all episodes of TNG
word_count_dict = { }
total_word_count = 0

for episode in scripts:
    clean_script(episode)
    contractions(episode)

    for char in string.punctuation:
        scripts[episode] = scripts[episode].replace(char," ")

    words = scripts[episode].strip().split()

    speaking_characters(words)
    gb2us(words)

    # Make all remaining words lower case, count, and add to dictionary
    for word in words:
        word = word.lower()
        total_word_count += 1
        try:
            word_count_dict[word] += 1
        except:
            word_count_dict[word] = 1


# From words in episode, purge non-English words (based on PyEnchant)
# and character names
purge_words(word_count_dict, star_trek_series)

# Adjust "sickbay" count for the 3 times it was a "character" in the TNG script
if star_trek_series == 'TNG':
    word_count_dict['sickbay'] = word_count_dict['sickbay'] - 3

# Calculate the frequency of each word in word_count_dict and add to word_freq_dict
series_word_freq_dict = {}
english_word_freq_dict = {}
for word in word_count_dict: #keys()
    english_word_freq_dict[word] = word_frequency(word, 'en', wordlist='best')
    series_word_freq_dict[word] = word_count_dict[word] / total_word_count

# Calculate the ratio of word usage in Star Trek series vs usage in English
# Create a string of words based on the frequency ratios
word_cloud_string = ""
word_freq_ratios = {}

for word in series_word_freq_dict:
    # Filter out words that have frequencies in the English language of "zero"
    if english_word_freq_dict[word] > 0:
        ratio_vs_english = series_word_freq_dict[word] / english_word_freq_dict[word]
        # Only use words that are used more freq than in English and used at least
        # 5 times in the series
        if ratio_vs_english > 1.0 and word_count_dict[word] > 5:
            word_freq_ratios[word] = ratio_vs_english
            # Use a factor of 10 to better distinguish better between words,
            # for example words that are used 1.1 times more than English and
            # words that are used 1.8 times more than English.  This makes the
            # word cloud look better.
            counter = ratio_vs_english * 10 # factor of 10
            while counter > 0:
                word_cloud_string += word + " "
                counter = counter - 1

# create and generate a word cloud image
wordcloud = WordCloud(background_color="white",
                      width=2000, height=2000,
                      collocations = False,
                      stopwords=STOPWORDS,
                      max_words=2100,
                      ).generate(word_cloud_string)


# display the generated image
plt.imshow(wordcloud, interpolation='bilinear')
#plt.title('star_trek_series = {} filter_word = {}'.format(star_trek_series, filter_word))
plt.axis('off')
plt.show()

sorted_counts = sorted(word_count_dict.items(), key=lambda x: x[1], reverse=True)
rank = 0
for word in sorted_counts[0:100]:
    rank += 1
    print("{}: {} is said {} times in {}.".format(rank, word[0], word[1], star_trek_series))


sorted_freq_ratios = sorted(word_freq_ratios.items(), key=lambda x: x[1], reverse=True)
rank = 0
for word in sorted_freq_ratios[0:100]:
    rank += 1
    print("{}: {} is used {} times more frequently in {} than in English.".format(rank, word[0], word[1], star_trek_series))
