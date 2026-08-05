"""
==============================================================
Customer Segmentation & Churn Pattern Analytics
European Banking Dashboard
Developed using Streamlit, Plotly and Pandas
==============================================================
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="European Banking Dashboard",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================
# COLOR PALETTE
# ============================================================

PRIMARY = "#0B3C5D"
SECONDARY = "#328CC1"
ACCENT = "#D9A441"
SUCCESS = "#3AA17E"
DANGER = "#C0392B"
LIGHT = "#F7F9FB"
CARD = "#FFFFFF"

COLORS = [
    PRIMARY,
    SECONDARY,
    ACCENT,
    SUCCESS,
    DANGER
]

# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown(
    f"""
<style>

.main {{
    background-color:{LIGHT};
}}

.block-container {{
    padding-top:1.5rem;
    padding-bottom:2rem;
}}

h1,h2,h3,h4 {{
    color:{PRIMARY};
    font-weight:700;
}}

section[data-testid="stSidebar"] {{
    background:#F3F5F7;
}}

div[data-testid="metric-container"] {{
    background:{CARD};
    border-radius:15px;
    padding:18px;
    border:1px solid #E5E7EB;
    box-shadow:0px 3px 10px rgba(0,0,0,.08);
}}

div[data-testid="metric-container"] label {{
    color:#555;
}}

div[data-testid="stMetricValue"] {{
    color:{PRIMARY};
    font-weight:700;
}}

.insight-box {{
    background:white;
    border-left:6px solid {SECONDARY};
    padding:14px;
    border-radius:10px;
    margin-top:12px;
    margin-bottom:18px;
    box-shadow:0px 2px 8px rgba(0,0,0,.05);
}}

.footer {{
    text-align:center;
    color:#666;
    font-size:14px;
    padding:15px;
}}

</style>
""",
    unsafe_allow_html=True
)

# ============================================================
# LOAD DATA
# ============================================================


@st.cache_data(show_spinner=False)
def load_data():

    data = pd.read_csv("European_Bank.csv")

    data["AgeGroup"] = pd.cut(
        data["Age"],
        bins=[0, 29, 45, 60, 120],
        labels=["<30", "30-45", "46-60", "60+"],
        include_lowest=True
    )

    data["TenureGroup"] = pd.cut(
        data["Tenure"],
        bins=[-1, 2, 6, 10],
        labels=[
            "New (0-2y)",
            "Mid (3-6y)",
            "Loyal (7+y)"
        ]
    )

    data["BalanceSegment"] = pd.cut(
        data["Balance"],
        bins=[-1, 0, 100000, float("inf")],
        labels=[
            "Zero Balance",
            "Regular Balance",
            "High Value"
        ]
    )

    data["CreditBand"] = pd.cut(
        data["CreditScore"],
        bins=[0, 580, 700, 900],
        labels=[
            "Low",
            "Medium",
            "High"
        ]
    )

    data["CustomerStatus"] = data["Exited"].map({
        0: "Retained",
        1: "Churned"
    })

    data["ActivityStatus"] = data["IsActiveMember"].map({
        1: "Active",
        0: "Inactive"
    })

    return data


df_master = load_data()

# ============================================================
# REUSABLE FUNCTIONS
# ============================================================


def section_heading(title, subtitle=""):
    st.markdown(f"## {title}")
    if subtitle:
        st.caption(subtitle)


def draw_divider():
    st.markdown("---")


def info_box(text):
    st.markdown(
        f"""
