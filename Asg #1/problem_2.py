def problem_2(n):
    if isinstance(n, int) and 0 <= n <= 9:
        return n + 111 * n + 11111 * n
    else:
        return 0


if __name__ == '__main__':
    n = input("Integer between 1 - 9 :")
    try:
        print(problem_2(int(n)))
    except Exception as err:
        print("Error: ", err)

