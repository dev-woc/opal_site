"""
FCRR Resource Database

Manages FCRR (Florida Center for Reading Research) word lists and activity data.
Provides direct access to validated word lists organized by phonics patterns.
"""

from typing import List, Dict, Any, Optional
import json


class FCRRDatabase:
    """
    Database of FCRR resources including word lists and activity templates.

    Organizes words by:
    - Phonics patterns
    - Syllable types
    - Difficulty levels
    - Activity types (Purple/Orange/Green)
    """

    def __init__(self):
        """Initialize the FCRR database with word lists and activities"""
        self._initialize_word_lists()
        self._initialize_activities()

    def _initialize_word_lists(self) -> None:
        """Initialize comprehensive word lists organized by phonics patterns"""
        self.word_lists = {
            "short_vowels": {
                "cvc_a": {
                    "pattern": "CVC with short 'a'",
                    "difficulty": "beginner",
                    "words": ["cat", "mat", "sat", "hat", "bat", "rat", "fat", "pat", "vat", "can", "man", "pan", "fan", "ran", "tan", "van", "ban", "cap", "map", "tap", "nap", "gap", "sap", "rap", "bad", "dad", "mad", "sad", "had", "pad", "lad", "bag", "tag", "rag", "wag", "lag", "sag", "gas", "has", "jam", "ham", "ram", "dam", "yam", "Sam"],
                    "example_sentence": "The cat sat on a mat."
                },
                "cvc_i": {
                    "pattern": "CVC with short 'i'",
                    "difficulty": "beginner",
                    "words": ["bit", "fit", "hit", "kit", "lit", "pit", "sit", "wit", "big", "dig", "fig", "pig", "wig", "gig", "jig", "rig", "bin", "din", "fin", "pin", "tin", "win", "sin", "bid", "did", "hid", "kid", "lid", "rid", "bib", "rib", "dip", "hip", "lip", "nip", "rip", "sip", "tip", "zip", "dim", "him", "rim", "Tim", "Jim", "Kim"],
                    "example_sentence": "The pig is big."
                },
                "cvc_o": {
                    "pattern": "CVC with short 'o'",
                    "difficulty": "beginner",
                    "words": ["cot", "dot", "got", "hot", "jot", "lot", "not", "pot", "rot", "tot", "cob", "gob", "job", "mob", "rob", "sob", "bob", "cod", "god", "nod", "pod", "rod", "sod", "cop", "hop", "mop", "pop", "top", "dog", "fog", "hog", "jog", "log", "bog", "cog", "fox", "box", "pox", "mom", "Tom", "Don", "Ron"],
                    "example_sentence": "The dog is on top of the log."
                },
                "cvc_e": {
                    "pattern": "CVC with short 'e'",
                    "difficulty": "beginner",
                    "words": ["bed", "fed", "led", "red", "wed", "Ted", "Ned", "beg", "leg", "peg", "keg", "Meg", "bet", "get", "jet", "let", "met", "net", "pet", "set", "vet", "wet", "yet", "den", "hen", "men", "pen", "ten", "Ben", "Ken", "web", "peck", "deck", "neck"],
                    "example_sentence": "Ten men are in the den."
                },
                "cvc_u": {
                    "pattern": "CVC with short 'u'",
                    "difficulty": "beginner",
                    "words": ["bug", "dug", "hug", "jug", "mug", "pug", "rug", "tug", "bud", "dud", "mud", "cud", "bum", "gum", "hum", "rum", "sum", "yum", "bun", "fun", "gun", "nun", "pun", "run", "sun", "bus", "gus", "pus", "but", "cut", "gut", "hut", "jut", "nut", "rut", "tub", "cub", "hub", "pub", "rub", "sub"],
                    "example_sentence": "The bug is on the rug."
                }
            },
            "digraphs": {
                "sh": {
                    "pattern": "Digraph 'sh'",
                    "difficulty": "intermediate",
                    "words": ["ship", "shop", "shut", "shed", "shell", "shelf", "shock", "shack", "shark", "shift", "shin", "shag", "sham", "shred", "shrub", "dish", "fish", "wish", "rush", "bush", "cash", "dash", "mash", "bash", "wash", "mesh", "fresh"],
                    "example_sentence": "The fish swam to the ship."
                },
                "ch": {
                    "pattern": "Digraph 'ch'",
                    "difficulty": "intermediate",
                    "words": ["chip", "chop", "chat", "chin", "chap", "chest", "chess", "check", "chick", "chill", "champ", "much", "such", "rich", "which", "lunch", "bunch", "munch", "bench", "ranch", "pinch", "inch", "etch"],
                    "example_sentence": "The chick is on the bench."
                },
                "th": {
                    "pattern": "Digraph 'th'",
                    "difficulty": "intermediate",
                    "words": ["this", "that", "them", "then", "than", "thick", "thin", "think", "thank", "thud", "bath", "math", "path", "with", "moth", "cloth", "broth"],
                    "example_sentence": "This path is thick with grass."
                },
                "wh": {
                    "pattern": "Digraph 'wh'",
                    "difficulty": "intermediate",
                    "words": ["when", "what", "which", "whip", "whim", "whiff", "whack", "wham", "whisk"],
                    "example_sentence": "When did you see the whip?"
                }
            },
            "blends": {
                "l_blends": {
                    "pattern": "L-blends (bl, cl, fl, gl, pl, sl)",
                    "difficulty": "intermediate",
                    "words": ["black", "blob", "block", "blend", "bliss", "clam", "clan", "clap", "class", "clip", "clock", "flag", "flat", "flip", "flop", "glad", "glass", "glen", "plan", "plant", "plot", "plus", "slam", "slap", "sled", "slip", "slot"],
                    "example_sentence": "The black clock is on the desk."
                },
                "r_blends": {
                    "pattern": "R-blends (br, cr, dr, fr, gr, pr, tr)",
                    "difficulty": "intermediate",
                    "words": ["brad", "brag", "brick", "crab", "crack", "crib", "drip", "drop", "drum", "frog", "from", "grab", "grin", "grip", "pram", "press", "track", "trap", "trim", "trip", "trot"],
                    "example_sentence": "The frog can hop on the rock."
                },
                "s_blends": {
                    "pattern": "S-blends (sc, sk, sm, sn, sp, st, sw)",
                    "difficulty": "intermediate",
                    "words": ["scan", "scat", "skip", "skin", "skim", "skull", "smash", "smell", "smock", "snack", "snap", "snip", "snug", "span", "spell", "spend", "spin", "spot", "staff", "stand", "step", "stick", "stop", "swim", "swell", "swift"],
                    "example_sentence": "Stop and smell the fresh grass."
                }
            },
            "vowel_teams": {
                "ai_ay": {
                    "pattern": "Vowel teams 'ai' and 'ay'",
                    "difficulty": "intermediate",
                    "words": ["rain", "train", "pain", "main", "wait", "bait", "tail", "sail", "mail", "nail", "pail", "snail", "trail", "day", "say", "may", "way", "play", "stay", "tray", "clay", "gray", "pray"],
                    "example_sentence": "The snail is on the trail in the rain."
                },
                "ee_ea": {
                    "pattern": "Vowel teams 'ee' and 'ea'",
                    "difficulty": "intermediate",
                    "words": ["see", "bee", "tree", "free", "three", "green", "sleep", "sweep", "feet", "meet", "street", "sea", "tea", "pea", "read", "bead", "lead", "beat", "heat", "meat", "seat", "team", "ream", "stream"],
                    "example_sentence": "I see three green trees on the street."
                },
                "oa_ow": {
                    "pattern": "Vowel teams 'oa' and 'ow'",
                    "difficulty": "intermediate",
                    "words": ["boat", "coat", "goat", "road", "load", "toad", "soap", "soak", "oak", "roam", "foam", "moan", "low", "bow", "row", "show", "snow", "grow", "blow", "flow", "glow", "slow", "crow"],
                    "example_sentence": "The boat will float slow on the sea."
                }
            },
            "r_controlled": {
                "ar": {
                    "pattern": "R-controlled 'ar'",
                    "difficulty": "intermediate",
                    "words": ["car", "far", "bar", "jar", "tar", "star", "scar", "barn", "yarn", "dark", "bark", "mark", "park", "shark", "spark", "start", "part", "cart", "chart", "smart"],
                    "example_sentence": "The car is in the dark barn."
                },
                "or": {
                    "pattern": "R-controlled 'or'",
                    "difficulty": "intermediate",
                    "words": ["or", "for", "fork", "corn", "horn", "born", "torn", "worn", "storm", "form", "short", "sport", "port", "sort", "north", "porch"],
                    "example_sentence": "The horn is on the porch."
                },
                "er_ir_ur": {
                    "pattern": "R-controlled 'er', 'ir', 'ur'",
                    "difficulty": "intermediate",
                    "words": ["her", "fern", "term", "herd", "verb", "bird", "girl", "first", "shirt", "skirt", "third", "burn", "turn", "curl", "hurt", "nurse", "purse", "surf", "church"],
                    "example_sentence": "The girl wore her purple shirt."
                }
            }
        }

    def _initialize_activities(self) -> None:
        """Initialize FCRR activity templates by color code"""
        self.activities = {
            "purple": {
                "name": "Phonological Awareness Activities",
                "description": "Activities that develop awareness of sounds in spoken language",
                "activities": [
                    {
                        "name": "Rhyme Recognition",
                        "objective": "Identify rhyming words in spoken language",
                        "materials": ["Picture cards", "Word lists"],
                        "procedure": "Present pairs of words and ask students to identify if they rhyme"
                    },
                    {
                        "name": "Syllable Counting",
                        "objective": "Count syllables in spoken words",
                        "materials": ["Word list", "Counters"],
                        "procedure": "Say words and have students clap or count syllables"
                    },
                    {
                        "name": "Phoneme Segmentation",
                        "objective": "Break words into individual phonemes",
                        "materials": ["Sound boxes", "Counters"],
                        "procedure": "Say a word and have students push counters for each sound"
                    },
                    {
                        "name": "Phoneme Blending",
                        "objective": "Blend individual sounds to form words",
                        "materials": ["Word list"],
                        "procedure": "Say sounds separately, students blend them together"
                    }
                ]
            },
            "orange": {
                "name": "Phonics Activities",
                "description": "Activities that teach letter-sound relationships and decoding",
                "activities": [
                    {
                        "name": "Sound-Symbol Matching",
                        "objective": "Match sounds to their corresponding letters",
                        "materials": ["Letter cards", "Sound cards"],
                        "procedure": "Present sounds and have students find matching letters"
                    },
                    {
                        "name": "Word Building",
                        "objective": "Build words using letter tiles",
                        "materials": ["Letter tiles", "Word lists"],
                        "procedure": "Provide phonemes and have students build words with tiles"
                    },
                    {
                        "name": "Blending Practice",
                        "objective": "Decode words by blending sounds",
                        "materials": ["Decodable word lists"],
                        "procedure": "Present words and guide students through blending process"
                    },
                    {
                        "name": "Encoding Practice",
                        "objective": "Spell words by segmenting sounds",
                        "materials": ["Whiteboards", "Word lists"],
                        "procedure": "Say words and have students write them using known patterns"
                    }
                ]
            },
            "green": {
                "name": "Fluency Activities",
                "description": "Activities that develop automatic, accurate reading",
                "activities": [
                    {
                        "name": "Repeated Reading",
                        "objective": "Increase reading fluency through repetition",
                        "materials": ["Decodable passages"],
                        "procedure": "Students read same passage multiple times, tracking speed/accuracy"
                    },
                    {
                        "name": "Partner Reading",
                        "objective": "Practice fluency with peer support",
                        "materials": ["Decodable books"],
                        "procedure": "Students take turns reading aloud to partners"
                    },
                    {
                        "name": "Phrase Reading",
                        "objective": "Read phrases with appropriate phrasing",
                        "materials": ["Phrase cards"],
                        "procedure": "Students practice reading phrases as meaningful units"
                    },
                    {
                        "name": "Timed Reading",
                        "objective": "Build reading speed while maintaining accuracy",
                        "materials": ["Timer", "Word lists"],
                        "procedure": "Students read word lists with timing, track progress"
                    }
                ]
            }
        }

    def get_word_list(
        self,
        pattern: str,
        difficulty: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get word list for a specific phonics pattern

        Args:
            pattern: The phonics pattern (e.g., 'cvc_a', 'sh', 'ai_ay')
            difficulty: Optional difficulty filter

        Returns:
            Dictionary with word list data
        """
        # Search through all categories
        for category, patterns in self.word_lists.items():
            if pattern in patterns:
                word_data = patterns[pattern]
                if difficulty and word_data.get("difficulty") != difficulty:
                    continue
                return {
                    "success": True,
                    "pattern": pattern,
                    "category": category,
                    "data": word_data
                }

        return {
            "success": False,
            "error": f"Pattern '{pattern}' not found in database"
        }

    def get_words_by_difficulty(self, difficulty: str) -> Dict[str, Any]:
        """
        Get all word lists for a specific difficulty level

        Args:
            difficulty: Difficulty level (beginner, intermediate, advanced)

        Returns:
            Dictionary with matching word lists
        """
        matching_lists = {}

        for category, patterns in self.word_lists.items():
            for pattern_name, pattern_data in patterns.items():
                if pattern_data.get("difficulty") == difficulty:
                    if category not in matching_lists:
                        matching_lists[category] = {}
                    matching_lists[category][pattern_name] = pattern_data

        return {
            "success": True,
            "difficulty": difficulty,
            "categories": len(matching_lists),
            "word_lists": matching_lists
        }

    def get_activity_by_color(self, color: str) -> Dict[str, Any]:
        """
        Get FCRR activities by color code

        Args:
            color: Color code (purple, orange, green)

        Returns:
            Dictionary with activity data
        """
        color = color.lower()
        if color in self.activities:
            return {
                "success": True,
                "color": color,
                "data": self.activities[color]
            }

        return {
            "success": False,
            "error": f"Color code '{color}' not found. Valid codes: purple, orange, green"
        }

    def search_words(
        self,
        search_term: str,
        max_results: int = 50
    ) -> Dict[str, Any]:
        """
        Search for words across all lists

        Args:
            search_term: Term to search for
            max_results: Maximum number of results

        Returns:
            Dictionary with matching words
        """
        matches = []

        for category, patterns in self.word_lists.items():
            for pattern_name, pattern_data in patterns.items():
                words = pattern_data.get("words", [])
                for word in words:
                    if search_term.lower() in word.lower():
                        matches.append({
                            "word": word,
                            "pattern": pattern_name,
                            "category": category,
                            "difficulty": pattern_data.get("difficulty")
                        })

                        if len(matches) >= max_results:
                            break

        return {
            "success": True,
            "search_term": search_term,
            "total_matches": len(matches),
            "matches": matches[:max_results]
        }

    def get_database_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the FCRR database

        Returns:
            Dictionary with database statistics
        """
        total_patterns = sum(len(patterns) for patterns in self.word_lists.values())
        total_words = sum(
            len(pattern_data.get("words", []))
            for patterns in self.word_lists.values()
            for pattern_data in patterns.values()
        )

        return {
            "success": True,
            "total_categories": len(self.word_lists),
            "total_patterns": total_patterns,
            "total_words": total_words,
            "activity_colors": len(self.activities),
            "categories": list(self.word_lists.keys()),
            "activity_color_codes": list(self.activities.keys())
        }
