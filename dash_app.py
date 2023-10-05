from dash import Dash, dcc, html, Input, Output
import plotly.express as px
import pandas as pd

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

df['continent'] = df['country'].apply(assign_continent)

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
        value='gdpp',
        clearable=False
    ),
    dcc.Graph(id='pie')
])


@app.callback(
    Output("bar", "figure"),
    Input("dropdown_country", "value"))
def update_bar_chart(selected_countries):
    mask = df["country"].isin(selected_countries)
    fig = px.bar(df[mask], x="country", y="child_mort",
                 color="gdpp", barmode="group", title='Child Mortality vs GDPP by Country',
                 labels={'country': "Countries", 'child_mort': 'Child Mortality'})
    return fig

@app.callback(
    Output("pie", "figure"),
    Input('dropdown_parameter', 'value'))
def update_pie_chart(dropdown_parameter):
    new_df = df.groupby('continent')[dropdown_parameter].mean().reset_index()
    fig = px.pie(new_df, names='continent', values=dropdown_parameter, hole=.3, title=f'Mean {dropdown_parameter} per Continent')
    return fig


if __name__ == "__main__":
    app.run_server(debug=True)
