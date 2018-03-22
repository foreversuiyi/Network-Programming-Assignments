import sys
import requests


def movies_print(in_movies):
    print("{")
    print('''"movies": [''')
    for num in range(len(in_movies["movies"])):
        dict_print(in_movies["movies"][num])
        if num < len(in_movies["movies"]) - 1:
            print(",")
        else:
            print("")


def dict_print(in_dict):
    str2num = {"Metascore":float,
               "Rank": int,
               "Rating": float,
               "Revenue (Millions)": float,
               "Runtime (Minutes)": int,
               "Votes": int,
               "Year": int,
               "id": int}
    print("{")
    for i, (x, y) in enumerate(in_dict.items()):
        print("\t", end="")
        print('''"%s": ''' % x, end="")
        if x in str2num:
            print(str2num[x](y), end="")
        elif x == "comments":
            if len(y) > 0:
                print("[")
                for num in range(len(y)):
                    print("\t\t{")
                    for j, (m, n) in enumerate(y[num].items()):
                        print('''\t\t\t"%s": "%s"''' % (m, n), end="")
                        if j < len(y[num]) - 1:
                            print(",")
                        else:
                            print("")
                    print("\t\t}", end="")
                    if num < len(y) - 1:
                        print(",")
                    else:
                        print("")
                print("\t]", end="")
            else:
                print("[]", end="")
        else:
            print('''"%s"''' % y, end="")
        if i < len(in_dict) - 1:
            print(",")
        else:
            print("")
    print("}", end="")


try:
    request = sys.argv[3]
    method = {"search": "GET", "movie": "GET", "comment": "POST"}[request]
    if method == "POST":
        params = tuple(sys.argv[1:4])
        tmp = input("What is your comment? <User inputs his/her comment here and press enter>")
        msg = "http://%s:%s/%s" % params
        info = {'user_name': sys.argv[4], 'movie_id': sys.argv[5], 'comment': tmp}
        r = requests.post(msg, data=info)
        dict_print(r.json())
    elif method == "GET":
        if request == 'search':
            params = tuple(sys.argv[1:])
            msg = "http://%s:%s/%s?query=%s&attribute=%s&sortby=%s&order=%s" % params
            r = requests.get(msg)
            movies_print(r.json())
        elif request == 'movie':
            params = tuple(sys.argv[1:])
            msg = "http://%s:%s/%s/%s" % params
            r = requests.get(msg)
            dict_print(r.json())
finally:
    pass
