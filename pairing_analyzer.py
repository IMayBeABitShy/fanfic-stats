"""
Anaylze stories regarding their pairings.
"""
import argparse
import pprint
import itertools

from chord import Chord

from ff2zim.project import Project


def increment_dict(org, new):
    """
    Increment each value in a dictionary with the value of the other dict with the same key.
    Expects both dicts to have the same keys.
    
    @param org: dict to increment
    @type org: L{dict}
    @param new: dict to use for incrementing
    @type new: L{dict}
    """
    for key in org:
        oldval = org[key]
        newval = oldval + new[key]
        org[key] = newval
        assert newval >= oldval


def hsv_to_rgb(h, s, v):
        """
        From https://stackoverflow.com/a/26856771
        """
        if s == 0.0: return (v, v, v)
        i = int(h*6.) # XXX assume int() truncates!
        f = (h*6.)-i; p,q,t = v*(1.-s), v*(1.-s*f), v*(1.-s*(1.-f)); i%=6
        if i == 0: return (v, t, p)
        if i == 1: return (q, v, p)
        if i == 2: return (p, v, t)
        if i == 3: return (p, q, v)
        if i == 4: return (t, p, v)
        if i == 5: return (v, p, q)


def colorlist(n):
    """
    Create a list containing n colors.
    
    @param n: number of colors
    @type n: L{int}
    """
    diff = 256 // n
    colors = []
    for i in range(n):
        h = (i * diff) / 256.0
        s = 1.0
        v = 1.0
        r, g, b = hsv_to_rgb(h, s, v)
        #r, g, b = int(r * 256), int(g * 256), int(b * 256)
        colors.append((r, g, b))
    return colors


class PairingAnalyzer(object):
    """
    Class for anaylzing pairing in stories from a ff2zim project.
    
    @param path: path to the project
    @type path: L{str}
    """
    def __init__(self, path, adult_only=False):
        self.path = path
        self.adult_only = adult_only
        self.project = Project(self.path)
    
    def filter_story(self, metadata):
        """
        Decide whether a story should be included, depending on the metadata.
        
        @param metadata: metadata of story
        @type metadata: L{dict}
        @return: whether the story should be included
        @rtype: L{bool}
        """
        if self.adult_only:
            return metadata["rating"].lower().strip().replace("+", "") == "m"
        else:
            return True
    
    def get_pairing_data(self):
        """
        Get a dict containing the collected data.
        
        @return: a dict of the data
        @rtype: L{tuple} of (L{dict} of L{str} -> L{int}, L{dict} of L{str} -> L{int})
        """
        pairing_stats = {}
        other_pairings = {}
        for metadata in self.project.collect_metadata():
            if not self.filter_story(metadata):
                continue
            
            # pairing preprocessing
            # get raw pairings
            rawpairings = metadata["ships"]
            # split pairings with more than 2 members into individual groups
            pairings = []
            for pairing in rawpairings:
                if len(pairing) == 1:
                    # ignore
                    continue
                elif len(pairing) == 2:
                    # normal
                    pairings.append(pairing)
                else:
                    # split
                    pairings += list(itertools.combinations(pairing, 2))
            # ensure unified name
            pairings = [tuple(sorted(s)) for s in pairings]
            
            for pairing in pairings:
                data = {
                    "occurences": 1,
                    "reviews":    metadata["reviews"],
                    "follows":    metadata["follows"],
                    "favorites":  metadata["favs"],
                    "words":      metadata["numWords"],
                    "chapters":   metadata["numChapters"],
                }
                if pairing not in pairing_stats:
                    pairing_stats[pairing] = data
                else:
                    increment_dict(pairing_stats[pairing], data)
                
                if len(pairings) == 1:
                    other = None
                    continue  # comment this line out to keep None
                else:
                    other = [p for p in pairings if p != pairing][0]
                cor_key = tuple(sorted(("/".join(pairing), ("/".join(other) if other is not None else "None"))))
                if cor_key not in other_pairings:
                    other_pairings[cor_key] = {"occurences": 1}
                else:
                    other_pairings[cor_key]["occurences"] += 1
        
        return {
            "stats": pairing_stats,
            "correlation": other_pairings,
        }
    
    def makegraph(self, outfile, masterkey="stats", key="occurences"):
        """
        Generate a graph.
        
        @param outfile: path to file to write to
        @type outfile: L{str}
        @param masterkey: category key of get_pairing_data()'s result to use.
        @type masterkey: L{str}
        @param key: key for value to use
        @type key: L{str}
        """
        # prepare data
        data = self.get_pairing_data()
        pairingstats = data[masterkey]
        
        # purge all entries were value of key <= 0
        to_purge = set()
        for pairing in pairingstats.keys():
            v = pairingstats[pairing][key]
            if v <= 0:
                to_purge.add(pairing)
        for p in to_purge:
            del pairingstats[p]
        
        names = list(sorted(set([name for pairing in data[masterkey] for name in pairing])))
        
        n_names = len(names)
        matrix = [[0] * n_names for i in range(n_names)]
        for pairing in pairingstats.keys():
            v = pairingstats[pairing][key]
            name_1, name_2 = pairing
            i, j = names.index(name_1), names.index(name_2)
            matrix[i][j] = v
            matrix[j][i] = v
        
        c = Chord(
            matrix,
            names,
            width=1600,
            margin=200,
            padding=0.02,
            wrap_labels=False,
            font_size="12px",
            noun="FanFics",
            allow_download=True,
            #title="Ships (by {})".format(key),
            credit=False,
            )
        c.to_html(filename=outfile)


def main():
    """
    The main function.
    """
    parser = argparse.ArgumentParser(description="Analyze stories regarding their pairings of a ff2zim project")
    parser.add_argument("project", help="path to ff2zim project")
    parser.add_argument("outfile", help="path to write HTML to")
    parser.add_argument("masterkey", action="store", choices=("stats", "correlation"), help="switch between stats for individual pairings and stats between pairings")
    parser.add_argument("key", action="store", choices=("occurences", "follows", "favorites", "words", "chapters"))
    parser.add_argument("--adult-only", action="store_true", help="Only evaluate fanfics rated mature / adult_only. May not work correctly.")
    parser.add_argument("-p", action="store_true", help="print gathered data")
    ns = parser.parse_args()
    
    analyzer = PairingAnalyzer(ns.project, adult_only=ns.adult_only)
    data = analyzer.get_pairing_data()
    
    if ns.p:
        pprint.pprint(data)
    
    analyzer.makegraph(ns.outfile, masterkey=ns.masterkey, key=ns.key)
        


if __name__ == "__main__":
    main()
