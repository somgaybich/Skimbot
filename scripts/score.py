from wordfreq import zipf_frequency
from math import log2

def score(word: str, occurences: int, size: int, mode: int = 0):
    """
    Generates a frequency score for a word.

    :param word: The word to analyze
    :type word: str
    :param occurences: The number of times this word appears in the data
    :type occurences: int
    :param size: The size of the dataset
    :type size: int
    :param mode: The formula to use for determining word score. 0=default,
    1=raw, 2=real
    :type mode: int[0|1|2]
    """
    match mode:
        case 0:
            expected = 10**(zipf_frequency(word, 'en') - 9)
            observed = occurences / size
            word_score = log2(observed / expected)
            return word_score
        case 1:
            observed = occurences / size
            return observed
        case 2:
            if zipf_frequency(word, 'en') == 0:
                return 0
            else:
                return score(word, occurences, size)
