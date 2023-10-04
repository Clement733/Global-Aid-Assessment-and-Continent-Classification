from dash import Dash, dcc, html, Input, Output
import plotly.express as px
import pandas as pd

app = Dash(__name__)
df = pd.read_csv('Country-data.csv')
dropdown_options = [{'label': country, 'value': country} for country in df['country'].unique()]


app.layout = html.Div([
    html.H4('Select Countries'),
    dcc.Dropdown(
        id="dropdown",
        options=dropdown_options,
        value=["Fri"],
        multi=True,
    ),
    dcc.Graph(id="bar"),
])


@app.callback(
    Output("bar", "figure"),
    Input("dropdown", "value"))
def update_bar_chart(selected_countries):
    mask = df["country"].isin(selected_countries)
    fig = px.bar(df[mask], x="country", y="child_mort",
                 color="gdpp", barmode="group", title='Child Mortality vs GDPP by Country',
                 labels={'country': "Countries", 'child_mort': 'Child Mortality'})
    return fig


if __name__ == "__main__":
    app.run(debug=True)
