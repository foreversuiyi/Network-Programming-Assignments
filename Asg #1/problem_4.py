def problem_4(sentence):
    words = sentence.split()
    words = sorted(words, key=lambda letter: (letter[0], letter[1]))
    return words


if __name__ == '__main__':
    sentence = input("Input sentence: ")
    try:
        print("Sorted", problem_4(sentence))
    except Exception as err:
        print("Error: ", err)