<div class="insight-box">
{text}
</div>
""",
        unsafe_allow_html=True
    )


def churn_rate(frame):
    if frame.empty:
        return 0
    return frame["Exited"].mean() * 100


def percent(value):
    return f"{value:.1f}%"


def money(value):
    return f"€{value:,.0f}"


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.title("🏦 European Bank")

st.sidebar.caption(
    "Customer Segmentation & Churn Dashboard"
)

st.sidebar.markdown("---")

st.sidebar.subheader("Dashboard Filters")

selected_geo = st.sidebar.multiselect(
    "Country",
    sorted(df_master["Geography"].unique()),
    default=sorted(df_master["Geography"].unique())
)

selected_gender = st.sidebar.multiselect(
    "Gender",
    sorted(df_master["Gender"].unique()),
    default=sorted(df_master["Gender"].unique())
)

selected_age = st.sidebar.multiselect(
    "Age Group",
    list(df_master["AgeGroup"].astype(str).unique()),
    default=list(df_master["AgeGroup"].astype(str).unique())
)

selected_activity = st.sidebar.multiselect(
    "Customer Activity",
    ["Active", "Inactive"],
    default=["Active", "Inactive"]
)

selected_balance = st.sidebar.multiselect(
    "Balance Category",
    list(df_master["BalanceSegment"].astype(str).unique()),
    default=list(df_master["BalanceSegment"].astype(str).unique())
)

selected_products = st.sidebar.multiselect(
    "Products Owned",
    sorted(df_master["NumOfProducts"].unique()),
    default=sorted(df_master["NumOfProducts"].unique())
)

df = df_master[
    (df_master["Geography"].isin(selected_geo))
    &
    (df_master["Gender"].isin(selected_gender))
    &
    (df_master["AgeGroup"].astype(str).isin(selected_age))
    &
    (df_master["ActivityStatus"].isin(selected_activity))
    &
    (df_master["BalanceSegment"].astype(str).isin(selected_balance))
    &
    (df_master["NumOfProducts"].isin(selected_products))
]

if df.empty:
    st.warning("No records match the selected filters.")
    st.stop()

# ============================================================
# DASHBOARD HEADER
# ============================================================

section_heading(
    "🏦 Customer Segmentation & Churn Pattern Analytics",
    "Retail Banking Customer Analytics | France • Germany • Spain"
)

left, right = st.columns([4, 1])

with left:
    st.markdown(
        """
This interactive dashboard helps identify customer churn behaviour,
high-value customer segments, demographic patterns and business
opportunities using the European Banking dataset.
"""
    )

with right:
    st.info(
        f"""
**Filtered Customers**

### {len(df):,}
"""
    )

draw_divider()

# ============================================================
# KPI CALCULATIONS
# ============================================================

total_customers = len(df)
total_churn = int(df["Exited"].sum())
total_retained = total_customers - total_churn
overall_churn_rate = churn_rate(df)
average_balance = df["Balance"].mean()
average_salary = df["EstimatedSalary"].mean()
average_credit = df["CreditScore"].mean()
average_age = df["Age"].mean()

active_customers = df[df["IsActiveMember"] == 1]
inactive_customers = df[df["IsActiveMember"] == 0]

active_rate = churn_rate(active_customers)
inactive_rate = churn_rate(inactive_customers)
engagement_gap = inactive_rate - active_rate

high_value = df[df["Balance"] >= 100000]
standard_value = df[df["Balance"] < 100000]
high_value_rate = churn_rate(high_value)

# ============================================================
# KPI SECTION
# ============================================================

k1, k2, k3, k4, k5, k6 = st.columns(6)

k1.metric(
    "Customers",
    f"{total_customers:,}"
)

k2.metric(
    "Churned",
    f"{total_churn:,}"
)

k3.metric(
    "Retention",
    f"{total_retained:,}"
)

k4.metric(
    "Churn Rate",
    percent(overall_churn_rate)
)

k5.metric(
    "High Value Churn",
    percent(high_value_rate)
)

k6.metric(
    "Engagement Gap",
    percent(engagement_gap)
)

draw_divider()

# ============================================================
# SECONDARY KPIs
# ============================================================

m1, m2, m3, m4 = st.columns(4)

m1.metric(
    "Average Age",
    f"{average_age:.1f} Years"
)

m2.metric(
    "Average Credit Score",
    f"{average_credit:.0f}"
)

m3.metric(
    "Average Balance",
    money(average_balance)
)

m4.metric(
    "Average Salary",
    money(average_salary)
)

info_box(
    """
**Executive Summary**

• The dashboard is fully interactive and updates according to the sidebar filters.

• Customer churn percentage represents the proportion of customers who have left the bank.

• High-value customers are currently defined as customers having a balance of **€100,000 or more**.

