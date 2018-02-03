def problem_5(sentence):
    output = []
    words = sentence.lower().split()
    words_list = []
    words_count = []
    for word in words:
        if word in words_list:
            words_count[words_list.index(word)] += 1
        else:
            words_list.append(word)
            words_count.append(1)
    for w_l, w_c in zip(words_list, words_count):
        output.append((w_c, w_l))
    output = sorted(output, key=lambda x: x[0], reverse=True)
    if len(output) >= 5:
        return output[0:5]
    else:
        return output


if __name__ == '__main__':
    sentence = input("Input sentence: ")
    try:
        print(problem_5(sentence))
    except Exception as err:
        print("Error: ", err)

