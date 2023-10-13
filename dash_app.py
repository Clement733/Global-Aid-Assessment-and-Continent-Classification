from dash import Dash, dcc, html, Input, Output
import plotly.express as px
import pandas as pd
from sklearn.preprocessing import RobustScaler
from sklearn.cluster import KMeans
from mpl_toolkits.mplot3d import Axes3D

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
    asia=['Afghanistan', 'Armenia', 'Azerbaijan', 'Bahrain', 'Bangladesh', 'Bhutan', 'Brunei', 'Cambodia', 'China', 'Georgia', 'India',
        'Indonesia', 'Iran', 'Iraq', 'Israel', 'Japan', 'Jordan', 'Kazakhstan',
        'Kuwait', 'Kyrgyz Republic', 'Lao', 'Lebanon', 'Malaysia', 'Maldives',
        'Mongolia', 'Myanmar', 'Namibia', 'Nepal', 'Oman', 'Pakistan',
        'Philippines', 'Qatar', 'Saudi Arabia', 'Singapore', 'South Korea',
        'Sri Lanka', 'Tajikistan', 'Thailand', 'Timor-Leste', 'Turkmenistan',
        'United Arab Emirates', 'Uzbekistan', 'Vietnam', 'Yemen']
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

df['Continent'] = df['country'].apply(assign_continent)
df.rename(columns={'child_mort': 'Child Mortality', 'exports':'Exports', 'health': 'Health Quality', 'imports': 'Imports',
                   'income': 'Income', 'inflation': 'Inflation', 'life_expec': 'Life expectancy', 'total_fer': 'Total Fertility',
                   'gdpp': 'GDP per Capital'}, inplace=True)

dropdown_options_first = [{'label': country, 'value': country} for country in df['country'].unique()]
dropdown_options_second = [{'label': col, 'value': col} for col in df.columns]

app.layout = html.Div([
    html.H4('Select Countries to see correlation between Child Mortality and GDPP'),
    dcc.Dropdown(
        id="dropdown_country",
        options=dropdown_options_first,
        value=["Fri"],
        multi=True,
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
    Input("dropdown_country", "value"))
def update_bar_chart(selected_countries):
    mask = df["country"].isin(selected_countries)
    fig = px.bar(df[mask], x="country", y="Child Mortality",
                 color="GDP per Capital", barmode="group", title='Child Mortality vs GDPP by Country',
                 labels={'country': "Countries"})
    return fig

@app.callback(
    Output("pie", "figure"),
    Input('dropdown_parameter', 'value'))
def update_pie_chart(dropdown_parameter):
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
    df_num = df.copy()
    df_num.set_index('country', inplace=True)
    print(df_num.head())
    df_num.drop(columns=['Continent'], inplace=True)
    df_num_scaled = RobustScaler().fit_transform(df_num)
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