• Engagement Gap compares the churn rate of inactive customers with active customers. A higher gap generally indicates poor customer engagement.
"""
)

draw_divider()

# ============================================================
# DASHBOARD TABS
# ============================================================

overview_tab, demographic_tab, segment_tab, premium_tab = st.tabs(
    [
        "📊 Executive Overview",
        "👥 Customer Demographics",
        "📈 Segment Analysis",
        "💎 Premium Customers"
    ]
)

# ============================================================
# TAB 1
# EXECUTIVE OVERVIEW
# ============================================================

with overview_tab:

    left, right = st.columns([1, 1.4])

    with left:
        st.subheader("Customer Distribution")

        pie = px.pie(
            df,
            names="CustomerStatus",
            hole=0.62,
            color="CustomerStatus",
            color_discrete_map={
                "Retained": SECONDARY,
                "Churned": DANGER
            }
        )

        pie.update_traces(
            textinfo="percent+label",
            pull=[0, 0.08]
        )

        pie.update_layout(
            showlegend=False,
            margin=dict(l=10, r=10, t=20, b=10),
            height=470
        )

        st.plotly_chart(
            pie,
            use_container_width=True
        )

        info_box(
            """
The majority of customers are retained while the remaining customers have exited the bank. This chart provides a quick overview of the overall customer distribution.
"""
        )

    with right:
        st.subheader("Churn Driver Analysis")

        driver_options = {
            "Geography": "Geography",
            "Age Group": "AgeGroup",
            "Gender": "Gender",
            "Products": "NumOfProducts",
            "Credit Band": "CreditBand",
            "Balance Segment": "BalanceSegment",
            "Customer Activity": "ActivityStatus",
            "Tenure Group": "TenureGroup"
        }

        selected_driver = st.selectbox(
            "Select Driver",
            list(driver_options.keys())
        )

        column = driver_options[selected_driver]

        driver_df = (
            df.groupby(column, observed=True)["Exited"]
            .mean()
            .mul(100)
            .reset_index(name="Churn Rate")
            .sort_values(
                "Churn Rate",
                ascending=False
            )
        )

        fig = px.bar(
            driver_df,
            x=column,
            y="Churn Rate",
            color="Churn Rate",
            text=driver_df["Churn Rate"].round(1),
            color_continuous_scale=[
                SECONDARY,
                ACCENT,
                DANGER
            ]
        )

        fig.update_traces(
            texttemplate="%{text:.1f}%",
            textposition="outside"
        )

        fig.update_layout(
            coloraxis_showscale=False,
            margin=dict(
                l=10,
                r=10,
                t=20,
                b=10
            ),
            height=470
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

        highest_segment = driver_df.iloc[0, 0]
        highest_rate = driver_df.iloc[0]["Churn Rate"]

        info_box(
            f"""
Highest churn is currently observed for **{highest_segment}**
with a churn rate of **{highest_rate:.1f}%**.
"""
        )

    draw_divider()

    st.subheader("Average Customer Profile")

    profile = (
        df.groupby("CustomerStatus")[
            [
                "Age",
                "Balance",
                "EstimatedSalary",
                "CreditScore",
                "Tenure"
            ]
        ]
        .mean()
        .round(1)
    )

    st.dataframe(
        profile.style.format(
            {
                "Balance": "€{:,.0f}",
                "EstimatedSalary": "€{:,.0f}"
            }
        ),
        use_container_width=True
    )

    info_box(
        """
The profile table compares retained and churned customers using
average values of important banking attributes.
"""
    )

# ============================================================
# TAB 2
# CUSTOMER DEMOGRAPHICS
# ============================================================

with demographic_tab:

    section_heading(
        "Customer Demographics",
        "Understand churn patterns across customer demographics."
    )

    left, right = st.columns(2)

    with left:
        st.subheader("Churn Rate by Geography")

        geography_df = (
            df.groupby("Geography")["Exited"]
            .mean()
            .mul(100)
            .reset_index(name="Churn Rate")
            .sort_values("Churn Rate", ascending=False)
        )

        fig = px.bar(
            geography_df,
            x="Geography",
            y="Churn Rate",
            color="Geography",
            text=geography_df["Churn Rate"].round(1),
            color_discrete_sequence=COLORS
        )

        fig.update_traces(
            texttemplate="%{text:.1f}%",
            textposition="outside"
        )

        fig.update_layout(
            showlegend=False,
            height=430,
            margin=dict(l=10, r=10, t=20, b=10)
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    with right:
        st.subheader("Churn Rate by Age Group")

        age_df = (
            df.groupby("AgeGroup", observed=True)["Exited"]
            .mean()
            .mul(100)
            .reset_index(name="Churn Rate")
        )

        fig = px.bar(
            age_df,
            x="AgeGroup",
            y="Churn Rate",
            text=age_df["Churn Rate"].round(1),
            color="Churn Rate",
            color_continuous_scale=[
                SECONDARY,
                ACCENT,
                DANGER
            ]
        )

        fig.update_traces(
            texttemplate="%{text:.1f}%",
            textposition="outside"
        )

        fig.update_layout(
            coloraxis_showscale=False,
            height=430,
            margin=dict(l=10, r=10, t=20, b=10)
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    info_box(
        """
