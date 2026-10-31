import os

import pandas as pd
import plotly.express as px
import streamlit as st

from labeler import label_comment, LABELS, GUIDE

# ---- Settings ----------------------------------------------------------
TITLE = "The Fancy Restaurant"
LOGO = "logo.png"
CSV_FILE = "feedback.csv"
LOW_RATING, HIGH_RATING = 2, 4
COLORS = {"food": "#8C2F39", "pricing": "#C9A227", "service": "#2E5E4E", "atmosphere": "#5B4B8A", "unclear": "#B0B0B0"}

# ------------------------------------------------------------------------

st.set_page_config(page_title=TITLE, page_icon=LOGO, layout="wide")
st.image(LOGO, width=90)
st.title(TITLE)
st.caption("Customers leave feedback on this fancy high-end restaurant. This app labels it and saves it. The owner analyzes it later.")

# Load the saved feedback, or start with an empty table
if os.path.exists(CSV_FILE):
    df = pd.read_csv(CSV_FILE)
else:
    df = pd.DataFrame(columns=["comment", "rating", "label"])

tab_customer, tab_owner = st.tabs(["Customer: leave feedback", "Owner: analyze the feedback"])

# ---- Customer tab: type feedback, pick stars, get a label, save --------------
with tab_customer:
    st.subheader("How was your evening with us?")
    with st.form("feedback_form", clear_on_submit=True):
        comment = st.text_area("Your comment")
        stars = st.feedback("stars")          # nothing until clicked, then 0 to 4
        submitted = st.form_submit_button("Send feedback")

    if submitted:
        if not comment.strip() or stars is None:
            st.error("Please type a comment and choose a star rating.")
        else:
            label = label_comment(comment.strip())
            new_row = pd.DataFrame([{"comment": comment.strip(), "rating": stars + 1, "label": label}])
            pd.concat([df, new_row], ignore_index=True).to_csv(CSV_FILE, index=False)
            df = pd.read_csv(CSV_FILE)
            st.success("Thank you for your feedback!")
            st.caption(f"Behind the scenes, the app labeled it: {label}")

# ---- Owner tab: which part of the experience is hurting ratings? -------------
with tab_owner:
    if df.empty:
        st.info("No feedback yet. Switch to the guest tab and add the first comment.")
    else:
        # Manual review: the label is unclear, or the rating is low
        review = (df["label"] == "unclear") | (df["rating"] <= LOW_RATING)

        # ---- Key numbers ----
        st.subheader("What are customers saying?")
        m1, m2, m3 = st.columns(3)
        m1.metric("Total Comments Received", len(df))
        m2.metric("Average stars", f"{df['rating'].mean():.1f}")
        m3.metric("Need manual review", int(review.sum()))


        # ---- Graphs ----
        col1, col2 = st.columns(2)

        with col1:
            st.caption("Number of comments by category")
            counts = df["label"].value_counts().rename_axis("label").reset_index(name="count")
            fig = px.bar(counts, x="label", y="count", color="label", text="count",
                         color_discrete_map=COLORS)
            fig.update_layout(showlegend=False, xaxis_title=None, yaxis_title="Comments")
            st.plotly_chart(fig, width="stretch")

        with col2:
            st.caption("Average stars by category")
            avg = df.groupby("label")["rating"].mean().round(1).reset_index().sort_values("rating")
            fig = px.bar(avg, x="label", y="rating", color="label", text="rating",
                         color_discrete_map=COLORS, range_y=[0, 5])
            fig.update_layout(showlegend=False, xaxis_title=None, yaxis_title="Average stars")
            st.plotly_chart(fig, width="stretch")


        # ---- Manual review list, every comment shown in full ----
        st.subheader(f"Comments that need manual review ({int(review.sum())})")
        st.caption(f"The label is unclear, or the guest gave {LOW_RATING} stars or fewer. "
                   "Lowest ratings first.")
        
        to_review = df[review].sort_values("rating")
        if to_review.empty:
            st.success("Nothing to review right now.")
        for _, row in to_review.iterrows():
            with st.container(border=True):
                st.markdown(f"**{row['label'].capitalize()}** · {'★' * int(row['rating'])}")
                st.markdown(row["comment"].replace("$", "\\$"))   # "$" would otherwise turn into math


        with st.expander("All feedback"):
            st.dataframe(df, hide_index=True, width="stretch")
        st.download_button("Download CSV", df.to_csv(index=False), file_name="feedback.csv")
        st.caption("On the free Streamlit Cloud, the saved file can disappear when the app restarts. "
                   "Download your CSV to keep it.")
