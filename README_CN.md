# LivCourse-聊天机器人

[**🇨🇳中文**](./README_CN.md) | [**🌐英文**](./README.md) | [**❓问题**](https://github.com/XavierXinchi/LivCourse-ChatBot/issues)

<p align="center">
    <img alt="GitHub" src="https://img.shields.io/badge/license-Apache--2.0-blue">
    <img alt="version" src="https://img.shields.io/badge/version-Beta_1.0-6666CC">
    <img alt="os" src="https://img.shields.io/badge/os-Linux-fcea63">
    <img alt="GitHub last commit" src="https://img.shields.io/badge/last%20commit-March-f15b31">
</p>


## 📝 简介

LivCourse-聊天机器人是一个**基于知识图谱（KG）和大型语言模型（LLM）融合**的关于利物浦大学课程聊天机器人，它结合了 LLM 和 KG 的优势，既能回答通用问题，也能回答特定领域的问题，例如有关利物浦大学课程模块的信息。

💡下图显示了部署后的聊天机器人演示

![](./img/demo.png)

## 💫 特征

- 基于记忆： 模型可以理解用户之前问题的上下文，从而产生有时序性的输出
- 特定领域： 该模型可回答有关利物浦大学课程信息的具体问题
- 可扩展性： 开发人员可为模型学习添加额外的个性化语料库

下图展示了模型的结构：

![](/Users/xavier/vscodeprojects/LivCourse_ChatBot/img/diagram.png)

在第一个模块中，大语言模型将把用户的原始问题与历史对话结合起来，生成一个经过处理的问题。

在第二个模块中，经过处理的问题将被发送给代理，代理将产生一连串的思考，以确定该问题属于哪个类别，并将其交给相应类别的函数，以生成最终答案

- Generic_func: 用于回答通用知识领域的问题，如问候语
- Retrival_func: 用于回答额外语料库中的问题，例如本项目中的校园体育馆信息
- Graph_func: 用于回答有关图数据库 [neo4j](https://neo4j.com/?utm_source=Google&utm_medium=PaidSearch&utm_campaign=Evergreenutm_content%3DEMEA-Search-SEMBrand-Evergreen-None-SEM-SEM-NonABM&utm_term=neo4j&utm_adgroup=core-brand&gad_source=1&gclid=CjwKCAiAopuvBhBCEiwAm8jaMXhwJ32kD3nX9mhZ08_5oWgJRYbsGqg8Nw8ele399ED5WMwsB5axgBoCCnsQAvD_BwE) 中存储的节点和关系的问题，如利物浦大学课程、学位、模块等
- Search_func: 用于在其他功能无法生成正确答案时，通过搜索引擎（[Google](https://www.google.com/)）回答问题

## 🛠️ 快速开始

### 1. 安装依赖项

创建虚拟 conda 环境，激活并安装软件包：

   ```shell
conda create -n LivCourse python=3.9
conda activate LivCourse
pip install -r requirements.txt
   ```

### 2. 设置neo4j图形数据库

在其 [网站](https://platform.openai.com/api-keys) 申请 OpenAI API 密钥。

进入`.env`文件，设置`OPENAI_API_KEY`、`NEO4J_URI`和`NEO4J_PASSWORD`。

运行以下代码在 neo4j 数据库中生成知识图谱：

```shell
python gen_kg.py
```

### 3. 使用 LangSmith 监控应用程序（可选）

访问 [LangSmith](https://smith.langchain.com/) 网站申请 API 密钥，并创建名为 `LivCourse-ChatBot` 的项目，配置连接 LangSmith 的环境。

```shell
export LANGCHAIN_TRACING_V2=true
export LANGCHAIN_ENDPOINT="https://api.smith.langchain.com"
export LANGCHAIN_API_KEY="<your langchain smith api>"
export LANGCHAIN_PROJECT="LivCourse-ChatBot"
```

### 4. 运行聊天机器人

```shell
python app.py
```

文件结构如下：

```shell
.
├── LICENSE
├── README.md
├── __pycache__
│   ├── agent.cpython-39.pyc
│   ├── config.cpython-39.pyc
│   ├── prompt.cpython-39.pyc
│   ├── service.cpython-39.pyc
│   └── utils.cpython-39.pyc
├── agent.py
├── app.py
├── config.py
├── data
│   └── db
│       ├── chroma.sqlite3
│       └── f4e6c6f1-3933-4325-b4d3-51ea2dceec57
│           ├── data_level0.bin
│           ├── header.bin
│           ├── length.bin
│           └── link_lists.bin
├── data_process.py
├── dataset
│   └── dataset.json
├── gen_kg.py
├── img
│   ├── demo.png
│   ├── diagram.png
│   └── diagram.svg
├── inputs
│   └── gym.txt
├── prompt.py
├── requirements.txt
├── service.py
└── utils.py
```

## ⚠️ 免责声明

本项目相关资源仅供学术研究使用，严禁用于商业用途。在使用涉及第三方代码的部分时，请严格遵守相应的开源协议。对于模型输出的任何内容，本项目不承担任何法律责任，也不承担因使用相关资源和输出结果而可能产生的任何损失。

## 🌟 Support

如果您喜欢这个项目，请不要忘记给这个仓库打上星✨。