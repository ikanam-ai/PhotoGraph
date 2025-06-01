import streamlit as st
import pandas as pd
import networkx as nx
from pyvis.network import Network
from PIL import Image
from io import BytesIO
import base64
import tempfile
import os
import matplotlib.pyplot as plt
import streamlit.components.v1 as components


st.set_page_config(layout="wide")
 
@st.cache_data
def load_data():
    df_photo = pd.read_csv("/Users/petraldoshkin/PhotoGraph/photo_map (1).csv")
    df_links = pd.read_csv("/Users/petraldoshkin/PhotoGraph/graph_edges.csv")
    df_faces = pd.read_csv("/Users/petraldoshkin/PhotoGraph/faces.csv")
    return df_photo, df_links, df_faces

df_photo, df_links, df_faces = load_data()

# Обработка данных
df_links.columns = ['source', 'target', 'weight']
photo_path_map = dict(zip(df_photo['photo_id'], df_photo['image_path']))
person_to_photos = df_faces.groupby("face_id")['photo_id'].apply(set).to_dict()

# Создание графа для статистики
G = nx.from_pandas_edgelist(df_links, 'source', 'target')
degrees = dict(G.degree())
top_nodes = sorted(degrees.items(), key=lambda x: x[1], reverse=True)[:5]
total_photos = len(df_photo)
total_people = len(person_to_photos)
total_edges = len(df_links)
album_url = "https://vk.com/album12345"  

# Словарь с путями к фотографиям топ-5 людей
top_people_photos = {
    top_nodes[0][0]: "/Users/petraldoshkin/Downloads/Ксюша 18.jpg",
    top_nodes[1][0]: "/Users/petraldoshkin/Downloads/Диденко.jpg",
    top_nodes[2][0]: "/Users/petraldoshkin/Downloads/Гоша.jpg",
    top_nodes[3][0]: "/Users/petraldoshkin/Downloads/Четвергов.jpg",
    top_nodes[4][0]: "/Users/petraldoshkin/Downloads/Попов 15.jpg",
}

# Заголовок
st.title("\U0001F465 Граф связей людей с альбома посвята")
st.write("Интерактивная визуализация социальных связей с фотографиями")

# Разделение на три колонки
col_gallery, col_main, col_stats = st.columns([1, 3, 1])

# Левая панель
with col_gallery:
    st.subheader("\U0001F5BC Избранные фото")

    gallery_images = [
        "/Users/petraldoshkin/Downloads/четвергов 1.jpg",
        "/Users/petraldoshkin/Downloads/четвергов 2.jpg",
        "/Users/petraldoshkin/Downloads/четвергов 3.jpg",
        "/Users/petraldoshkin/Downloads/четвергов 4.jpg",
        "/Users/petraldoshkin/Downloads/четвергов 5.jpg",
        "/Users/petraldoshkin/Downloads/четвергов 6.jpg",
    ]

    for path in gallery_images:
        if os.path.exists(path):
            try:
                img = Image.open(path)
                img.thumbnail((150, 150))
                st.image(img, use_container_width=True)
            except Exception:
                st.error(f"Ошибка при загрузке {os.path.basename(path)}")
        else:
            st.warning(f"Файл не найден: {os.path.basename(path)}")

# Правая панель
with col_stats:
    st.subheader("\U0001F4CA Статистика альбома")
    st.metric("\U0001F4F8 Всего фотографий", total_photos)
    st.metric("\U0001F464 Всего найдено лиц(уникальных около 85)", total_people)
    st.metric("\U0001F517 Всего связей", total_edges)

    st.divider()
    st.subheader("\U0001F517 Ссылка на альбом")
    st.markdown(f"[Перейти к альбому]({album_url})")

    st.divider()
    st.subheader("\U0001F3C6 Топ-5 активных людей")
    for node_id, degree in top_nodes:
        st.markdown(f"### \U0001F464 Человек {node_id}")
        st.markdown(f"**Связей:** {degree}")
        photo_path = top_people_photos.get(node_id)
        if photo_path and os.path.exists(photo_path):
            try:
                img = Image.open(photo_path)
                img.thumbnail((250, 250))
                st.image(img, use_container_width=True)
            except Exception as e:
                st.error(f"Ошибка загрузки фото для человека {node_id}: {e}")
        else:
            st.warning("Фото для этого человека не найдено")
        st.divider()

    st.subheader("\U0001F4C8 Распределение связей")
    degree_counts = pd.Series(degrees).value_counts().sort_index()
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.bar(degree_counts.index.astype(str), degree_counts.values, color='skyblue')
    ax.set_title("Количество людей по числу связей")
    ax.set_xlabel("Количество связей")
    ax.set_ylabel("Всего найдено лиц")
    plt.xticks(rotation=45)
    st.pyplot(fig)

# Центральная панель: граф
with col_main:
    st.subheader("\U0001F310 Социальный граф связей")
    st.info("Наведите курсор на узел, чтобы увидеть фотографии человека")

    net = Network(height="800px", width="100%", bgcolor="#ffffff", font_color="#333333")

    net.set_options("""
    {
      "nodes": {
        "borderWidth": 2,
        "size": 40,
        "font": {
          "size": 14,
          "face": "Tahoma",
          "strokeWidth": 2
        },
        "shape": "dot"
      },
      "edges": {
        "color": {"inherit": true},
        "smooth": false,
        "width": 2
      },
      "physics": {
        "barnesHut": {
          "gravitationalConstant": -20000,
          "centralGravity": 0.3,
          "springLength": 250
        },
        "minVelocity": 0.75
      },
      "interaction": {
        "hover": true,
        "tooltipDelay": 200
      },
      "layout": {
        "improvedLayout": true
      }
    }
    """)

    progress_bar = st.progress(0)
    total_nodes = len(G.nodes)

    for i, node in enumerate(G.nodes):
        photo_ids = person_to_photos.get(node, set())
        thumbnails_html = ""
        for pid in sorted(photo_ids)[:4]:
            image_path = photo_path_map.get(pid)
            if not image_path or not os.path.exists(image_path):
                continue
            try:
                img = Image.open(image_path)
                img.thumbnail((120, 120))
                buf = BytesIO()
                img.save(buf, format="JPEG")
                encoded = base64.b64encode(buf.getvalue()).decode()
                thumbnails_html += f'<img src="data:image/jpeg;base64,{encoded}" style="margin:5px;border-radius:6px;box-shadow:0 2px 4px rgba(0,0,0,0.2);">'
            except Exception:
                continue

        size = 40 if node in [n[0] for n in top_nodes] else 30
        net.add_node(node, label=str(node), title=thumbnails_html, size=size)
        progress_bar.progress((i + 1) / total_nodes)

    for edge in G.edges:
        net.add_edge(edge[0], edge[1], width=3)

    html_content = net.generate_html()

    with tempfile.NamedTemporaryFile(delete=False, suffix=".html", mode="w", encoding="utf-8") as tmp_file:
        tmp_file.write(html_content)
        html_path = tmp_file.name

    with open(html_path, 'r', encoding='utf-8') as f:
        html = f.read()

    components.html(html, height=800, scrolling=False)
    os.remove(html_path)

# Стили
st.markdown("""
<style>
    .block-container {
        padding-top: 2rem;
    }
    .stImage > img {
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.2);
        margin-bottom: 12px;
    }
    .stApp {
        background-color: #a9c4ae;
    }
</style>
""", unsafe_allow_html=True)

st.divider()
st.caption("© 2023 Анализ социальных связей | Данные из альбома посвята")

