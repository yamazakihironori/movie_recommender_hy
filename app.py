import streamlit as st
import pandas as pd
import numpy as np
import gensim

st.title('映画レコメンド')

# 映画情報の読み込み
movies = pd.read_csv("data/movies.tsv", sep="\t")

# 学習済みのitem2vecモデルの読み込み
model = gensim.models.word2vec.Word2Vec.load("data/item2vec.model")

# 映画IDとタイトルを辞書型に変換
movie_titles = movies["title"].tolist()
movie_ids = movies["movie_id"].tolist()
movie_id_to_title = dict(zip(movie_ids, movie_titles))
movie_title_to_id = dict(zip(movie_titles, movie_ids))

st.markdown("## 1本の映画に対して似ている映画を表示する")
selected_movie = st.selectbox("映画を選んでください", movie_titles)
selected_movie_id = movie_title_to_id[selected_movie]
st.write(f"あなたが選択した映画は{selected_movie}(id={selected_movie_id})です")

# 似ている映画を表示
st.markdown(f"### {selected_movie}に似ている映画")
results = []
for movie_id, score in model.wv.most_similar(selected_movie_id):
    title = movie_id_to_title[movie_id]
    results.append({"movie_id":movie_id, "title": title, "score": score})
results = pd.DataFrame(results)
st.write(results)


st.markdown("## 複数の映画を選んでおすすめの映画を表示する")

selected_movies = st.multiselect("映画を複数選んでください", movie_titles)
selected_movie_ids = [movie_title_to_id[movie] for movie in selected_movies]
vectors = [model.wv.get_vector(movie_id) for movie_id in selected_movie_ids]
if len(selected_movies) > 0:
    user_vector = np.mean(vectors, axis=0)
    st.markdown(f"### おすすめの映画")
    recommend_results = []
    for movie_id, score in model.wv.most_similar(user_vector):
        title = movie_id_to_title[movie_id]
        recommend_results.append({"movie_id":movie_id, "title": title, "score": score})
    recommend_results = pd.DataFrame(recommend_results)
    st.write(recommend_results)



usr_assessment = [1, 2, 3, 4, 5]
assesment_to_wait = {1:-2, 2:-1, 3:1, 4:2, 5:3}

def add_container(i):
    with st.container():
        col1, col2 = st.columns(2)
    with col1:
        movie_select = st.selectbox("映画を選んでください", movie_titles, key=3*i)
    with col2:
        assesment_select = st.selectbox("評価を選んでください", usr_assessment, key=3*i+1)
    movie_assesment_list.append((movie_title_to_id[movie_select], assesment_select))

st.markdown("## 映画を評価しておすすめの映画を表示する")

movie_assesment_list = []
if 'count' not in st.session_state:
    st.session_state["count"] = 0
with st.container():
    col1, col2 = st.columns(2)
with col1:
    if st.button("追加"):
        st.session_state["count"] += 1
with col2:
    if st.button("削除"):
        if st.session_state["count"] > 0:
            st.session_state["count"] -= 1 
with st.container():
    col1, col2 = st.columns(2)
with col1:
    movie_select = st.selectbox("映画を選んでください", movie_titles, key=1)
with col2:
    assesment_select = st.selectbox("評価を選んでください", usr_assessment, key=2)
movie_assesment_list.append((movie_title_to_id[movie_select], assesment_select))
for i in range(st.session_state["count"]):
    add_container(i+1)
    
ass_vectors = [model.wv.get_vector(movie_ass[0])*assesment_to_wait[movie_ass[1]] for movie_ass in movie_assesment_list]
if len(movie_assesment_list) > 0:
    ass_user_vector = np.mean(ass_vectors, axis=0)
    st.markdown(f"### おすすめの映画")
    ass_recommend_results = []
    for movie_id, score in model.wv.most_similar(ass_user_vector):
        title = movie_id_to_title[movie_id]
        ass_recommend_results.append({"movie_id":movie_id, "title": title, "score": score})
    ass_recommend_results = pd.DataFrame(ass_recommend_results)
    st.write(ass_recommend_results)