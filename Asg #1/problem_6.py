def problem_6(path_to_file):
    output = []
    f = open(path_to_file, "r")
    keywords = f.readline().strip('\n').split(',')
    for contents in f.readlines():
        single_member = {}
        for x, y in zip(keywords, contents.strip('\n').split(',')):
            single_member[x] = y
        output.append(single_member)
    return output


if __name__ == '__main__':
    path_to_file = input("Path to file: ")
    try:
        print(problem_6(path_to_file))
    except Exception as err:
        print("Error: ", err)

