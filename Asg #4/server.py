import nltk
import pandas as pd
import numpy as np
from flask import jsonify
from flask import Flask
from flask import current_app
from flask import request
import time
import datetime

file = 'imdb_top1000.csv'
movie_frames = pd.read_csv(file)
movie_frames.insert(0, 'comments', [list() for x in range(len(movie_frames.index))])
titles = movie_frames['Title']
title_inv_index = {}
for index, title in enumerate(titles):
    tmp_str = nltk.word_tokenize(title)
    for word in tmp_str:
        if word in title_inv_index:
            if index not in title_inv_index[word]:
                title_inv_index[word].append(index)
        else:
            title_inv_index[word] = []
            title_inv_index[word].append(index)
actors = movie_frames['Actors']
actor_inv_index = {}
title_actor_inv_index = title_inv_index
for index, actor in enumerate(actors):
    tmp_str = nltk.word_tokenize(actor)
    for word in tmp_str:
        if word in title_actor_inv_index:
            if index not in title_actor_inv_index[word]:
                title_actor_inv_index[word].append(index)
        else:
            title_actor_inv_index[word] = []
            title_actor_inv_index[word].append(index)
        if word in actor_inv_index:
            if index not in actor_inv_index[word]:
                actor_inv_index[word].append(index)
        else:
            actor_inv_index[word] = []
            actor_inv_index[word].append(index)

app = Flask(__name__)
app.movies = movie_frames
app.title_index = title_inv_index
app.actor_index = actor_inv_index
app.title_actor_index = title_actor_inv_index


def movie_return_type(data_frame, method):
    if method == 'search':
        return_type = {"Actors": data_frame["Actors"],
                       "Director": data_frame["Director"],
                       "Genre": data_frame["Genre"],
                       "Rating": float(data_frame["Rating"]),
                       "Revenue (Millions)": float(data_frame["Revenue (Millions)"]),
                       "Title": data_frame["Title"],
                       "Year": int(data_frame["Year"]),
                       "id": int(data_frame["Rank"]) - 1}
    elif method == 'movie'or method == 'comment':
        return_type = {"Actors": data_frame["Actors"],
                       "Description": data_frame["Description"],
                       "Director": data_frame["Director"],
                       "Genre": data_frame["Genre"],
                       "Metascore": float(data_frame["Metascore"]),
                       "Rank": int(data_frame["Rank"]),
                       "Rating": float(data_frame["Rating"]),
                       "Revenue (Millions)": float(data_frame["Revenue (Millions)"]),
                       "Runtime (Minutes)": int(data_frame["Runtime (Minutes)"]),
                       "Title": data_frame["Title"],
                       "Votes": int(data_frame["Votes"]),
                       "Year": int(data_frame["Year"]),
                       "comments": data_frame["comments"],
                       "id": int(data_frame["Rank"]) - 1}
        if np.isnan(data_frame["Metascore"]):
            return_type["Metascore"] = float(0.0)
    else:
        return_type = {}
    if np.isnan(data_frame["Revenue (Millions)"]):
        return_type["Revenue (Millions)"] = 0.0
    return return_type


@app.route('/movie/<int:movie_id>', methods=['GET'])
def find_movie(movie_id):
    return jsonify(movie_return_type(current_app.movies.loc[int(movie_id)], method='movie'))


@app.route('/search', methods=['GET'])
def search_movie():
    query_string = request.args.get("query").capitalize()
    query_attribute = request.args.get("attribute")
    query_sort = request.args.get("sortby").capitalize()
    query_order = request.args.get("order")
    query_index = {"title": current_app.title_index,
                   "actor": current_app.actor_index,
                   "both": current_app.title_actor_index}[query_attribute]
    if query_string in query_index:
        tmp_index = query_index[query_string]
        sort_reverse = {"descending": True, "ascending": False}[query_order]
        final_index = sorted(tmp_index, key=lambda x: current_app.movies[query_sort][x], reverse=sort_reverse)
        if len(final_index) > 10:
            return_index = final_index[0:10]
        else:
            return_index = final_index
        return_movies = {"movies": []}
        for r_index in return_index:
            return_movies["movies"].append(movie_return_type(current_app.movies.loc[r_index], method='search'))
        return jsonify(return_movies)


@app.route('/comment', methods=['POST'])
def make_comment():
    user_name = request.form.get("user_name")
    movie_id = request.form.get("movie_id")
    comment = request.form.get("comment")
    ts = time.time()
    st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
    tmp_comment = {"comment": comment, "timestamp": st, "user_name": user_name}
    current_app.movies.loc[int(movie_id)]["comments"].append(tmp_comment)
    return jsonify(movie_return_type(current_app.movies.loc[int(movie_id)], method='comment'))


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=50000)