These visualizations highlight whether customer location or age has
a significant influence on customer churn.
"""
    )

    draw_divider()

    left, right = st.columns([1, 1])

    with left:
        st.subheader("Gender Distribution")

        fig = px.pie(
            df,
            names="Gender",
            hole=0.55,
            color="Gender",
            color_discrete_sequence=[
                PRIMARY,
                ACCENT
            ]
        )

        fig.update_layout(
            showlegend=True,
            height=420
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    with right:
        st.subheader("Gender-wise Churn Rate")

        gender_df = (
            df.groupby("Gender")["Exited"]
            .mean()
            .mul(100)
            .reset_index(name="Churn Rate")
        )

        fig = px.bar(
            gender_df,
            x="Gender",
            y="Churn Rate",
            color="Gender",
            text=gender_df["Churn Rate"].round(1),
            color_discrete_sequence=[
                SECONDARY,
                DANGER
            ]
        )

        fig.update_traces(
            texttemplate="%{text:.1f}%",
            textposition="outside"
        )

        fig.update_layout(
            showlegend=False,
            height=420
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    draw_divider()

    st.subheader("Geography vs Age Group")

    heatmap_df = (
        df.pivot_table(
            index="Geography",
            columns="AgeGroup",
            values="Exited",
            aggfunc="mean",
            observed=True
        ) * 100
    )

    fig = px.imshow(
        heatmap_df,
        text_auto=".1f",
        aspect="auto",
        color_continuous_scale=[
            SECONDARY,
            ACCENT,
            DANGER
        ],
        labels={
            "color": "Churn %"
        }
    )

    fig.update_layout(
        height=420
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    info_box(
        """
The heatmap makes it easy to identify combinations of geography and
age group where customer churn is comparatively higher.
"""
    )

    draw_divider()

    left, right = st.columns(2)

    with left:
        st.subheader("Customer Balance Distribution")

        fig = px.histogram(
            df,
            x="Balance",
            nbins=40,
            color="CustomerStatus",
            color_discrete_map={
                "Retained": SECONDARY,
                "Churned": DANGER
            },
            opacity=0.75
        )

        fig.update_layout(
            bargap=0.05,
            height=430
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    with right:
        st.subheader("Salary Distribution")

        fig = px.box(
            df,
            x="CustomerStatus",
            y="EstimatedSalary",
            color="CustomerStatus",
            color_discrete_map={
                "Retained": SECONDARY,
                "Churned": DANGER
            }
        )

        fig.update_layout(
            showlegend=False,
            height=430
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    info_box(
        """
These charts compare financial characteristics between retained and
churned customers. Outliers may indicate valuable customer segments.
"""
    )

    draw_divider()

    left, right = st.columns(2)

    with left:
        st.subheader("Tenure Group Churn")

        tenure_df = (
            df.groupby(
                "TenureGroup",
                observed=True
            )["Exited"]
            .mean()
            .mul(100)
            .reset_index(name="Churn Rate")
        )

        fig = px.bar(
            tenure_df,
            x="TenureGroup",
            y="Churn Rate",
            text=tenure_df["Churn Rate"].round(1),
            color_discrete_sequence=[ACCENT]
        )

        fig.update_traces(
            texttemplate="%{text:.1f}%",
            textposition="outside"
        )

        fig.update_layout(
            height=420
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    with right:
        st.subheader("Average Credit Score")

        credit_df = (
            df.groupby(
                "CreditBand",
                observed=True
            )["CreditScore"]
            .mean()
            .reset_index()
        )

        fig = px.bar(
            credit_df,
            x="CreditBand",
            y="CreditScore",
            color="CreditBand",
            color_discrete_sequence=COLORS
        )

        fig.update_layout(
            showlegend=False,
            height=420
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    info_box(
        """
