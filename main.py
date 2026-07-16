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
st.markdown("""
<style>
.main {
    background-color: #f8fafc;
}

[data-testid="stMetric"] {
    background-color: white;
    border-radius: 12px;
    padding: 15px;
    box-shadow: 0px 2px 10px rgba(0,0,0,0.08);
}

h1,h2,h3 {
    color:#075E54;
}

.block-container {
    padding-top:2rem;
    padding-bottom:2rem;
}

div.stButton > button:first-child{
    background:#25D366;
    color:white;
    border:none;
    border-radius:10px;
    font-weight:bold;
}

div.stButton > button:first-child:hover{
    background:#128C7E;
}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<h1 style='text-align:center;color:#25D366;'>
💬 WhatsApp Chat Analyzer
</h1>

<p style='text-align:center;color:gray;font-size:18px'>
Visualize chats, emojis, links, media and user activity
</p>
""", unsafe_allow_html=True)

st.sidebar.markdown("# 📱 WhatsApp Analyzer")
st.sidebar.markdown("---")

st.sidebar.info(
    "Upload an exported WhatsApp chat to generate analytics."
)

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

    c1, c2, c3 = st.columns(3)

    c1.metric("💬 Messages", f"{num_messages:,}")
    c2.metric("📝 Words", f"{words:,}")
    c3.metric("🔗 Links", f"{links:,}")

    # ---------------- Monthly Timeline ----------------
    st.divider()
    st.subheader("📈 Chat Timeline")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### Monthly Timeline")
        timeline = txtprocessor.monthly_timeline(selected_user, df)

        fig, ax = plt.subplots(figsize=(6,3.5))
        ax.plot(
            timeline["time"],
            timeline["message"],
            marker="o",
            linewidth=2,
            color="#25D366"
        )
        ax.grid(alpha=0.3)
        plt.xticks(rotation=30)
        plt.tight_layout()
        st.pyplot(fig, use_container_width=True)

    with col2:
        st.markdown("#### Daily Timeline")

        daily = txtprocessor.daily_timeline(selected_user, df)

        fig, ax = plt.subplots(figsize=(6,3.5))
        ax.plot(
            daily["only_date"],
            daily["message"],
            linewidth=2,
            color="#128C7E"
        )
        ax.grid(alpha=0.3)
        plt.xticks(rotation=30)
        plt.tight_layout()
        st.pyplot(fig, use_container_width=True)

        # ---------------- Activity ----------------
    st.divider()
    st.subheader("📊 Activity Overview")

    col1, col2 = st.columns([2,1])

    with col1:
            st.markdown("#### Weekly Activity")

            busy_day = txtprocessor.week_activity_map(selected_user, df)

            fig, ax = plt.subplots(figsize=(6,3.5))
            ax.bar(busy_day.index, busy_day.values)
            plt.xticks(rotation=30)
            plt.tight_layout()
            st.pyplot(fig, use_container_width=True)

    with col2:
            st.markdown("#### Monthly Activity")

            busy_month = txtprocessor.month_activity_map(selected_user, df)

            fig, ax = plt.subplots(figsize=(6,3.5))
            ax.bar(busy_month.index, busy_month.values)
            plt.xticks(rotation=30)
            plt.tight_layout()
            st.pyplot(fig, use_container_width=True)
    # ---------------- Heatmap ----------------
    st.divider()
    st.subheader("🔥 Weekly Heatmap")

    heatmap = txtprocessor.activity_heatmap(selected_user, df)

    fig, ax = plt.subplots(figsize=(8,4))
    sns.heatmap(heatmap, ax=ax)
    plt.tight_layout()

    st.pyplot(fig, use_container_width=True)
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
    st.divider()
    st.subheader("☁ Text Analysis")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### Word Cloud")

        wc = txtprocessor.create_wordcloud(selected_user, df)

        fig, ax = plt.subplots(figsize=(6,4))
        ax.imshow(wc)
        ax.axis("off")
        st.pyplot(fig, use_container_width=True)

    with col2:
        st.markdown("#### Most Common Words")

        common = txtprocessor.most_common_words(selected_user, df)

        if not common.empty:
            fig, ax = plt.subplots(figsize=(6,4))
            ax.barh(common[0], common[1])
            plt.tight_layout()
            st.pyplot(fig, use_container_width=True)
        else:
            st.info("No words found.")

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

st.divider()

st.markdown("""
<div style="
text-align:center;
padding:20px;
font-size:15px;
color:#666;
">

Made with <b>Streamlit</b> by <b>Olivia</b><br><br>

📱 WhatsApp Chat Analyzer • 2026

</div>
""", unsafe_allow_html=True)
