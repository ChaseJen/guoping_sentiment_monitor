

# 🔍 国乒微博舆情分析系统

本项目是一个基于 Flask 的微博舆情分析系统，支持情绪分析、交互式检索与动态可视化功能，内置 AI 自动生成内容解释。

---

## 🧩 项目功能

* ✅ **基于DS-R1的智能搜索**
* ✅ **高人气球员的相关微博一览**
* ✅ **舆情走向及社交网络可视化**
---

## 📁 项目结构

```bash
project/
│
├── app.py                    # 主 Flask 应用
├── templates/
│   └── index.html
│   └── player.html
│   └── searchResults.html          
│
├── static/
│   └── style.css
│   └── weiboPosts.css
│   └── aiResponse.css        
│   ├── js/
│   │   └── particles.js      
│
├── utils/
│   └── deepseekQuery.py             
│   └── visualization.py          
│
├── requirements.txt
└── README.md                
```

---

## 🛠️ 安装与运行

### 1. 克隆仓库

```bash
git clone git@github.com:ChaseJen/guoping_sentiment_monitor.git
cd guoping_sentiment_monitor
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 启动服务

```bash
python app.py
```

运行在 [http://127.0.0.1:5001/](http://127.0.0.1:5001/)

---

## 🧠 技术栈

| 类型    | 技术                          |
| ----- | --------------------------- |
| 后端框架  | Flask                       |
| 前端 UI | HTML / CSS / JS / Plotly    |
| 动画背景  | Canvas 粒子系统（原生 JS）          |
| 检索系统  | AI智搜            |
| 数据存储  | Elasticsearch       |
| AI能力  | AI生成回应解释（如总结、分析）            |

---

## 🎨 UI 亮点

* 🌌 深色界面，视觉友好
* 🌠 粒子背景与鼠标交互，点击触发动画
* 📊 情绪分析可视化图表


