"""This file contains assorted general utility functions used by other
modules in the PyAIML package.

"""


def sentences(s):
    """Split the string s into a list of sentences."""
    try:
        s + ""
    except TypeError:
        print "s must be a string"
    pos = 0
    sentence_list = []
    l = len(s)
    while pos < l:
        try:
            p = s.index('.', pos)
        except:
            p = l + 1
        try:
            q = s.index('?', pos)
        except:
            q = l + 1
        try:
            e = s.index('!', pos)
        except:
            e = l + 1
        end = min(p, q, e)
        sentence_list.append(s[pos:end].strip())
        pos = end + 1
    # If no sentences were found, return a one-item list containing
    # the entire input string.
    if len(sentence_list) == 0: sentence_list.append(s)
    return sentence_list


# Self test
if __name__ == "__main__":
    # sentences
    sents = sentences("First.  Second, still?  Third and Final!  Well, not really")
    assert (len(sents) == 4)
