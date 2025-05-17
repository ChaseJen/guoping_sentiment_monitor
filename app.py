from flask import Flask, render_template, request, redirect, url_for
from elasticsearch import Elasticsearch
from datetime import datetime
import pandas as pd
import plotly.graph_objs as go
import json
import plotly
import markdown
import networkx as nx
from utils.visualization import *
from utils.deepseekQuery import *


app = Flask(__name__)
es = Elasticsearch("http://localhost:9200")
INDEX_NAME = "guoping"
players = ["马龙", "孙颖莎", "王楚钦", "樊振东", "陈梦"]




@app.route('/')
def index():
    player_score = request.args.get('player_score', players[0])
    player_network = request.args.get('player_network', players[0])

    # 情感评分图
    dates, scores = get_score_timeseries(player_score)
    score_fig = go.Figure()
    score_fig.add_trace(go.Scatter(x=dates, y=scores, mode='lines+markers', name='情感评分均值'))
    score_fig.update_layout(
        title=f"{player_score} 情感评分趋势",
        xaxis_title="日期",
        yaxis_title="均值",
        xaxis=dict(type="date", tickformat="%Y-%m-%d", tickangle=45)
    )

    # 社交网络图
    G = get_social_network_graph(player_network)
    social_fig = draw_networkx_plotly(G)

    score_graphJSON = json.dumps(score_fig, cls=plotly.utils.PlotlyJSONEncoder)
    social_graphJSON = json.dumps(social_fig, cls=plotly.utils.PlotlyJSONEncoder)

    return render_template('index.html', players=players,
                           player_score=player_score,
                           player_network=player_network,
                           score_graphJSON=score_graphJSON,
                           social_graphJSON=social_graphJSON)



@app.route('/player/<name>')
def player_posts(name):
    page = int(request.args.get("page", 1))
    size = 20
    offset = (page - 1) * size

    all_posts = fetch_posts_by_player(name)
    total = len(all_posts)
    posts = all_posts[offset:offset + size]

    total_pages = (total + size - 1) // size  

    return render_template(
        'player.html',
        name=name,
        posts=posts,
        players=players,
        current_page=page,
        total_pages=total_pages
    )


@app.route("/ai_search", methods=["GET"])
def ai_search():
    query = request.args.get("query", "")
    results = []
    ai_response = ""

    if query:  
        results = semantic_search(query)

        context = "\n\n".join([
            f"微博原文: {doc['text'][:300]}..." for doc in results
        ])

        ai_response = call_deepseek(query, context)
        

    return render_template(
        "searchResults.html",
        query=query,
        results=results,
        ai_response=ai_response
    )

if __name__ == '__main__':
    app.config['WTF_CSRF_ENABLED'] = False  
    app.run(debug=True,host='0.0.0.0', port=5001)  
