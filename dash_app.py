from dash import Dash, dcc, html, Input, Output
import plotly.express as px
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from sklearn.cluster import KMeans
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
from plotly.subplots import make_subplots

app = Dash(__name__)
df = pd.read_csv('Country-data.csv')

def assign_continent(country):
    africa = ["Algeria", "Angola", "Benin", "Botswana", "Burkina Faso", "Burundi", "Cameroon", "Cape Verde",
    "Central African Republic", "Chad", "Comoros", "Congo, Dem. Rep.", "Congo, Rep.", "Costa Rica", "Cote d'Ivoire", "Egypt",
    "Equatorial Guinea", "Eritrea", "Gabon", "Gambia", "Ghana", "Guinea", "Guinea-Bissau", "Kenya", "Lesotho", "Liberia", "Libya",
    "Madagascar", "Malawi", "Mali", "Mauritania", "Mauritius", "Morocco", "Mozambique", "Niger", "Nigeria", "Rwanda", "Senegal",
    "Seychelles", "Sierra Leone", "South Africa", "Sudan", "Tanzania", "Togo", "Tunisia", "Uganda", "Zambia"]
    europe = ["Albania", "Austria", "Belarus", "Belgium", "Bosnia and Herzegovina", "Bulgaria", "Croatia", "Cyprus", "Czech Republic",
    "Denmark", "Estonia", "Finland", "France", "Germany", "Greece", "Hungary", "Iceland", "Ireland", "Italy", "Latvia", "Lithuania",
    "Luxembourg", "Macedonia, FYR", "Malta", "Moldova", "Montenegro", "Netherlands", "Norway", "Poland", "Portugal", "Romania", "Russia", "Serbia",
    "Slovak Republic", "Slovenia", "Spain", "Sweden", "Switzerland", "Turkey", "Ukraine", "United Kingdom"]
    north_america = ["Antigua and Barbuda", "Bahamas", "Barbados", "Belize", "Canada", "Costa Rica", "Dominican Republic",
    "El Salvador", "Grenada", "Guatemala", "Haiti", "Jamaica", "Panama", "St. Vincent and the Grenadines", "United States"]
    south_america = ["Argentina", "Bolivia", "Brazil", "Chile", "Colombia", "Ecuador", "Guyana", "Paraguay", "Peru", "Suriname",
    "Uruguay", "Venezuela"]
    oceania = ["Australia", "Fiji", "Kiribati", "Micronesia, Fed. Sts.", "New Zealand", "Samoa", "Solomon Islands", "Tonga", "Vanuatu"]
    if country in africa:
        return "Africa"
    elif country in europe:
        return "Europe"
    elif country in north_america:
        return 'North-America'
    elif country in south_america:
        return "South-America"
    elif country in oceania:
        return "Oceania"
    return "Asia"

df.rename(columns={'child_mort': 'Child Mortality', 'exports':'Exports', 'health': 'Health Quality', 'imports': 'Imports',
                   'income': 'Income', 'inflation': 'Inflation', 'life_expec': 'Life expectancy', 'total_fer': 'Total Fertility',
                   'gdpp': 'GDP per Capital'}, inplace=True)

drop_options = [{'label': col, 'value': col} for col in df[['Child Mortality', 'Exports', 'Health Quality',
                                                           'Imports', 'Income', 'Inflation', 'Life expectancy', 'Total Fertility',
                                                           'GDP per Capital']]]
dropdown_options_second = [{'label': col, 'value': col} for col in df.columns]

df_num = df.copy()
df_num.set_index('country', inplace=True)
df_num_scaled = MinMaxScaler().fit_transform(df_num)

app.layout = html.Div([
    html.H4('Select feature you would like to see the first 5, middle 5, and last 5 countries'),
    dcc.Dropdown(
        id="selected_feature",
        options=drop_options,
        value='Child Mortality',
        clearable=False,
    ),
    dcc.Graph(id="bar"),

    html.H4("Select parameter you would like to compare continents through"),
    html.P('Parameter:'),
    dcc.Dropdown(
        id='dropdown_parameter',
        options=dropdown_options_second,
        value='GDP per Capital',
        clearable=False
    ),
    dcc.Graph(id='pie'),

    html.H4("3D Plot representing features meaningful in clustering"),
    html.P('You can change the number of clusters to see the differences:'),
    dcc.Dropdown(
        id='cluster_number',
        options=[{'label': str(i), 'value': i} for i in range(1,10)],
        value=2,
        clearable=False
    ),
    dcc.Graph(id='scatter',
              style={'height': '600px', 'width': '1500px'}),

    html.H3("Although I don't recommend, you can change the plotting features here"),
    html.P('The x-axis feature here:'),
    dcc.Dropdown(
        id='x_axis',
        options = dropdown_options_second,
        value = 'Income',
        clearable=False
    ),
    html.P('The y-axis feature here:'),
    dcc.Dropdown(
        id='y_axis',
        options = dropdown_options_second,
        value = 'GDP per Capital',
        clearable=False
    ),
    html.P('The z-axis feature here:'),
    dcc.Dropdown(
        id='z_axis',
        options = dropdown_options_second,
        value = 'Health Quality',
        clearable=False
    )
])


@app.callback(
    Output("bar", "figure"),
    Input("selected_feature", "value"))
def update_bar_chart(selected_feature):
    sorted_df = df.sort_values(by=[selected_feature], ascending=False)

    fig = make_subplots(rows=1, cols=3, subplot_titles=[
        f'Top 5 {selected_feature}',
        f'Middle 5 {selected_feature}',
        f'Bottom 5 {selected_feature}'
    ])

    for i, subset in enumerate([sorted_df.head(5), sorted_df.iloc[80:85], sorted_df.tail(5)]):
        chart = px.bar(
            subset,
            x='country',
            y=selected_feature,
            labels={'country': 'Countries', selected_feature: selected_feature},
        )
        for trace in chart.data:
            fig.add_trace(trace, row=1, col=i+1)

    fig.update_layout(
        title='Comparison of Top, Middle, and Bottom 5 Countries',
        showlegend=False,
    )

    return fig

@app.callback(
    Output("pie", "figure"),
    Input('dropdown_parameter', 'value'))
def update_pie_chart(dropdown_parameter):
    df['Continent'] = df['country'].apply(assign_continent)
    new_df = df.groupby('Continent')[dropdown_parameter].mean().reset_index()
    fig = px.pie(new_df, names='Continent', values=dropdown_parameter, hole=.3, title=f'Mean {dropdown_parameter} per Continent')
    return fig

@app.callback(
    Output('scatter', 'figure'),
    Input('cluster_number', 'value'),
    Input('x_axis', 'value'),
    Input('y_axis', 'value'),
    Input('z_axis', 'value'))
def scatter_model(cluster_number, x_axis, y_axis, z_axis):
    kmeans = KMeans(n_clusters=cluster_number, max_iter=300, random_state=1)
    kmeans.fit(df_num_scaled)
    labels = kmeans.labels_
    df_num['Cluster'] = labels
    df_num['Index'] = df_num.index
    fig = px.scatter_3d(df_num,
                        x=x_axis,
                        y=y_axis,
                        z=z_axis,
                        color='Cluster',
                        hover_data=['Index'],
                        title='Interactive KMeans 3D Scatter Plot'
                    )
    return fig


if __name__ == "__main__":
    app.run_server(debug=True)
