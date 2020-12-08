"""
Make a wordcloud from a ff2zim project.
"""
import argparse
import re
import os

from ff2zim.project import Project

from html2text import html2text
from fanficfare.htmlcleanup import removeAllEntities
import wordcloud


REPLACEMENTS = {
}

TO_IGNORE = [
    "to",
    "the", "a", "an",
    "was",
    "and",
    "is", "isnt", "was", "wasnt", "be", "wont", "were", "werent", "an",
    "out",
    "of",
    "has", "have", "had",
    "do", "did", "didnt", "done",
    "as",
    "i", "you", "he", "she", "it", "we", "they", "them",
    "my", "yours", "his", "her", "its", "our", "their",
    "me", "your", "him", "im", "us", "youre"
    "ill", "youll", "well",
    "in", "at", "on", "with", "without", "from",
    "but", "this", "that", "what", "why", "where", "who", "whom",
    "can", "cant", "would", "woudlnt",
    "so",  "if", "for", "not",  "else",
    "then",
]


class WordcloudMaker(object):
    """
    Class for creating a wordcloud from a ff2zim project.
    
    @param path: path to the project
    @type path: L{str}
    """
    def __init__(self, path):
        self.path = path
        self.project = Project(self.path)
    
    def get_paths_to_include(self):
        """
        Return a list of story directories to include.
        
        @return: a list of the story directories to include
        @rtype: L{list} of L{str}
        """
        all_metadata = self.project.collect_metadata()
        to_include = []
        for metadata in all_metadata:
            if self.filter_story(metadata):
                fp = os.path.join(self.path, "fanfics", metadata["siteabbrev"], metadata["storyId"])
                to_include.append(fp)
        return to_include
    
    def filter_story(self, metadata):
        """
        Decide whether a story should be included, depending on the metadata.
        
        @param metadata: metadata of story
        @type metadata: L{dict}
        @return: whether the story should be included
        @rtype: L{bool}
        """
        return metadata["language"].lower() == "english"
    
    def get_combined_text(self):
        """
        Return the combined text of all stories as a string.
        
        @return: string containing the text of all stories.
        @rtype: L{str}
        """
        # non_char = re.compile(ur"[^A-Za-z]", re.UNICODE)
        non_char = re.compile(u"[^\\s\\w\\-]", re.UNICODE)
        extra_spaces = re.compile(u"(\n|\\.|\\!|\\?)", re.UNICODE)
        paths = self.get_paths_to_include()
        texts = []
        for p in paths:
            fp = os.path.join(p, "story.html")
            with open(fp, "r") as fin:
                content = fin.read()
                text = removeAllEntities(content)
                text = html2text(text)
                # basic replacements
                text = re.sub(non_char, "", text)
                text = re.sub(extra_spaces, " ", text)
                texts.append(text)
        print("Collected {} texts.".format(len(texts)))
        joined = " ".join(texts)
        print("Total length: {}".format(len(joined)))
        return joined
    
    def get_frequencies(self):
        """
        Get a dict containing the frequencies.
        
        @return: a tuple of (single word frequencies, double word frequencies)
        @rtype: L{tuple} of (L{dict} of L{str} -> L{int}, L{dict} of L{str} -> L{int})
        """
        words = self.get_combined_text().split(" ")
        single_counts = {}
        double_counts = {}
        prev = None
        
        for word in words:
            word = word.strip()
            if not word.replace("-", "").replace("_", ""):
                continue
            elif word.lower() in TO_IGNORE:
                continue
            single_counts[word] = single_counts.get(word, 0) + 1
            if prev is not None:
                phrase = prev + " " + word
                double_counts[phrase] = double_counts.get(phrase, 0) + 1
            prev = word
        return single_counts, double_counts
    
    def make_wordcloud(self, path, use_pairs=False):
        """
        Make a wordcloud and write it to the specified path.
        
        @param path: path to write image to
        @type path: L{str}
        @param use_pairs: if nonzero, use wordpairs
        @type use_pairs: L{bool}
        """
        single, double = self.get_frequencies()
        if use_pairs:
            source = double
        else:
            source = single
        cloud = wordcloud.WordCloud(
            width=1600,
            height=900,
            max_words=200,
            include_numbers=True,
            repeat=False,
        )
        cloud.generate_from_frequencies(source)
        cloud.to_file(path)


def main():
    """
    The main function.
    """
    parser = argparse.ArgumentParser(description="Create a wordcloud for a ff2zim project")
    parser.add_argument("project", help="path to ff2zim project")
    parser.add_argument("outfile", help="path to write image to")
    parser.add_argument("--pairs", action="store_true", dest="pairs", help="Use word pairs instead of single word")
    parser.add_argument("-i", "--ignore", action="append", help="ignore/exclude word(s)")
    ns = parser.parse_args()

    if ns.ignore:
        TO_IGNORE.extend(ns.ignore)
    
    maker = WordcloudMaker(ns.project)
    maker.make_wordcloud(ns.outfile, use_pairs=ns.pairs)
        


if __name__ == "__main__":
    main()
