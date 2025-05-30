# PhotoGraph
---

## 1. Описание датасета

В качестве исходных данных используется набор фотографий из одного или нескольких альбомов социальной сети VK (например, альбом по адресу `https://vk.com/albums-130344439`). Каждая фотография — это изображение, на котором могут присутствовать один или несколько лиц. Для каждого лица на фото необходимо извлечь и сохранить следующие данные:

* **photo\_id** — уникальный идентификатор фотографии в ВК;
* **face\_id** — уникальный идентификатор обнаруженного лица на фото;
* **embedding** — числовой вектор признаков лица (например, 128‑мерный), получаемый из модели распознавания лиц;
* **bbox** — координаты ограничивающего прямоугольника лица на изображении (x, y, width, height);
* **album\_id** — идентификатор альбома;
* **source\_url** — прямая ссылка на фотографию.

Все эти данные сохраняются в базе данных или в виде таблицы (CSV/Parquet) для последующей агрегации и построения социального графа по «встречам» лиц на разных фотографиях.

---

## 2. Задание: что нужно сделать

1. **Скачивание и подготовка фотографий**

   * Получить список фотографий из указанных альбомов VK через официальный API или веб‑скрейпинг.
   * Сохранить оригинальные изображения локально или в облачном хранилище.

2. **Детекция и векторизация лиц**

   * Для каждой фотографии выполнить детекцию лиц и получить координаты каждого обнаруженного лица.
   * Прогнать каждый обрезанный регион лица через модель для извлечения эмбеддингов (face embeddings).
   * Сохранить все эмбеддинги вместе с идентификаторами фото и лиц в БД.

3. **Построение «социального графа»**

   * Сравнивать новые эмбеддинги с уже сохранёнными: если расстояние между векторами ниже заданного порога, считать, что лицо уже встречалось ранее, и использовать один и тот же `person_id`.
   * Для каждой пары лиц, которые одновременно присутствуют на одной фотографии, наращивать вес связи между ними (количество «встреч»).
   * Хранить в отдельной таблице ребра графа:

     ```
     person_id_1 | person_id_2 | cooccurrence_count
     ```

4. **Визуализация результатов**

   * Для одного альбома или одного года публикации сформировать граф, где узлы — уникальные персоны, а рёбра — сила их связей (число совместных фото).
   * Визуализировать этот граф при помощи библиотеки для интерактивных сетей (например, PyVis, NetworkX + Bokeh или Streamlit Components).

5. **Интерактивный дашборд**

   * Собрать **Streamlit**‑приложение, где можно:

     * Выбирать альбом(ы);
     * Смотреть агрегированную статистику по числу лиц, числу связей, наиболее «социально активных» персон;
     * Отображать интерактивный граф;

---

## 3. Ссылки и представление конечного результата

* **VK‑альбом с исходными фото:**
  `https://vk.com/albums-130344439`
* **Пример подхода к распознаванию и связыванию лиц:**
  статья на Habr: [https://habr.com/ru/companies/okkamgroup/articles/509204/](https://habr.com/ru/companies/okkamgroup/articles/509204/)
* **Полезно для ознакомления:**
  Иканам гранд ресерч: [https://nbviewer.org/github/FUlyankin/ekanam_grand_research/blob/master/Posts/0.%20Introduction.ipynb](https://nbviewer.org/github/FUlyankin/ekanam_grand_research/blob/master/Posts/0.%20Introduction.ipynb)
* **Основные используемые инструменты и библиотеки:**

  * Работа с VK API: `vk_api` или `requests` + BeautifulSoup
  * Детекция/эмбеддинги лиц: `face_recognition`, `dlib`, `InsightFace`
  * Хранение данных: Pandas DataFrame
  * Построение графа: NetworkX, PyVis
  * Дашборд: Streamlit

## 4. Презентация проекта

Презентация с основной инфой 

Продолжительность: 10-15 минут  
