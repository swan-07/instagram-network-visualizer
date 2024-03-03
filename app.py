import networkx as nx
import plotly.graph_objects as go
from dash import dcc, html, Input, Output
import dash
from scraper import fetch_data  # Assuming this function returns nodes and edges


# Initialize the Dash app
app = dash.Dash(__name__)

app.layout = html.Div([
    html.H1("Instagram Network Visualizer"),
    dcc.Input(id='username', type='text', placeholder='Enter Instagram Username'),
    dcc.Input(id='depth', type='number', placeholder='Enter Search Depth (1<=x<=3)'),
    html.Button('Show', id='submit-val', n_clicks=0),
    dcc.Graph(id='network-graph')
])

@app.callback(
    Output('network-graph', 'figure'),
    [Input('submit-val', 'n_clicks')],
    [dash.dependencies.State('username', 'value'),
     dash.dependencies.State('depth', 'value')]
)

def update_graph(n_clicks, username, depth):
    if n_clicks > 0 and username and depth and depth < 3:
        nodes, edges = fetch_data(username, depth)

        # Create a networkx graph
        G = nx.Graph()
        G.add_nodes_from(nodes)
        G.add_edges_from(edges)

        # Calculate node positions using one of networkx's layout algorithms
        pos = nx.spring_layout(G)

        # Create edge traces
        edge_trace = []
        for edge in G.edges():
            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]
            edge_trace.append(go.Scatter(x=[x0, x1, None], y=[y0, y1, None],
                                         mode='lines',
                                         line=dict(width=2, color='black'),
                                         hoverinfo='none'))

 # Create node traces
        node_trace = go.Scatter(x=[], y=[], 
                                mode='markers', 
                                hoverinfo='text', 
                                marker=dict(showscale=True, 
                                            colorscale='YlGnBu',
                                            reversescale=True,
                                            color=[], 
                                            size=10, 
                                            colorbar=dict(thickness=15, 
                                                          title='Node Connections',
                                                          xanchor='left', 
                                                          titleside='right')))
        for node in G.nodes():
            x, y = pos[node]
            node_trace['x'] += (x,)
            node_trace['y'] += (y,)
        
         # Color node points by the number of connections.
        for node, adjacencies in enumerate(G.adjacency()):
            node_trace['marker']['color'] += (len(adjacencies[1]),)

        fig = go.Figure(data=edge_trace + [node_trace],
                        layout=go.Layout(showlegend=False, hovermode='closest',
                                         margin={'b': 0, 'l': 0, 'r': 0, 't': 0},
                                         xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                                         yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)))

        return fig
    else:
        return go.Figure()
    
if __name__ == '__main__':
    app.run_server(debug=True)