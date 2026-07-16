import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns

import dataprocessing
import txtprocessor


st.set_page_config(
    page_title="WhatsApp Chat Analyzer",
    page_icon="💬",
    layout="wide"
)

st.title("💬 WhatsApp Chat Analyzer")

st.sidebar.header("Upload Chat")

uploaded_file = st.sidebar.file_uploader(
    "Choose exported WhatsApp chat (.txt)",
    type=["txt"]
)

if uploaded_file is None:
    st.info("Upload a WhatsApp exported chat to begin.")
    st.stop()

try:
    data = uploaded_file.read().decode("utf-8")
except UnicodeDecodeError:
    data = uploaded_file.read().decode("utf-8", errors="ignore")

df = dataprocessing.preprocess(data)

if df.empty:
    st.error("No valid WhatsApp messages found.")
    st.stop()

# User selection
user_list = sorted(df["user"].dropna().unique())

if "group_notification" in user_list:
    user_list.remove("group_notification")

user_list.insert(0, "Overall")

selected_user = st.sidebar.selectbox(
    "Analyze",
    user_list
)

if st.sidebar.button("Show Analysis", use_container_width=True):

    # ---------------- Top Stats ----------------
    num_messages, words, media, links = txtprocessor.fetch_stats(selected_user, df)

    st.header("Top Statistics")

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("Messages", num_messages)
    c2.metric("Words", words)
    c3.metric("Media", media)
    c4.metric("Links", links)

    # ---------------- Monthly Timeline ----------------
    st.header("Monthly Timeline")

    timeline = txtprocessor.monthly_timeline(selected_user, df)

    fig, ax = plt.subplots(figsize=(10, 4))
    ax.plot(
        timeline["time"],
        timeline["message"],
        marker="o"
    )
    plt.xticks(rotation=45)
    plt.tight_layout()
    st.pyplot(fig)

    # ---------------- Daily Timeline ----------------
    st.header("Daily Timeline")

    daily = txtprocessor.daily_timeline(selected_user, df)

    fig, ax = plt.subplots(figsize=(10, 4))
    ax.plot(daily["only_date"], daily["message"])
    plt.xticks(rotation=45)
    plt.tight_layout()
    st.pyplot(fig)

    # ---------------- Activity ----------------
    st.header("Activity Map")

    c1, c2 = st.columns(2)

    with c1:
        busy_day = txtprocessor.week_activity_map(selected_user, df)

        fig, ax = plt.subplots()
        ax.bar(busy_day.index, busy_day.values)
        plt.xticks(rotation=45)
        st.pyplot(fig)

    with c2:
        busy_month = txtprocessor.month_activity_map(selected_user, df)

        fig, ax = plt.subplots()
        ax.bar(busy_month.index, busy_month.values)
        plt.xticks(rotation=45)
        st.pyplot(fig)

    # ---------------- Heatmap ----------------
    st.header("Weekly Heatmap")

    heatmap = txtprocessor.activity_heatmap(selected_user, df)

    fig, ax = plt.subplots(figsize=(10, 5))
    sns.heatmap(heatmap, ax=ax)
    st.pyplot(fig)

    # ---------------- Busy Users ----------------
    if selected_user == "Overall":

        st.header("Most Busy Users")

        counts, busy_df = txtprocessor.most_busy_users(df)

        c1, c2 = st.columns(2)

        with c1:
            fig, ax = plt.subplots()
            ax.bar(counts.index, counts.values)
            plt.xticks(rotation=45)
            st.pyplot(fig)

        with c2:
            st.dataframe(busy_df, use_container_width=True)

    # ---------------- Word Cloud ----------------
    st.header("Word Cloud")

    wc = txtprocessor.create_wordcloud(selected_user, df)

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.imshow(wc)
    ax.axis("off")
    st.pyplot(fig)

    # ---------------- Common Words ----------------
    st.header("Most Common Words")

    common = txtprocessor.most_common_words(selected_user, df)

    if common.empty:
        st.info("No words found.")
    else:
        fig, ax = plt.subplots(figsize=(8, 5))
        ax.barh(common[0], common[1])
        plt.tight_layout()
        st.pyplot(fig)

    # ---------------- Emoji Analysis ----------------
    st.header("Emoji Analysis")

    emoji_df = txtprocessor.emoji_helper(selected_user, df)

    if emoji_df.empty:
        st.info("No emojis found.")
    else:
        c1, c2 = st.columns(2)

        with c1:
            st.dataframe(emoji_df)

        with c2:
            fig, ax = plt.subplots(figsize=(6, 6))
            ax.pie(
                emoji_df[1].head(),
                labels=emoji_df[0].head(),
                autopct="%1.1f%%"
            )
            ax.axis("equal")
            st.pyplot(fig)
