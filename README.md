# Multi-Agent AI System

**Author:** Chibuike Obiora  
**Email:** obiorachibuike22@gmail.com  
**Assignment:** AI Engineering Internship - Enshrine Global Systems  

## Overview

This project implements a sophisticated multi-agent AI system that takes user goals, creates execution plans, and routes data between specialized agents to achieve complex objectives. Each agent enriches the output of the previous agent, creating a chain of intelligent processing that iteratively works toward goal completion.

### Key Features

- **Dynamic Planning**: Intelligent goal analysis and execution plan creation
- **Agent Chaining**: Sequential data enrichment between specialized agents
- **Iterative Refinement**: Automatic retry and refinement logic
- **Multi-API Integration**: Seamless integration with multiple public APIs
- **Comprehensive Evaluation**: Built-in goal satisfaction and trajectory analysis

## System Architecture

### Agent Flow Diagram

```
User Goal → PlannerAgent → [Agent Chain] → SummarizeAgent → Final Result
                ↓
            Dynamic Plan Creation
                ↓
    SpaceXAgent → WeatherAgent → NewsAgent → CryptoAgent
        ↓             ↓            ↓           ↓
   Launch Data → Weather Analysis → News → Crypto Prices
```

### Core Components

1. **BaseAgent**: Abstract base class defining agent interface
2. **PlannerAgent**: Analyzes goals and creates execution plans
3. **SpaceXAgent**: Fetches SpaceX launch information
4. **WeatherAgent**: Provides weather analysis for launch locations
5. **NewsAgent**: Retrieves relevant news articles
6. **CryptoAgent**: Fetches cryptocurrency market data
7. **SummarizeAgent**: Creates comprehensive summaries
8. **MultiAgentSystem**: Main orchestrator managing agent execution

## Agent Logic & Responsibilities

### PlannerAgent
- **Input**: User goal description
- **Logic**: NLP-based keyword analysis to determine required agents
- **Output**: Ordered execution plan with agent sequence
- **Routing**: Dynamically selects first agent based on goal analysis

### SpaceXAgent
- **Input**: Goal context or previous agent data
- **Logic**: Fetches next SpaceX launch using SpaceX API
- **Output**: Launch details, location coordinates, timing
- **Enhancement**: Enriches data with launchpad information

### WeatherAgent
- **Input**: Location data from SpaceXAgent
- **Logic**: Fetches weather data and analyzes launch suitability
- **Output**: Weather conditions with launch risk assessment
- **Enhancement**: Adds meteorological analysis for mission planning

### NewsAgent
- **Input**: Context from previous agents
- **Logic**: Searches for relevant news articles
- **Output**: Curated news articles related to the mission
- **Enhancement**: Provides current media context

### CryptoAgent
- **Input**: Any previous agent data
- **Logic**: Fetches current cryptocurrency prices
- **Output**: Market data for Bitcoin and Ethereum
- **Enhancement**: Adds financial market context

### SummarizeAgent
- **Input**: All previous agent outputs
- **Logic**: Intelligent summarization and conclusion generation
- **Output**: Comprehensive summary with recommendations
- **Enhancement**: Synthesizes all data into actionable insights

## API Integration

### Supported APIs

1. **SpaceX API** (`https://api.spacexdata.com/v4`)
   - Endpoints: `/launches/next`, `/launchpads/{id}`
   - Purpose: Launch information and location data
   - Rate Limit: None specified

2. **OpenWeatherMap API** (`http://api.openweathermap.org/data/2.5`)
   - Endpoints: `/weather`
   - Purpose: Weather conditions and forecasting
   - Rate Limit: 1000 calls/day (free tier)

3. **NewsAPI** (`https://newsapi.org/v2`)
   - Endpoints: `/everything`
   - Purpose: News article retrieval
   - Rate Limit: 100 requests/day (free tier)

4. **CoinGecko API** (`https://api.coingecko.com/api/v3`)
   - Endpoints: `/simple/price`
   - Purpose: Cryptocurrency market data
   - Rate Limit: 100 calls/minute

### API Key Configuration

Create a `.env` file in the project root:

```env
OPENWEATHER_API_KEY=your_openweather_api_key_here
NEWS_API_KEY=your_newsapi_key_here
```

**Note**: SpaceX and CoinGecko APIs are free and don't require API keys.

## Installation & Setup

### Prerequisites

- Python 3.8+
- pip package manager
- Internet connection for API calls

### Installation Steps

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd multi-agent-ai-system
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

4. **Run the system**
   ```bash
   python main.py
   ```

### Dependencies

```txt
requests>=2.31.0
asyncio
python-dotenv>=1.0.0
logging
dataclasses
typing
```

## Usage Examples

### Example 1: SpaceX Launch Weather Analysis
```python
goal = "Find the next SpaceX launch, check weather at that location, then summarize if it may be delayed"
result = await system.execute_goal(goal)
```

**Expected Flow**: PlannerAgent → SpaceXAgent → WeatherAgent → SummarizeAgent

**Output**: Comprehensive analysis of launch conditions with delay risk assessment.

### Example 2: News Summary
```python
goal = "Get news about SpaceX and summarize the current situation"
result = await system.execute_goal(goal)
```

**Expected Flow**: PlannerAgent → NewsAgent → SummarizeAgent

**Output**: Current SpaceX news with intelligent summarization.

### Example 3: Multi-Domain Analysis
```python
goal = "Check Bitcoin price, get SpaceX news, and summarize the technology sector"
result = await system.execute_goal(goal)
```

**Expected Flow**: PlannerAgent → CryptoAgent → NewsAgent → SummarizeAgent

**Output**: Financial and technology sector analysis.

## Evaluation Framework

### Goal Satisfaction Metrics

1. **Completion Rate**: Percentage of successfully executed agents
2. **Success Score**: Overall goal achievement rating (0-100%)
3. **Agent Trajectory**: Sequence of executed agents
4. **Error Analysis**: Failed agents and error messages
5. **Data Enrichment**: Quality and relevance of agent outputs

### Evaluation Example

```python
evaluation = system.evaluate_goal_satisfaction(goal)
print(f"Goal Satisfied: {evaluation['goal_satisfied']}")
print(f"Success Rate: {evaluation['satisfaction_score']:.1f}%")
print(f"Agent
