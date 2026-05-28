import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ===== PAGE CONFIG =====
st.set_page_config(
    page_title="SkyCity Auckland Analytics",
    page_icon="🍽️",
    layout="wide"
)

# ===== LOAD DATA =====
@st.cache_data
def load_data():
    df = pd.read_csv(
        'skycity_final_analysis (1).csv'
    )
    return df

df = load_data()

# ===== CALCULATE KPIs =====
df['UberEats_Share%'] = (
    df['UberEatsOrders'] /
    df['MonthlyOrders'] * 100
).round(2)

df['DoorDash_Share%'] = (
    df['DoorDashOrders'] /
    df['MonthlyOrders'] * 100
).round(2)

df['InStore_Share%'] = (
    df['InStoreOrders'] /
    df['MonthlyOrders'] * 100
).round(2)

df['Aggregator_Dependence%'] = (
    df['UberEats_Share%'] +
    df['DoorDash_Share%']
).round(2)

df['Diversification_Score'] = (
    1 - (
        (df['InStoreOrders'] /
         df['MonthlyOrders'])**2 +
        (df['UberEatsOrders'] /
         df['MonthlyOrders'])**2 +
        (df['DoorDashOrders'] /
         df['MonthlyOrders'])**2 +
        (df['SelfDeliveryOrders'] /
         df['MonthlyOrders'])**2
    )
).round(3)

df['Risk_Profile'] = df.apply(
    lambda row: 'High Risk'
    if (row['UberEats_Share%'] >= 70 or
        row['DoorDash_Share%'] >= 70)
    else 'Moderate Risk'
    if row['Aggregator_Dependence%'] >= 60
    else 'Balanced', axis=1
)

# ===== SIDEBAR FILTERS =====
st.sidebar.title("🔍 Filters")

subregion = st.sidebar.multiselect(
    "Select Subregion",
    options=['North Shore','South Auckland',
             'West Auckland','CBD'],
    default=['North Shore','South Auckland',
             'West Auckland','CBD']
)

cuisine = st.sidebar.multiselect(
    "Select Cuisine",
    options=['Burgers','Chicken Dishes',
             'Chinese','Indian','Japanese',
             'Kebabs/Mediterranean',
             'Pizza','Thai'],
    default=['Burgers','Chicken Dishes',
             'Chinese','Indian','Japanese',
             'Kebabs/Mediterranean',
             'Pizza','Thai']
)

segment = st.sidebar.multiselect(
    "Select Segment",
    options=['Cafe','QSR',
             'Ghost Kitchen','Full-service'],
    default=['Cafe','QSR',
             'Ghost Kitchen','Full-service']
)

# Channel toggle
channel_view = st.sidebar.radio(
    "Channel View",
    ["All Channels",
     "In-Store Only",
     "Delivery Only"]
)

# Filter dataframe
filtered_df = df[
    (df['Subregion'].isin(subregion)) &
    (df['CuisineType'].isin(cuisine)) &
    (df['Segment'].isin(segment))
]

# ===== MAIN TITLE =====
st.title("🍽️ SkyCity Auckland")
st.title("Order Channel Analytics")
st.markdown("---")

# ===== KPI METRICS ROW =====
st.subheader("📊 Key Performance Indicators")

col1, col2, col3, col4, col5 = st.columns(5)

total_orders = filtered_df['MonthlyOrders'].sum()

with col1:
    instore_share = (
        filtered_df['InStoreOrders'].sum() /
        total_orders * 100
    )
    st.metric(
        "In-Store Share",
        f"{instore_share:.1f}%"
    )

with col2:
    ue_share = (
        filtered_df['UberEatsOrders'].sum() /
        total_orders * 100
    )
    st.metric(
        "Uber Eats Share",
        f"{ue_share:.1f}%"
    )

with col3:
    dd_share = (
        filtered_df['DoorDashOrders'].sum() /
        total_orders * 100
    )
    st.metric(
        "DoorDash Share",
        f"{dd_share:.1f}%"
    )

with col4:
    agg_dep = ue_share + dd_share
    st.metric(
        "Aggregator Dependence",
        f"{agg_dep:.1f}%"
    )

with col5:
    avg_div = filtered_df[
        'Diversification_Score'
    ].mean()
    st.metric(
        "Avg Diversification",
        f"{avg_div:.3f}"
    )

st.markdown("---")

# ===== ROW 1: TWO CHARTS =====
col1, col2 = st.columns(2)

with col1:
    st.subheader("📈 Channel Market Share")
    channel_data = pd.DataFrame({
        'Channel': ['In-Store','Uber Eats',
                    'DoorDash','Self-Delivery'],
        'Orders': [
            filtered_df['InStoreOrders'].sum(),
            filtered_df['UberEatsOrders'].sum(),
            filtered_df['DoorDashOrders'].sum(),
            filtered_df['SelfDeliveryOrders'].sum()
        ]
    })
    fig1 = px.pie(
        channel_data,
        values='Orders',
        names='Channel',
        color_discrete_sequence=px.colors.qualitative.Set3
    )
    st.plotly_chart(fig1, 
                    use_container_width=True)

