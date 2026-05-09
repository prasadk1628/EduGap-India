import plotly.express as px
import plotly.graph_objects as go

from utils.helpers import hex_to_rgba
from utils.config import (
    ACC,
    CMP_PAL,
    TIER_CLR
)


def infra_breakdown_chart(df):
    fig = px.bar(
        df,
        x="Metric",
        y="Value",
        text_auto=".0%",
        title="School Facility Availability"
    )

    fig.update_layout(
        xaxis_title="Facilities",
        yaxis_title="Availability Ratio",
        height=350,
        bargap=0.2
    )

    return fig


def india_map(df, geojson):
    fig = px.choropleth(
        df,
        geojson=geojson,
        featureidkey="properties.ST_NM",
        locations="state_mapped",
        color="infra_tier",
        hover_name="India/State/UT",
        color_discrete_map=TIER_CLR,
        title="State-wise Infrastructure Quality"
    )

    fig.update_geos(
        fitbounds="locations",
        visible=False
    )

    return fig


def radar_chart(categories, values, name, color):
    fig = go.Figure()

    fig.add_trace(go.Scatterpolar(
        r=values + [values[0]],
        theta=categories + [categories[0]],
        fill="toself",
        name=name,
        line=dict(color=color),
        fillcolor=hex_to_rgba(color, 0.15)
    ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 1]
            )
        ),
        showlegend=True,
        height=450
    )

    return fig


def compare_radar_chart(states_data, categories):
    fig = go.Figure()

    for i, (state, vals) in enumerate(states_data.items()):
        fig.add_trace(go.Scatterpolar(
            r=vals + [vals[0]],
            theta=categories + [categories[0]],
            fill="toself",
            name=state,
            line=dict(color=CMP_PAL[i % len(CMP_PAL)]),
            fillcolor=hex_to_rgba(
                CMP_PAL[i % len(CMP_PAL)],
                0.15
            )
        ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 1]
            )
        ),
        showlegend=True,
        height=500
    )

    return fig  