
import streamlit as st
import preprocessor,helper
import matplotlib.pyplot as plt
import seaborn as sns

st.sidebar.title("Whatsapp Chat Analyzer")
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
uploaded_file = st.sidebar.file_uploader("Choose a file")
if uploaded_file is not None:
    bytes_data = uploaded_file.getvalue()
    data = bytes_data.decode("utf-8")
    df = preprocessor.preprocess(data)
    if df.empty:
        st.error("No messages found. Please upload a valid WhatsApp chat export.")
        st.stop()

    # fetch unique users
    user_list = sorted(df['user'].dropna().unique().tolist())

    if 'group_notification' in user_list:
        user_list.remove('group_notification')

    user_list.insert(0, "Overall")

    selected_user = st.sidebar.selectbox("Show analysis wrt",user_list)

    if st.sidebar.button("Show Analysis"):

        # Stats Area
        num_messages, words, num_media_messages, num_links = helper.fetch_stats(selected_user,df)
        st.title("Top Statistics")
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.header("Total Messages")
            st.title(num_messages)
        with col2:
            st.header("Total Words")
            st.title(words)
        with col3:
            st.header("Media Shared")
            st.title(num_media_messages)
        with col4:
            st.header("Links Shared")
            st.title(num_links)

        # monthly timeline
        st.title("Monthly Timeline")
        timeline = helper.monthly_timeline(selected_user,df)
        fig,ax = plt.subplots()
        ax.plot(
         timeline['time'],
        timeline['message'],
        color='green',
        marker='o',
        linewidth=2
        )
        plt.xticks(rotation=45)
        plt.tight_layout()
        st.pyplot(fig)

        # daily timeline
        st.title("Daily Timeline")
        daily_timeline = helper.daily_timeline(selected_user, df)
        fig, ax = plt.subplots()
        ax.plot(daily_timeline['only_date'], daily_timeline['message'], color='black')
        plt.xticks(rotation='vertical')
        st.pyplot(fig)

        # activity map
        st.title('Activity Map')
        col1,col2 = st.columns(2)

        with col1:
            st.header("Most busy day")
            busy_day = helper.week_activity_map(selected_user,df)
            fig,ax = plt.subplots()
            ax.bar(busy_day.index,busy_day.values,color='purple')
            plt.xticks(rotation='vertical')
            st.pyplot(fig)

        with col2:
            st.header("Most busy month")
            busy_month = helper.month_activity_map(selected_user, df)
            fig, ax = plt.subplots()
            ax.bar(busy_month.index, busy_month.values,color='orange')
            plt.xticks(rotation='vertical')
            st.pyplot(fig)

        st.title("Weekly Activity Map")
        user_heatmap = helper.activity_heatmap(selected_user,df)
        fig,ax = plt.subplots()
        ax = sns.heatmap(user_heatmap)
        st.pyplot(fig)

        # finding the busiest users in the group(Group level)
        if selected_user == 'Overall':
            st.title('Most Busy Users')
            x,new_df = helper.most_busy_users(df)
            fig, ax = plt.subplots()

            col1, col2 = st.columns(2)

            with col1:
                ax.bar(x.index, x.values,color='red')
                plt.xticks(rotation='vertical')
                st.pyplot(fig)
            with col2:
                st.dataframe(new_df)

        # WordCloud
        st.title("Wordcloud")
        df_wc = helper.create_wordcloud(selected_user,df)
        fig,ax = plt.subplots()
        ax.imshow(df_wc)
        ax.axis("off")
        st.pyplot(fig)

        # most common words
        most_common_df = helper.most_common_words(selected_user,df)

        fig,ax = plt.subplots()

        if not most_common_df.empty:
            ax.barh(most_common_df[0], most_common_df[1], color="skyblue")
            plt.tight_layout()
            st.title("Most Common Words")
            st.pyplot(fig)
        else:
            st.info("No words found.")
    

        # emoji analysis
        emoji_df = helper.emoji_helper(selected_user, df)

        st.title("Emoji Analysis")

        if emoji_df.empty:
            st.info("No emojis found.")
        else:
            col1, col2 = st.columns(2)

            with col1:
                st.dataframe(emoji_df)

            with col2:
                fig, ax = plt.subplots(figsize=(6,6))
                ax.pie(
                    emoji_df[1].head(),
                    labels=emoji_df[0].head(),
                    autopct="%1.1f%%",
                    startangle=90
                )
                ax.axis("equal")
                st.pyplot(fig)










