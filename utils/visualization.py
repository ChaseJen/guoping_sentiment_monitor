# 😊所有和可视化相关的方法都写这里

from flask import Flask, render_template, request, redirect, url_for
from elasticsearch import Elasticsearch
from datetime import datetime
import pandas as pd
import plotly.graph_objs as go
import json
import plotly
import networkx as nx


app = Flask(__name__)
es = Elasticsearch("http://localhost:9200")
INDEX_NAME = "guoping"
players = ["马龙", "孙颖莎", "王楚钦", "樊振东", "陈梦"]



# 这个函数在浏览界面也会用到，不要随便改
def fetch_posts_by_player(player):
    """
    从 Elasticsearch 中查询包含指定球员名的微博，字段包括：
    text、created_at、screen_name、user_authentication、reposts_count、comments_count、attitudes_count
    """
    query = {
        "query": {
            "term": {
                "keyword": player  
            }
        },
        "_source": [
            "text", "created_at", "screen_name", "user_authentication",
            "reposts_count", "comments_count", "attitudes_count"
        ],
        "size": 1000
    }

    try:
        res = es.search(index=INDEX_NAME, body=query)
        return [
            {
                "text": hit['_source'].get("text", ""),
                "created_at": hit['_source'].get("created_at", ""),
                "screen_name": hit['_source'].get("screen_name", "未知用户"),
                "user_authentication": hit['_source'].get("user_authentication", "普通用户"),
                "reposts_count": hit['_source'].get("reposts_count", 0),
                "comments_count": hit['_source'].get("comments_count", 0),
                "attitudes_count": hit['_source'].get("attitudes_count", 0)
            }
            for hit in res["hits"]["hits"]
        ]
    except Exception as e:
        print(f"⚠️ 查询 Elasticsearch 出错：{e}")
        return []


def get_score_timeseries(player):
    query = {
        "size": 0,
        "query": {
            "term": {"keyword": player}
        },
        "aggs": {
            "per_day": {
                "date_histogram": {
                    "field": "created_at",
                    "calendar_interval": "day"
                },
                "aggs": {
                    "avg_score": {
                        "avg": {"field": "score"}
                    }
                }
            }
        }
    }
    res = es.search(index=INDEX_NAME, body=query)

   
    print(f"[DEBUG] Aggregation: {json.dumps(res['aggregations'], indent=2, ensure_ascii=False)}")

    dates, scores = [], []
    for bucket in res['aggregations']['per_day']['buckets']:
        dates.append(bucket['key_as_string'])  # yyyy-MM-dd
        scores.append(bucket['avg_score']['value'] or 0)  
    return dates, scores


def get_social_network_graph(player):
    query = {
        "size": 1000,
        "query": {
            "term": {"keyword": player}
        },
        "_source": ["user_id", "screen_name", "at_users"]
    }
    res = es.search(index=INDEX_NAME, body=query)

    G = nx.DiGraph()
    for hit in res['hits']['hits']:
        source = hit['_source'].get("screen_name", "")
        at_users = hit['_source'].get("at_users", [])
        for target in at_users:
            if not G.has_node(source):
                G.add_node(source)
            if not G.has_node(target):
                G.add_node(target)
            if G.has_edge(source, target):
                G[source][target]['weight'] += 1
            else:
                G.add_edge(source, target, weight=1)
    return G

def draw_networkx_plotly(G):
    pos = nx.spring_layout(G, k=0.5, seed=42)  # 布局固定

    edge_x = []
    edge_y = []
    for edge in G.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_x += [x0, x1, None]
        edge_y += [y0, y1, None]

    edge_trace = go.Scatter(
        x=edge_x, y=edge_y,
        line=dict(width=0.5, color='#888'),
        hoverinfo='none',
        mode='lines')

    node_x = []
    node_y = []
    node_text = []
    for node in G.nodes():
        x, y = pos[node]
        node_x.append(x)
        node_y.append(y)
        node_text.append(node)

    node_trace = go.Scatter(
        x=node_x, y=node_y,
        mode='markers+text',
        text=node_text,
        textposition="bottom center",
        hoverinfo='text',
        marker=dict(
            showscale=True,
            colorscale='YlGnBu',
            reversescale=True,
            color=[G.degree(n) for n in G.nodes()],
            size=10,
            colorbar=dict(
                thickness=15,
                title=dict(text='连接数', side='right'),
                xanchor='left',
            ),
            line_width=2))

    fig = go.Figure(data=[edge_trace, node_trace],
                    layout=go.Layout(
                        title=dict(text='社交网络图', font=dict(size=16)),
                        showlegend=False,
                        hovermode='closest',
                        margin=dict(b=20, l=5, r=5, t=40),
                        xaxis=dict(showgrid=False, zeroline=False),
                        yaxis=dict(showgrid=False, zeroline=False))
                    )
    return fig
