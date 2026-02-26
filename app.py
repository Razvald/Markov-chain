# app.py
import os
import re
import random
import streamlit as st

# --- Helper Functions ---

def tokenize_with_starts(text: str):
    starts = set()
    raw_tokens = re.findall(r"[А-Яа-яA-Za-z]+|[.!?]", text)
    tokens = []
    new_sentence = True
    for tok in raw_tokens:
        if tok in ".!?":
            new_sentence = True
            continue
        word = tok.lower()
        tokens.append(word)
        if new_sentence:
            starts.add(word)
            new_sentence = False
    return tokens, starts

def build_model(tokens):
    transition = {}
    for i in range(len(tokens) - 2):
        key = (tokens[i], tokens[i+1])
        next_word = tokens[i+2]
        if key not in transition:
            transition[key] = []
        transition[key].append(next_word)
    return transition

def get_start_pairs(tokens, start_words):
    start_pairs = []
    for i in range(len(tokens) - 1):
        if tokens[i] in start_words:
            start_pairs.append((tokens[i], tokens[i+1]))
    return start_pairs

def generate_text(transition, start_pairs, count):
    w1, w2 = random.choice(start_pairs)
    result = [w1.capitalize(), w2]

    for _ in range(count - 2):
        next_words = transition.get((w1, w2))
        if not next_words:
            break

        w3 = random.choice(next_words)
        result.append(w3)

        w1, w2 = w2, w3

    return " ".join(result) + '.'

def load_corpus_from_folder(folder_path):
    corpus = ""
    for filename in os.listdir(folder_path):
        if filename.endswith(".txt"):
            with open(os.path.join(folder_path, filename), "r", encoding="utf-8") as f:
                corpus += " " + f.read()
    return corpus

# --- Streamlit UI ---

st.title("Генератор текстов на основе цепей Маркова")
st.write("Загрузите тексты, настройте длину и сгенерируйте псевдореалистичный текст.")

uploaded_files = st.file_uploader("Загрузите один или несколько .txt файлов", type="txt", accept_multiple_files=True)

corpus = ""
if uploaded_files:
    for uploaded_file in uploaded_files:
        corpus += " " + uploaded_file.read().decode("utf-8")
    tokens, start_words = tokenize_with_starts(corpus)
    transition = build_model(tokens)
    start_pairs = get_start_pairs(tokens, start_words)
    st.success(f"Загружено {len(tokens)} токенов из {len(uploaded_files)} файлов")

length = st.slider("Длина текста (слов)", min_value=20, max_value=500, value=80, step=10)

if st.button("Сгенерировать текст"):
    if not uploaded_files:
        st.error("Сначала загрузите файлы!")
    else:
        output = generate_text(transition, start_pairs, length)
        st.text_area("Сгенерированный текст", value=output, height=300)

if st.button("Сохранить текст в файл"):
    if not uploaded_files:
        st.error("Сначала сгенерируйте текст!")
    else:
        with open("generated_text.txt", "w", encoding="utf-8") as f:
            f.write(output)
        st.success("Текст сохранен")