with col2:
    st.subheader("📊 Orders by Channel")
    fig2 = px.bar(
        channel_data,
        x='Channel',
        y='Orders',
        color='Channel',
        color_discrete_sequence=px.colors.qualitative.Set3
    )
    st.plotly_chart(fig2,
                    use_container_width=True)

st.markdown("---")

# ===== ROW 2: GEOGRAPHIC ANALYSIS =====
st.subheader("🗺️ Geographic Channel Analysis")

geo = filtered_df.groupby('Subregion').agg(
    InStore=('InStoreOrders','sum'),
    UberEats=('UberEatsOrders','sum'),
    DoorDash=('DoorDashOrders','sum'),
    SelfDelivery=('SelfDeliveryOrders','sum'),
    Total=('MonthlyOrders','sum')
).reset_index()

for col in ['InStore','UberEats',
            'DoorDash','SelfDelivery']:
    geo[f'{col}%'] = (
        geo[col]/geo['Total']*100
    ).round(2)

geo_melted = geo.melt(
    id_vars='Subregion',
    value_vars=['InStore%','UberEats%',
                'DoorDash%','SelfDelivery%'],
    var_name='Channel',
    value_name='Share%'
)

fig3 = px.bar(
    geo_melted,
    x='Subregion',
    y='Share%',
    color='Channel',
    barmode='group',
    title='Channel Share by Subregion'
)
st.plotly_chart(fig3, use_container_width=True)

st.markdown("---")

# ===== ROW 3: CUISINE ANALYSIS =====
st.subheader("🍜 Cuisine Channel Patterns")

cuisine_data = filtered_df.groupby(
    'CuisineType'
).agg(
    InStore=('InStoreOrders','sum'),
    UberEats=('UberEatsOrders','sum'),
    DoorDash=('DoorDashOrders','sum'),
    SelfDelivery=('SelfDeliveryOrders','sum'),
    Total=('MonthlyOrders','sum')
).reset_index()

for col in ['InStore','UberEats',
            'DoorDash','SelfDelivery']:
    cuisine_data[f'{col}%'] = (
        cuisine_data[col] /
        cuisine_data['Total']*100
    ).round(2)

cuisine_melted = cuisine_data.melt(
    id_vars='CuisineType',
    value_vars=['InStore%','UberEats%',
                'DoorDash%','SelfDelivery%'],
    var_name='Channel',
    value_name='Share%'
)

fig4 = px.bar(
    cuisine_melted,
    x='CuisineType',
    y='Share%',
    color='Channel',
    barmode='stack',
    title='Channel Mix by Cuisine'
)
st.plotly_chart(fig4, use_container_width=True)

st.markdown("---")

# ===== ROW 4: DEPENDENCY RISK =====
st.subheader("⚠️ Channel Dependency Risk")

col1, col2 = st.columns(2)

with col1:
    risk_counts = filtered_df[
        'Risk_Profile'
    ].value_counts().reset_index()
    risk_counts.columns = ['Risk','Count']

    fig5 = px.pie(
        risk_counts,
        values='Count',
        names='Risk',
        color='Risk',
        color_discrete_map={
            'High Risk':'red',
            'Moderate Risk':'orange',
            'Balanced':'green'
        },
        title='Risk Profile Distribution'
    )
    st.plotly_chart(fig5,
                    use_container_width=True)

with col2:
    high_risk = filtered_df[
        filtered_df['Risk_Profile']=='High Risk'
    ][['RestaurantName',
       'UberEats_Share%',
       'DoorDash_Share%',
       'Aggregator_Dependence%']]

    st.write("🔴 High Risk Restaurants:")
    st.dataframe(high_risk)

st.markdown("---")

# ===== ROW 5: SEGMENT ANALYSIS =====
st.subheader("🏪 Segment Channel Analysis")

seg_data = filtered_df.groupby('Segment').agg(
    InStore=('InStoreOrders','sum'),
    UberEats=('UberEatsOrders','sum'),
    DoorDash=('DoorDashOrders','sum'),
    SelfDelivery=('SelfDeliveryOrders','sum'),
    Total=('MonthlyOrders','sum')
).reset_index()

for col in ['InStore','UberEats',
            'DoorDash','SelfDelivery']:
    seg_data[f'{col}%'] = (
        seg_data[col]/
        seg_data['Total']*100
    ).round(2)

seg_melted = seg_data.melt(
    id_vars='Segment',
    value_vars=['InStore%','UberEats%',
                'DoorDash%','SelfDelivery%'],
    var_name='Channel',
    value_name='Share%'
)

fig6 = px.bar(
    seg_melted,
    x='Segment',
    y='Share%',
    color='Channel',
    barmode='group',
    title='Channel Mix by Segment'
)
st.plotly_chart(fig6, use_container_width=True)

st.markdown("---")

# ===== RAW DATA TABLE =====
st.subheader("📋 Raw Data")
if st.checkbox("Show Raw Data"):
    st.dataframe(filtered_df)

# ===== FOOTER =====
st.markdown("---")
st.markdown(
    "**SkyCity Auckland** | "
    "Order Channel Analytics Dashboard"
)