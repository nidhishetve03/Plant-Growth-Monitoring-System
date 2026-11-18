
from pathlib import Path
from datetime import date

import pandas as pd
import plotly.express as px
import streamlit as st

# Page settings
st.set_page_config(
    page_title="Plant Growth Monitor",
    page_icon="🌱",
    layout="wide"
)

# Custom Dashboard Styling
st.markdown("""
<style>

/* Main background */
.stApp {
    background-color: #F3F8F3;
}

/* Main content */
.block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
}

/* Headings */
h1, h2, h3 {
    color: #174D35;
    font-family: 'Arial', sans-serif;
    font-weight: 700;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background-color: #E2F0E5;
    border-right: 2px solid #C5DEC9;
}

/* Metric cards */
div[data-testid="stMetric"] {
    background: linear-gradient(135deg, #FFFFFF, #E5F4E8);
    padding: 22px;
    border-radius: 16px;
    border: 1px solid #C8E3CE;
    box-shadow: 0 4px 12px rgba(30, 80, 50, 0.08);
}

/* Metric values */
div[data-testid="stMetricValue"] {
    color: #176B45;
    font-weight: bold;
}

/* Buttons */
.stButton > button {
    background-color: #238653;
    color: white;
    border-radius: 10px;
    border: none;
    padding: 10px 20px;
    font-weight: bold;
}

.stButton > button:hover {
    background-color: #14532D;
    color: white;
}

/* Input fields */
.stTextInput input,
.stNumberInput input,
.stTextArea textarea {
    border-radius: 9px;
}

/* Data table */
div[data-testid="stDataFrame"] {
    border: 1px solid #C8E3CE;
    border-radius: 12px;
    overflow: hidden;
}

</style>
""", unsafe_allow_html=True)


# File storage
DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)
DATA_FILE = DATA_DIR / "plant_data.csv"

COLUMNS = [
    "Plant Name",
    "Date",
    "Height (cm)",
    "Number of Leaves",
    "Watered",
    "Notes"
]


def load_data():
    if DATA_FILE.exists():
        df = pd.read_csv(DATA_FILE)
        if not df.empty:
            df["Date"] = pd.to_datetime(
                df["Date"], format="mixed"
            )
        return df
    return pd.DataFrame(columns=COLUMNS)



# Premium Welcome Banner
st.markdown("""
<div style="background-color: #237A50; padding: 30px; border-radius: 15px; color: white;">
    <h1 style="color: white;">🌱 Plant Growth Monitor</h1>
    <p style="color: white;">Track growth, analyse progress and care for your plants.</p>
</div>
""", unsafe_allow_html=True)

st.caption("🌱 Your personal plant growth analytics space")

df = load_data()

# Sidebar form
st.sidebar.header("➕ Add Plant Observation")

with st.sidebar.form("plant_form"):
    plant_name = st.text_input("Plant Name")
    observation_date = st.date_input("Observation Date", value=date.today())
    height = st.number_input("Plant Height (cm)", min_value=0.0, step=0.5)
    leaves = st.number_input("Number of Leaves", min_value=0, step=1)
    watered = st.selectbox("Watered Today?", ["Yes", "No"])
    notes = st.text_area("Notes")

    submitted = st.form_submit_button("Save Observation")

    if submitted:
        if not plant_name.strip():
            st.error("Please enter a plant name.")
        else:
            new_record = pd.DataFrame([{
                "Plant Name": plant_name.strip(),
                "Date": observation_date,
                "Height (cm)": height,
                "Number of Leaves": leaves,
                "Watered": watered,
                "Notes": notes
            }])

            df = pd.concat([df, new_record], ignore_index=True)
            df.to_csv(DATA_FILE, index=False)
            st.success("Observation saved!")
            st.rerun()

# Dashboard
if df.empty:
    st.info("No plant observations yet. Add your first observation using the sidebar.")
else:
    df["Date"] = pd.to_datetime(df["Date"], format="mixed")
    df = df.sort_values("Date")

    latest = df.sort_values("Date").groupby(
        "Plant Name", as_index=False
    ).tail(1)

    total_plants = df["Plant Name"].nunique()
    total_observations = len(df)
    average_height = latest["Height (cm)"].mean()

    col1, col2, col3 = st.columns(3)

    col1.metric("🌿 Total Plants", total_plants)
    col2.metric("📝 Total Observations", total_observations)
    col3.metric("📏 Average Latest Height", f"{average_height:.1f} cm")

    st.divider()

    selected_plant = st.selectbox(
        "Choose a plant",
        sorted(df["Plant Name"].unique())
    )

    plant_df = df[df["Plant Name"] == selected_plant]

    # Plant Information Cards
    latest_record = plant_df.iloc[-1]

    st.subheader("🌿 Plant Information")

    card1, card2, card3 = st.columns(3)

    card1.metric(
        "Plant Name",
        selected_plant
    )

    card2.metric(
        "Latest Height",
        f"{latest_record['Height (cm)']} cm"
    )

    card3.metric(
        "Number of Leaves",
        int(latest_record["Number of Leaves"])
    )
    st.info(
        f"💧 Last watering status: {latest_record['Watered']}"
    )

    st.subheader(f"📈 Growth History: {selected_plant}")

    height_chart = px.line(
        plant_df,
        x="Date",
        y="Height (cm)",
        markers=True,
        title="Plant Height Over Time"
    )
    st.plotly_chart(height_chart, use_container_width=True)

    leaves_chart = px.bar(
        plant_df,
        x="Date",
        y="Number of Leaves",
        title="Number of Leaves Over Time"
    )
    st.plotly_chart(leaves_chart, use_container_width=True)

    
st.subheader("📋 Observation Records")
st.dataframe(plant_df, use_container_width=True)
csv_data = plant_df.to_csv(index=False).encode("utf-8")

st.download_button(
    label="📥 Download Plant Records",
    data=csv_data,
    file_name="plant_growth_records.csv",
    mime="text/csv"
)


st.subheader("🗑️ Delete an Observation")

if not plant_df.empty:
    record_to_delete = st.selectbox(
        "Select observation to delete",
        plant_df.index,
        format_func=lambda i: (
            f"{plant_df.loc[i, 'Plant Name']} - "
            f"{plant_df.loc[i, 'Date'].date()} - "
            f"{plant_df.loc[i, 'Height (cm)']} cm"
        ),
        key="delete_record"
    )

    confirm_delete = st.checkbox(
        "I confirm that I want to delete this observation."
    )

    if st.button("Delete Selected Observation"):
        if confirm_delete:
            df = df.drop(index=record_to_delete).reset_index(drop=True)
            df.to_csv(DATA_FILE, index=False)
            st.success("Observation deleted successfully!")
            st.rerun()
        else:
            st.warning("Please confirm before deleting.")



    if len(plant_df) >= 2:
        first_height = plant_df.iloc[0]["Height (cm)"]
        latest_height = plant_df.iloc[-1]["Height (cm)"]
        difference = latest_height - first_height

        st.subheader("🌱 Growth Summary")

        growth_col1, growth_col2 = st.columns(2)

        growth_col1.metric(
            "Initial Height",
            f"{first_height:.1f} cm"
        )

        growth_col2.metric(
            "Total Height Growth",
            f"{difference:.1f} cm"
        )

   