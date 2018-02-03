def problem_1(number_1, number_2):
    num = 0
    lower = min(number_1, number_2)
    upper = max(number_1, number_2)
    for i in range(lower, upper + 1):
        if i % 7 == 0 and i % 3 != 0:
            num += 1
    return num


if __name__ == '__main__':
    number_1 = input("First integer: ")
    number_2 = input("Second integer: ")
    try:
        print(problem_1(int(number_1), int(number_2)))
    except Exception as err:
        print("Error: ", err)