Long-term customers generally exhibit different churn behaviour than
new customers. Credit score bands also help understand customer quality.
"""
    )

# ============================================================
# TAB 3
# SEGMENT ANALYSIS
# ============================================================

with segment_tab:
    section_heading(
        "Customer Segment Explorer",
        "Analyse customer behaviour across multiple dimensions."
    )

    dimensions = {
        "Geography": "Geography",
        "Gender": "Gender",
        "Age Group": "AgeGroup",
        "Credit Band": "CreditBand",
        "Balance Segment": "BalanceSegment",
        "Tenure Group": "TenureGroup",
        "Products Held": "NumOfProducts",
        "Customer Activity": "ActivityStatus"
    }

    left_col, right_col = st.columns(2)

    primary_dimension = left_col.selectbox(
        "Primary Dimension",
        list(dimensions.keys()),
        index=0
    )

    secondary_dimension = right_col.selectbox(
        "Secondary Dimension",
        list(dimensions.keys()),
        index=2
    )

    if primary_dimension == secondary_dimension:
        st.warning(
            "Please choose two different dimensions."
        )
    else:
        comparison_df = (
            df.groupby(
                [
                    dimensions[primary_dimension],
                    dimensions[secondary_dimension]
                ],
                observed=True
            )["Exited"]
            .agg(
                ChurnRate="mean",
                Customers="count"
            )
            .reset_index()
        )

        comparison_df["ChurnRate"] = (
            comparison_df["ChurnRate"] * 100
        ).round(2)

        fig = px.bar(
            comparison_df,
            x=dimensions[primary_dimension],
            y="ChurnRate",
            color=dimensions[secondary_dimension],
            barmode="group",
            hover_data=["Customers"],
            text=comparison_df["ChurnRate"].round(1),
            color_discrete_sequence=COLORS
        )

        fig.update_traces(
            texttemplate="%{text:.1f}%",
            textposition="outside"
        )

        fig.update_layout(
            height=500,
            margin=dict(
                l=10,
                r=10,
                t=20,
                b=10
            )
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

        info_box(
            """
Compare two customer dimensions simultaneously to discover
which combinations experience the highest churn.
"""
        )

        st.subheader("Segment Summary")

        summary_table = comparison_df.rename(
            columns={
                "ChurnRate": "Churn Rate (%)"
            }
        )

        st.dataframe(
            summary_table.sort_values(
                "Churn Rate (%)",
                ascending=False
            ),
            hide_index=True,
            use_container_width=True
        )

    draw_divider()

    st.subheader("Contribution to Overall Customer Churn")

    contribution_dimension = st.selectbox(
        "Analyse Contribution By",
        list(dimensions.keys()),
        key="contribution_dimension"
    )

    churn_customers = df[df["Exited"] == 1]

    contribution_df = (
        churn_customers.groupby(
            dimensions[contribution_dimension],
            observed=True
        )
        .size()
        .reset_index(name="Churned Customers")
    )

    total_churn_count = contribution_df["Churned Customers"].sum()

    contribution_df["Contribution (%)"] = (
        contribution_df["Churned Customers"]
        / total_churn_count
        * 100
    ).round(1)

    contribution_df = contribution_df.sort_values(
        "Contribution (%)",
        ascending=True
    )

    fig = px.bar(
        contribution_df,
        x="Contribution (%)",
        y=dimensions[contribution_dimension],
        orientation="h",
        text="Contribution (%)",
        color="Contribution (%)",
        color_continuous_scale=[
            SECONDARY,
            ACCENT,
            DANGER
        ]
    )

    fig.update_traces(
        texttemplate="%{text:.1f}%",
        textposition="outside"
    )

    fig.update_layout(
        height=480,
        coloraxis_showscale=False,
        margin=dict(
            l=10,
            r=10,
            t=15,
            b=10
        )
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    info_box(
        """
