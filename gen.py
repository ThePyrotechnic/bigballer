from nltk.corpus import brown


def main():
    modifiers = {
        w[0]
        for w in brown.tagged_words()
        if w[1] in ("JJ", "JJ+JJ", "JJR", "NNS$", "NR$", "NN+HVZ", "OD", "RBR", "VBG")
    }
    items = {w[0] for w in brown.tagged_words() if w[1] == "NN"}
    appraisals = {
        w[0]
        for w in brown.tagged_words()
        if w[1] in ("JJ", "JJR", "JJT", "JJS", "RBR", "VBN")
    }

    print(len(modifiers), len(items), len(appraisals))
    print(len(modifiers) * len(items) * len(appraisals))

    with open("_words.py", "w", encoding="UTF-8") as words_file:
        print(f"modifiers={list(modifiers)}", file=words_file)
        print(f"items={list(items)}", file=words_file)
        print(f"appraisals={list(appraisals)}", file=words_file)


if __name__ == "__main__":
    main()
