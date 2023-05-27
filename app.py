import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.graph_objects as go
import random
import math
from city import City

def generate_color_list(n):
    color_list = []
    hue_step = 360 / n

    for i in range(n):
        hue = int(i * hue_step)
        saturation = 50  # You can adjust the saturation and lightness values as desired
        lightness = 50   # Higher values make colors brighter

        # Convert HSL to RGB
        hue /= 360.0
        saturation /= 100.0
        lightness /= 100.0

        if saturation == 0:
            red = green = blue = lightness
        else:
            def hue_to_rgb(p, q, t):
                if t < 0:
                    t += 1
                if t > 1:
                    t -= 1
                if t < 1 / 6:
                    return p + (q - p) * 6 * t
                if t < 1 / 2:
                    return q
                if t < 2 / 3:
                    return p + (q - p) * (2 / 3 - t) * 6
                return p

            q = lightness * (1 + saturation) if lightness < 0.5 else lightness + saturation - lightness * saturation
            p = 2 * lightness - q
            red = hue_to_rgb(p, q, hue + 1 / 3)
            green = hue_to_rgb(p, q, hue)
            blue = hue_to_rgb(p, q, hue - 1 / 3)

        # Scale RGB values to 255
        red = int(red * 255)
        green = int(green * 255)
        blue = int(blue * 255)

        color_list.append((red, green, blue))

    return color_list

def random_point_in_circle(radius):
    # Generate a random point within a circle
    r = radius * math.sqrt(random.random())
    theta = random.uniform(0, 2*math.pi)
    x = r * math.cos(theta)
    y = r * math.sin(theta)
    return x, y

def distance(x1, y1, x2, y2):
    # Calculate the Euclidean distance between two points
    return math.sqrt((x2 - x1)**2 + (y2 - y1)**2)

# Initialize the cities
num_cities = 100
num_nations = 10
cities_per_nation = num_cities // num_nations
cities = []
nation_centers = []

color_list = generate_color_list(num_nations)

for i in range(num_nations):
    while True:
        nation_center_x = random.randint(100, 900)  # Avoid edges of the 1000x1000 grid
        nation_center_y = random.randint(100, 900)  # Avoid edges of the 1000x1000 grid

        # Check if the new nation is far enough away from all existing nations
        if all(distance(nation_center_x, nation_center_y, x, y) >= 200 for x, y in nation_centers):
            break

    nation_centers.append((nation_center_x, nation_center_y))
    nation_color = 'rgba({},{},{},1)'.format(*color_list[i])

    for j in range(cities_per_nation):
        x_offset, y_offset = random_point_in_circle(100)
        x = nation_center_x + x_offset
        y = nation_center_y + y_offset
        city = City(i*cities_per_nation+j, 
                    [random.uniform(0, 100)],           #resources
                    10,                                 #population
                    [random.uniform(0, 100)],           #production
                    [1],                                #utilization exponent
                    random.uniform(1, 1.1),             #growth rate
                    x, y, f"Nation {i+1}", nation_color)
        cities.append(city)

app = dash.Dash(__name__)

app.layout = html.Div([
    dcc.Graph(id='city-graph', style={"height": "90vh", "width": "100%"}),
    html.Button('Next Step', id='next-step-button'),
], style={"height": "100vh", "width": "100%"})

@app.callback(
    Output('city-graph', 'figure'),
    Input('next-step-button', 'n_clicks')
)
def update_graph(n_clicks):
    if n_clicks is not None:
        # Run the next step of the simulation
        for city in cities:
            city.step()
            if city.population <= 0:
                cities.remove(city)

    # Create the scatter plot
    figure = go.Figure(
        data=[
            go.Scatter(
                x=[city.x for city in cities if city.nation == f"Nation {i+1}"],  # Use the city's x-coordinate
                y=[city.y for city in cities if city.nation == f"Nation {i+1}"],  # Use the city's y-coordinate
                mode='markers',
                text=[f"City {city.id} of {city.nation}:<br>Population: {city.population}<br>Resources: {city.resources}" for city in cities if city.nation == f"Nation {i+1}"],
                hoverinfo='text',
                marker=dict(
                    color=[city.color for city in cities if city.nation == f"Nation {i+1}"],  # Set the color of the markers
                    size=[max(city.population,10) for city in cities if city.nation == f"Nation {i+1}"],  # Set the size of the markers
                    sizemode='area',  # The size represents the area of the markers
                ),               
                name=f"Nation {i+1}"
            ) for i in range(num_nations)
        ]
    )
    # Set the layout to be square
    figure.update_layout(
        autosize=True,
        xaxis=dict(range=[0, 1000], autorange=False),
        yaxis=dict(range=[0, 1000], autorange=False),
        xaxis_title="X Coordinate",
        yaxis_title="Y Coordinate",
    )

    return figure

if __name__ == '__main__':
    app.run_server(debug=True)