This chart shows how much each customer segment contributes
to the total number of customers who have churned.
Large contributions highlight business areas where retention
strategies can have the greatest impact.
"""
    )

    draw_divider()

    st.subheader("Top Customer Segments by Churn Rate")

    top_dimension = st.selectbox(
        "Rank Segments By",
        list(dimensions.keys()),
        key="top_segments"
    )

    ranking_df = (
        df.groupby(
            dimensions[top_dimension],
            observed=True
        )["Exited"]
        .agg(
            Customers="count",
            ChurnRate="mean"
        )
        .reset_index()
    )

    ranking_df["Churn Rate (%)"] = (
        ranking_df["ChurnRate"] * 100
    ).round(1)

    ranking_df = ranking_df.drop(
        columns="ChurnRate"
    )

    ranking_df = ranking_df.sort_values(
        "Churn Rate (%)",
        ascending=False
    )

    fig = px.bar(
        ranking_df,
        x=dimensions[top_dimension],
        y="Churn Rate (%)",
        text="Churn Rate (%)",
        color="Churn Rate (%)",
        color_continuous_scale=[
            SECONDARY,
            ACCENT,
            DANGER
        ]
    )

    fig.update_traces(
        texttemplate="%{text:.1f}%",
        textposition="outside"
    )

    fig.update_layout(
        height=450,
        coloraxis_showscale=False,
        margin=dict(
            l=10,
            r=10,
            t=15,
            b=10
        )
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    st.dataframe(
        ranking_df,
        hide_index=True,
        use_container_width=True
    )

    info_box(
        """
Segments appearing at the top of this ranking have the highest
percentage of churn and should be prioritized for customer
retention campaigns.
"""
    )

    draw_divider()

    st.subheader("Customer Segmentation Treemap")

    treemap_df = (
        df.groupby(
            [
                "Geography",
                "CustomerStatus"
            ],
            observed=True
        )
        .size()
        .reset_index(name="Customers")
    )

    fig = px.treemap(
        treemap_df,
        path=[
            "Geography",
            "CustomerStatus"
        ],
        values="Customers",
        color="Customers",
        color_continuous_scale="Blues"
    )

    fig.update_layout(
        height=550,
        margin=dict(
            l=10,
            r=10,
            t=20,
            b=10
        )
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    info_box(
        """
The treemap displays the distribution of customers across
different countries and their churn status. Larger blocks
represent larger customer groups.
"""
    )

    draw_divider()

    st.subheader("Customer Hierarchy")

    hierarchy_df = (
        df.groupby(
            [
                "Geography",
                "Gender",
                "CustomerStatus"
            ],
            observed=True
        )
        .size()
        .reset_index(name="Customers")
    )

    fig = px.sunburst(
        hierarchy_df,
        path=[
            "Geography",
            "Gender",
            "CustomerStatus"
        ],
        values="Customers",
        color="Customers",
        color_continuous_scale="Viridis"
    )

    fig.update_layout(
        height=650,
        margin=dict(
            l=10,
            r=10,
            t=20,
            b=10
        )
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    info_box(
        """
The sunburst chart presents a hierarchical view of customers,
starting from geography, then gender, and finally customer
status. It helps identify the composition of each segment.
"""
    )

    draw_divider()

    st.subheader("Highest Risk Customer Segments")

    minimum_customers = st.slider(
        "Minimum Customers in Segment",
        min_value=10,
        max_value=200,
        value=25,
        step=5,
        key="risk_slider"
    )

    risk_df = (
        df.groupby(
            [
                "Geography",
                "AgeGroup",
                "Gender"
            ],
            observed=True
        )["Exited"]
        .agg(
            Customers="count",
            ChurnRate="mean"
        )
        .reset_index()
    )

    risk_df = risk_df[
        risk_df["Customers"] >= minimum_customers
    ]

    risk_df["Churn Rate (%)"] = (
        risk_df["ChurnRate"] * 100
    ).round(1)

    risk_df.drop(
        columns="ChurnRate",
        inplace=True
    )

    risk_df = risk_df.sort_values(
        "Churn Rate (%)",
        ascending=False
    )

    st.dataframe(
        risk_df.head(15),
        hide_index=True,
        use_container_width=True
    )

    draw_divider()

    st.subheader("Customer Segment Bubble Analysis")

    bubble_df = risk_df.copy()

    fig = px.scatter(
        bubble_df,
        x="Customers",
        y="Churn Rate (%)",
        size="Customers",
        color="Geography",
        hover_name="AgeGroup",
        hover_data={
            "Gender": True,
            "Customers": True,
            "Churn Rate (%)": True
        },
        size_max=40,
        color_discrete_sequence=COLORS
    )

    fig.update_layout(
        height=500,
        margin=dict(
            l=10,
            r=10,
            t=20,
            b=10
        )
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    info_box(
        """
Large bubbles indicate larger customer groups.

