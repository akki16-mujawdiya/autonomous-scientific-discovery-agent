# Autonomous Scientific Discovery Agent

An AI-based research agent that helps automate the scientific research process using RAG, multiple AI agents, research papers, and Python experiments.

## Project Overview

The main goal of this project is to build an AI system that can assist in scientific research with minimum human intervention.

The system collects recent research papers from ArXiv and PubMed, retrieves useful information from the papers, generates research hypotheses, writes and executes Python code for experiments, checks the results, and prepares a research draft.

## How It Works

ArXiv + PubMed
        ↓
Collect Research Papers
        ↓
Vector Database
        ↓
RAG
        ↓
Literature Reviewer
        ↓
Hypothesis Generator
        ↓
Code Executor
        ↓
Python Experiment
        ↓
Check Results
        ↓
Research Draft

## Main Features

- Collect research papers from ArXiv and PubMed
- Store research information in a vector database
- Use RAG to retrieve relevant research information
- Use multiple AI agents for different tasks
- Generate research hypotheses
- Generate and execute Python experiment code
- Run generated code in a secure Docker environment
- Debug and improve code when errors occur
- Analyze charts and graphs from research papers
- Check experiment results using a Critic Agent
- Generate research abstracts and drafts
- Monitor the research process using a Streamlit dashboard

## AI Agents

### Literature Reviewer

Reviews research papers and finds useful information related to the research topic.

### Hypothesis Generator

Uses the available research information to generate new research hypotheses.

### Code Executor

Generates and runs Python code to test the generated hypothesis.

### Critic Agent

Checks the experiment results and evaluates their statistical significance.

## Technologies Used

- Python
- LangChain / AutoGen
- RAG
- ArXiv API
- PubMed API
- Milvus / Pinecone
- Docker
- PyTorch
- Transformers
- Hugging Face
- Streamlit
- Git
- GitHub

## Project Workflow

### Week 1

- Build the multi-agent system
- Create Literature Reviewer, Hypothesis Generator, and Code Executor
- Connect ArXiv and PubMed APIs
- Set up the vector database
- Set up GitHub branches

### Week 2

- Implement RAG
- Create the Docker execution sandbox
- Run Python experiments safely
- Add automatic error debugging

### Week 3

- Add multimodal research data such as charts and graphs
- Add the Critic Agent
- Check p-values and confidence intervals
- Improve memory handling for long-running tasks

### Week 4

- Generate research abstracts
- Create the Streamlit monitoring dashboard
- Evaluate the system using recent research papers
- Prepare the final research and architecture report

## Expected Output

- Research paper information
- Generated research hypotheses
- Experimental Python code
- Experiment results
- Statistical evaluation
- Research abstract or draft
- Monitoring dashboard

## Project Status

This project is currently under development.

## Author

**Akki Mujawdiya**

GitHub: akki16-mujawdiya