Bubbles appearing in the upper-right region represent
large customer segments with high churn and should
receive the highest retention priority.
"""
    )

    draw_divider()

    st.subheader("Segment Performance Summary")

    performance = (
        df.groupby(
            "BalanceSegment",
            observed=True
        )
        .agg(
            Customers=("CustomerId", "count"),
            AverageAge=("Age", "mean"),
            AverageBalance=("Balance", "mean"),
            AverageSalary=("EstimatedSalary", "mean"),
            AverageCredit=("CreditScore", "mean"),
            ChurnRate=("Exited", "mean")
        )
        .reset_index()
    )

    performance["Churn Rate (%)"] = (
        performance["ChurnRate"] * 100
    ).round(1)

    performance.drop(
        columns="ChurnRate",
        inplace=True
    )

    st.dataframe(
        performance.style.format(
            {
                "AverageAge": "{:.1f}",
                "AverageBalance": "€{:,.0f}",
                "AverageSalary": "€{:,.0f}",
                "AverageCredit": "{:.0f}",
                "Churn Rate (%)": "{:.1f}"
            }
        ),
        use_container_width=True,
        hide_index=True
    )

    draw_divider()

    st.subheader("Business Insights")

    if not risk_df.empty:
        highest_segment = risk_df.iloc[0]

        st.success(
            f"""
Highest observed churn segment:

• Geography : {highest_segment['Geography']}

• Age Group : {highest_segment['AgeGroup']}

• Gender : {highest_segment['Gender']}

• Customers : {highest_segment['Customers']}

• Churn Rate : {highest_segment['Churn Rate (%)']:.1f}%
"""
        )

    info_box(
        """
Recommended Actions

• Improve customer engagement programmes.

• Offer personalised financial products.

• Reward loyal customers through retention campaigns.

• Monitor inactive customers regularly.

• Target high-risk customer groups using predictive analytics.

• Improve customer support for premium customers.
"""
    )

    draw_divider()

# ============================================================
# TAB 4
# PREMIUM CUSTOMER ANALYTICS
# ============================================================

with premium_tab:

    section_heading(
        "Premium Customer Analytics",
        "Analyse customers with higher account balances and their churn behaviour."
    )

    threshold = st.slider(
        "High Value Balance Threshold (€)",
        min_value=0,
        max_value=250000,
        value=100000,
        step=10000
    )

    premium_df = df[df["Balance"] >= threshold]
    standard_df = df[df["Balance"] < threshold]

    premium_count = len(premium_df)
    standard_count = len(standard_df)

    premium_rate = churn_rate(premium_df)
    standard_rate = churn_rate(standard_df)

    premium_share = (
        premium_df["Exited"].sum()
        / df["Exited"].sum()
        * 100
        if df["Exited"].sum() > 0
        else 0
    )

    average_premium_balance = (
        premium_df["Balance"].mean()
        if premium_count
        else 0
    )

    average_salary = (
        premium_df["EstimatedSalary"].mean()
        if premium_count
        else 0
    )

    c1, c2, c3, c4 = st.columns(4)

    c1.metric(
        "Premium Customers",
        f"{premium_count:,}"
    )

    c2.metric(
        "Premium Churn",
        f"{premium_rate:.1f}%"
    )

    c3.metric(
        "Standard Churn",
        f"{standard_rate:.1f}%"
    )

    c4.metric(
        "Contribution to Total Churn",
        f"{premium_share:.1f}%"
    )

    draw_divider()

    m1, m2 = st.columns(2)

    m1.metric(
        "Average Premium Balance",
        money(average_premium_balance)
    )

    m2.metric(
        "Average Premium Salary",
        money(average_salary)
    )

    info_box(
        """
Premium customers generally contribute more revenue to the bank.
Understanding their churn behaviour helps improve long-term profitability.
"""
    )

    draw_divider()

    left, right = st.columns(2)

    with left:
        st.subheader("Premium vs Standard Churn")

        comparison = pd.DataFrame({
            "Customer Type": [
                "Premium",
                "Standard"
            ],
            "Churn Rate": [
                premium_rate,
                standard_rate
            ]
        })

        fig = px.bar(
            comparison,
            x="Customer Type",
            y="Churn Rate",
            color="Customer Type",
            text="Churn Rate",
            color_discrete_sequence=[
                DANGER,
                SECONDARY
            ]
        )

        fig.update_traces(
            texttemplate="%{text:.1f}%",
            textposition="outside"
        )

        fig.update_layout(
            showlegend=False,
            height=430
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    with right:
        st.subheader("Premium Customer Distribution")

        fig = px.pie(
            values=[
                premium_count,
                standard_count
            ],
            names=[
                "Premium",
                "Standard"
            ],
            hole=.60,
            color_discrete_sequence=[
                ACCENT,
                SECONDARY
            ]
        )

        fig.update_layout(
            height=430
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    info_box(
        """
This comparison highlights whether premium customers churn at a higher
or lower rate than standard customers.
"""
    )

    draw_divider()

    left, right = st.columns(2)

    with left:
        st.subheader("Balance vs Estimated Salary")

        sample_df = premium_df.sample(
            min(2000, len(premium_df)),
            random_state=42
        ) if not premium_df.empty else premium_df

        fig = px.scatter(
            sample_df,
            x="EstimatedSalary",
            y="Balance",
            color="CustomerStatus",
            size="Age",
            hover_data=[
                "CreditScore",
                "Tenure",
                "NumOfProducts"
            ],
            opacity=0.70,
            color_discrete_map={
                "Retained": SECONDARY,
                "Churned": DANGER
            }
        )

        fig.update_layout(height=500)

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    with right:
        st.subheader("Age vs Credit Score")

        fig = px.scatter(
            sample_df,
            x="Age",
            y="CreditScore",
            color="CustomerStatus",
            size="Balance",
            hover_data=[
                "EstimatedSalary",
                "NumOfProducts"
            ],
            opacity=0.70,
            color_discrete_map={
                "Retained": SECONDARY,
                "Churned": DANGER
            }
        )

        fig.update_layout(height=500)

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    info_box(
        """
The scatter plots help identify premium customers with similar
financial characteristics and highlight where churned customers
tend to cluster.
"""
    )

    draw_divider()

    st.subheader("Correlation Between Numerical Features")

    correlation_columns = [
        "CreditScore",
        "Age",
        "Tenure",
        "Balance",
        "EstimatedSalary",
        "NumOfProducts",
        "Exited"
    ]

    correlation = premium_df[
        correlation_columns
    ].corr(numeric_only=True)

    fig = px.imshow(
        correlation,
        text_auto=".2f",
        aspect="auto",
        color_continuous_scale="RdBu_r"
    )

    fig.update_layout(
        height=600
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    info_box(
        """
The correlation matrix shows the strength of relationships
between customer attributes. Strong positive or negative
correlations may indicate influential churn factors.
"""
    )

    draw_divider()

    st.subheader("Top Premium Customers")

    display_columns = [
        "CustomerId",
        "Geography",
        "Gender",
        "Age",
        "CreditScore",
        "Balance",
        "EstimatedSalary",
        "NumOfProducts",
        "Tenure",
        "ActivityStatus",
        "CustomerStatus"
    ]

    top_customers = (
        premium_df
        .sort_values(
            "Balance",
            ascending=False
        )
        .head(50)
    )

    st.dataframe(
        top_customers[
            display_columns
        ].style.format(
            {
                "Balance": "€{:,.0f}",
                "EstimatedSalary": "€{:,.0f}"
            }
        ),
        use_container_width=True,
        hide_index=True
    )

    draw_divider()

    st.subheader("Executive Business Insights")

    col1, col2 = st.columns(2)

    with col1:
        st.success(
            f"""
### Key Findings

• Premium Customers : **{premium_count:,}**

• Premium Churn Rate : **{premium_rate:.1f}%**

• Average Balance : **{money(average_premium_balance)}**

• Average Salary : **{money(average_salary)}**
"""
        )

    with col2:
        st.info(
            """
### Recommended Actions

• Improve loyalty programmes.

• Increase personalised banking services.

• Monitor inactive premium customers.

• Encourage multi-product adoption.

• Launch targeted retention campaigns.

• Continuously monitor churn trends.
"""
        )

    draw_divider()

# ============================================================
# FOOTER
# ============================================================

st.markdown(
    """
<div class="footer">

<h4>Customer Segmentation & Churn Pattern Analytics</h4>

European Banking Dataset (10,000 Customers)

<br>

Developed using

<b>Streamlit</b> •
<b>Pandas</b> •
<b>Plotly</b>

<br><br>

Interactive Dashboard Features

✔ Executive KPIs

✔ Customer Segmentation

✔ Geography Analysis

✔ Premium Customer Analytics

✔ Interactive Filters

✔ Churn Trend Exploration

</div>
""",
    unsafe_allow_html=True
)
