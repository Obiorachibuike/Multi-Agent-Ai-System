"""
Multi-Agent AI System using Google ADK
Assignment for Enshrine Global Systems AI Engineering Internship
Author: Chibuike Obiora
"""

import os
import json
import requests
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from abc import ABC, abstractmethod
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class AgentResult:
    """Represents the result of an agent's execution"""
    agent_name: str
    success: bool
    data: Dict[str, Any]
    message: str
    next_agent: Optional[str] = None

@dataclass
class Goal:
    """Represents a user goal and its execution state"""
    description: str
    plan: List[str]
    current_step: int = 0
    results: List[AgentResult] = None
    is_complete: bool = False
    
    def __post_init__(self):
        if self.results is None:
            self.results = []

class BaseAgent(ABC):
    """Abstract base class for all agents"""
    
    def __init__(self, name: str):
        self.name = name
        self.logger = logging.getLogger(f"Agent.{name}")
    
    @abstractmethod
    async def execute(self, input_data: Dict[str, Any]) -> AgentResult:
        """Execute the agent's logic"""
        pass
    
    def log_execution(self, input_data: Dict[str, Any], result: AgentResult):
        """Log agent execution details"""
        self.logger.info(f"Executed with input: {json.dumps(input_data, indent=2)}")
        self.logger.info(f"Result: {result.message}")

class PlannerAgent(BaseAgent):
    """Agent responsible for creating execution plans from user goals"""
    
    def __init__(self):
        super().__init__("Planner")
        self.agent_registry = {
            "spacex": "SpaceXAgent",
            "weather": "WeatherAgent",
            "news": "NewsAgent",
            "crypto": "CryptoAgent",
            "summarizer": "SummarizeAgent"
        }
    
    async def execute(self, input_data: Dict[str, Any]) -> AgentResult:
        """Create a plan based on the user goal"""
        goal_text = input_data.get("goal", "").lower()
        
        # Analyze goal and create plan
        plan = self._analyze_goal(goal_text)
        
        result = AgentResult(
            agent_name=self.name,
            success=True,
            data={"plan": plan, "original_goal": input_data.get("goal")},
            message=f"Created execution plan with {len(plan)} steps",
            next_agent=plan[0] if plan else None
        )
        
        self.log_execution(input_data, result)
        return result
    
    def _analyze_goal(self, goal_text: str) -> List[str]:
        """Analyze goal text and return execution plan"""
        plan = []
        
        # SpaceX launch detection
        if any(keyword in goal_text for keyword in ["spacex", "launch", "rocket", "falcon", "dragon"]):
            plan.append("SpaceXAgent")
        
        # Weather detection
        if any(keyword in goal_text for keyword in ["weather", "temperature", "rain", "storm", "delay"]):
            plan.append("WeatherAgent")
        
        # News detection
        if any(keyword in goal_text for keyword in ["news", "article", "report", "update"]):
            plan.append("NewsAgent")
        
        # Crypto detection
        if any(keyword in goal_text for keyword in ["bitcoin", "crypto", "btc", "eth", "price"]):
            plan.append("CryptoAgent")
        
        # Always end with summarizer if multiple agents
        if len(plan) > 1 or any(keyword in goal_text for keyword in ["summarize", "summary", "conclude"]):
            plan.append("SummarizeAgent")
        
        # Default plan if nothing detected
        if not plan:
            plan = ["NewsAgent", "SummarizeAgent"]
        
        return plan

class SpaceXAgent(BaseAgent):
    """Agent for fetching SpaceX launch information"""
    
    def __init__(self):
        super().__init__("SpaceX")
        self.api_url = "https://api.spacexdata.com/v4"
    
    async def execute(self, input_data: Dict[str, Any]) -> AgentResult:
        """Fetch next SpaceX launch information"""
        try:
            # Get next launch
            response = requests.get(f"{self.api_url}/launches/next")
            response.raise_for_status()
            launch_data = response.json()
            
            # Get launchpad details
            launchpad_id = launch_data.get("launchpad")
            launchpad_response = requests.get(f"{self.api_url}/launchpads/{launchpad_id}")
            launchpad_data = launchpad_response.json() if launchpad_response.status_code == 200 else {}
            
            enriched_data = {
                "launch_name": launch_data.get("name"),
                "launch_date": launch_data.get("date_utc"),
                "details": launch_data.get("details", "No details available"),
                "launchpad": {
                    "name": launchpad_data.get("full_name", "Unknown"),
                    "location": launchpad_data.get("locality", "Unknown"),
                    "region": launchpad_data.get("region", "Unknown"),
                    "latitude": launchpad_data.get("latitude"),
                    "longitude": launchpad_data.get("longitude")
                },
                "rocket": launch_data.get("rocket"),
                "success_probability": launch_data.get("success", None)
            }
            
            result = AgentResult(
                agent_name=self.name,
                success=True,
                data=enriched_data,
                message=f"Retrieved next SpaceX launch: {enriched_data['launch_name']}",
                next_agent="WeatherAgent"
            )
            
        except Exception as e:
            result = AgentResult(
                agent_name=self.name,
                success=False,
                data={},
                message=f"Failed to fetch SpaceX data: {str(e)}"
            )
        
        self.log_execution(input_data, result)
        return result

class WeatherAgent(BaseAgent):
    """Agent for fetching weather information"""
    
    def __init__(self):
        super().__init__("Weather")
        self.api_key = os.getenv("OPENWEATHER_API_KEY")
        self.api_url = "http://api.openweathermap.org/data/2.5"
    
    async def execute(self, input_data: Dict[str, Any]) -> AgentResult:
        """Fetch weather information for launch location"""
        try:
            if not self.api_key:
                # Use mock data if no API key
                weather_data = self._get_mock_weather_data()
            else:
                # Extract location from previous agent data
                location = self._extract_location(input_data)
                weather_data = self._fetch_weather(location)
            
            # Analyze weather for launch suitability
            analysis = self._analyze_weather_for_launch(weather_data)
            
            enriched_data = {
                "weather": weather_data,
                "launch_suitability": analysis,
                "previous_data": input_data
            }
            
            result = AgentResult(
                agent_name=self.name,
                success=True,
                data=enriched_data,
                message=f"Weather analysis complete. Launch suitability: {analysis['recommendation']}",
                next_agent="SummarizeAgent"
            )
            
        except Exception as e:
            result = AgentResult(
                agent_name=self.name,
                success=False,
                data={"previous_data": input_data},
                message=f"Failed to fetch weather data: {str(e)}"
            )
        
        self.log_execution(input_data, result)
        return result
    
    def _extract_location(self, input_data: Dict[str, Any]) -> str:
        """Extract location from previous agent data"""
        if "launchpad" in input_data:
            location = input_data["launchpad"].get("location", "Cape Canaveral")
        else:
            location = "Cape Canaveral"  # Default SpaceX location
        return location
    
    def _fetch_weather(self, location: str) -> Dict[str, Any]:
        """Fetch weather data from OpenWeatherMap API"""
        response = requests.get(
            f"{self.api_url}/weather",
            params={"q": location, "appid": self.api_key, "units": "metric"}
        )
        response.raise_for_status()
        return response.json()
    
    def _get_mock_weather_data(self) -> Dict[str, Any]:
        """Return mock weather data when API key is not available"""
        return {
            "weather": [{"main": "Clear", "description": "clear sky"}],
            "main": {"temp": 25, "humidity": 60, "pressure": 1013},
            "wind": {"speed": 5.2, "deg": 180},
            "visibility": 10000,
            "name": "Cape Canaveral"
        }
    
    def _analyze_weather_for_launch(self, weather_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze weather conditions for launch suitability"""
        main_weather = weather_data.get("weather", [{}])[0].get("main", "").lower()
        wind_speed = weather_data.get("wind", {}).get("speed", 0)
        visibility = weather_data.get("visibility", 10000)
        
        # Simple launch suitability logic
        issues = []
        if "rain" in main_weather or "storm" in main_weather:
            issues.append("Precipitation detected")
        if wind_speed > 15:
            issues.append(f"High wind speeds: {wind_speed} m/s")
        if visibility < 5000:
            issues.append(f"Poor visibility: {visibility}m")
        
        if not issues:
            recommendation = "FAVORABLE"
            risk_level = "LOW"
        elif len(issues) == 1:
            recommendation = "CAUTION"
            risk_level = "MEDIUM"
        else:
            recommendation = "UNFAVORABLE"
            risk_level = "HIGH"
        
        return {
            "recommendation": recommendation,
            "risk_level": risk_level,
            "issues": issues,
            "analysis": f"Weather conditions are {recommendation.lower()} for launch"
        }

class NewsAgent(BaseAgent):
    """Agent for fetching relevant news"""
    
    def __init__(self):
        super().__init__("News")
        self.api_key = os.getenv("NEWS_API_KEY")
        self.api_url = "https://newsapi.org/v2"
    
    async def execute(self, input_data: Dict[str, Any]) -> AgentResult:
        """Fetch relevant news articles"""
        try:
            if not self.api_key:
                # Use mock data if no API key
                news_data = self._get_mock_news_data()
            else:
                # Determine search query from input data
                query = self._generate_search_query(input_data)
                news_data = self._fetch_news(query)
            
            enriched_data = {
                "news_articles": news_data,
                "previous_data": input_data
            }
            
            result = AgentResult(
                agent_name=self.name,
                success=True,
                data=enriched_data,
                message=f"Retrieved {len(news_data)} relevant news articles",
                next_agent="SummarizeAgent"
            )
            
        except Exception as e:
            result = AgentResult(
                agent_name=self.name,
                success=False,
                data={"previous_data": input_data},
                message=f"Failed to fetch news data: {str(e)}"
            )
        
        self.log_execution(input_data, result)
        return result
    
    def _generate_search_query(self, input_data: Dict[str, Any]) -> str:
        """Generate search query based on input data"""
        if "launch_name" in input_data:
            return f"SpaceX {input_data['launch_name']}"
        return "SpaceX launch"
    
    def _fetch_news(self, query: str) -> List[Dict[str, Any]]:
        """Fetch news from NewsAPI"""
        response = requests.get(
            f"{self.api_url}/everything",
            params={
                "q": query,
                "sortBy": "publishedAt",
                "pageSize": 5,
                "apiKey": self.api_key
            }
        )
        response.raise_for_status()
        return response.json().get("articles", [])
    
    def _get_mock_news_data(self) -> List[Dict[str, Any]]:
        """Return mock news data"""
        return [
            {
                "title": "SpaceX Prepares for Next Falcon 9 Launch",
                "description": "SpaceX is preparing for its next Falcon 9 mission with careful weather monitoring.",
                "url": "https://example.com/spacex-news-1",
                "publishedAt": datetime.now().isoformat()
            },
            {
                "title": "Weather Conditions Favorable for Upcoming Launch",
                "description": "Meteorologists report favorable conditions for the scheduled launch.",
                "url": "https://example.com/weather-news-1",
                "publishedAt": (datetime.now() - timedelta(hours=2)).isoformat()
            }
        ]

class CryptoAgent(BaseAgent):
    """Agent for fetching cryptocurrency information"""
    
    def __init__(self):
        super().__init__("Crypto")
        self.api_url = "https://api.coingecko.com/api/v3"
    
    async def execute(self, input_data: Dict[str, Any]) -> AgentResult:
        """Fetch cryptocurrency data"""
        try:
            # Fetch Bitcoin and Ethereum prices
            response = requests.get(
                f"{self.api_url}/simple/price",
                params={"ids": "bitcoin,ethereum", "vs_currencies": "usd", "include_24hr_change": "true"}
            )
            response.raise_for_status()
            crypto_data = response.json()
            
            enriched_data = {
                "crypto_prices": crypto_data,
                "previous_data": input_data
            }
            
            result = AgentResult(
                agent_name=self.name,
                success=True,
                data=enriched_data,
                message="Retrieved current cryptocurrency prices",
                next_agent="SummarizeAgent"
            )
            
        except Exception as e:
            result = AgentResult(
                agent_name=self.name,
                success=False,
                data={"previous_data": input_data},
                message=f"Failed to fetch crypto data: {str(e)}"
            )
        
        self.log_execution(input_data, result)
        return result

class SummarizeAgent(BaseAgent):
    """Agent for summarizing and concluding the multi-agent workflow"""
    
    def __init__(self):
        super().__init__("Summarize")
    
    async def execute(self, input_data: Dict[str, Any]) -> AgentResult:
        """Create a comprehensive summary of all agent results"""
        try:
            summary = self._create_summary(input_data)
            
            result = AgentResult(
                agent_name=self.name,
                success=True,
                data={"summary": summary, "all_data": input_data},
                message="Successfully created comprehensive summary"
            )
            
        except Exception as e:
            result = AgentResult(
                agent_name=self.name,
                success=False,
                data={"all_data": input_data},
                message=f"Failed to create summary: {str(e)}"
            )
        
        self.log_execution(input_data, result)
        return result
    
    def _create_summary(self, input_data: Dict[str, Any]) -> str:
        """Create a comprehensive summary from all collected data"""
        summary_parts = []
        
        # SpaceX Launch Information
        if "launch_name" in input_data:
            launch_date = input_data.get("launch_date", "Unknown")
            launch_location = input_data.get("launchpad", {}).get("name", "Unknown")
            summary_parts.append(
                f"🚀 SPACEX LAUNCH INFORMATION:\n"
                f"Mission: {input_data['launch_name']}\n"
                f"Date: {launch_date}\n"
                f"Location: {launch_location}\n"
                f"Details: {input_data.get('details', 'No additional details available')}"
            )
        
        # Weather Analysis
        if "weather" in input_data:
            weather = input_data["weather"]
            suitability = input_data.get("launch_suitability", {})
            summary_parts.append(
                f"\n🌤️ WEATHER ANALYSIS:\n"
                f"Current Conditions: {weather.get('weather', [{}])[0].get('description', 'Unknown')}\n"
                f"Temperature: {weather.get('main', {}).get('temp', 'Unknown')}°C\n"
                f"Wind Speed: {weather.get('wind', {}).get('speed', 'Unknown')} m/s\n"
                f"Launch Suitability: {suitability.get('recommendation', 'Unknown')}\n"
                f"Risk Level: {suitability.get('risk_level', 'Unknown')}"
            )
        
        # News Articles
        if "news_articles" in input_data:
            articles = input_data["news_articles"][:3]  # Top 3 articles
            if articles:
                summary_parts.append("\n📰 RELATED NEWS:")
                for i, article in enumerate(articles, 1):
                    summary_parts.append(f"{i}. {article.get('title', 'No title')}")
        
        # Crypto Information
        if "crypto_prices" in input_data:
            crypto = input_data["crypto_prices"]
            summary_parts.append(
                f"\n💰 CRYPTOCURRENCY PRICES:\n"
                f"Bitcoin: ${crypto.get('bitcoin', {}).get('usd', 'Unknown')}\n"
                f"Ethereum: ${crypto.get('ethereum', {}).get('usd', 'Unknown')}"
            )
        
        # Final Assessment
        if "launch_suitability" in input_data:
            suitability = input_data["launch_suitability"]
            if suitability.get("recommendation") == "UNFAVORABLE":
                summary_parts.append("\n⚠️ CONCLUSION: Launch may face delays due to weather conditions.")
            elif suitability.get("recommendation") == "CAUTION":
                summary_parts.append("\n⚡ CONCLUSION: Launch conditions require monitoring.")
            else:
                summary_parts.append("\n✅ CONCLUSION: Conditions appear favorable for launch.")
        
        return "\n".join(summary_parts) if summary_parts else "No data available for summary."

class MultiAgentSystem:
    """Main orchestrator for the multi-agent system"""
    
    def __init__(self):
        self.agents = {
            "PlannerAgent": PlannerAgent(),
            "SpaceXAgent": SpaceXAgent(),
            "WeatherAgent": WeatherAgent(),
            "NewsAgent": NewsAgent(),
            "CryptoAgent": CryptoAgent(),
            "SummarizeAgent": SummarizeAgent()
        }
        self.logger = logging.getLogger("MultiAgentSystem")
    
    async def execute_goal(self, goal_description: str, max_iterations: int = 10) -> Goal:
        """Execute a user goal through the multi-agent system"""
        self.logger.info(f"Starting execution of goal: {goal_description}")
        
        # Initialize goal
        goal = Goal(description=goal_description, plan=[])
        
        # Start with planner
        current_data = {"goal": goal_description}
        current_agent = "PlannerAgent"
        iteration = 0
        
        while current_agent and iteration < max_iterations:
            iteration += 1
            self.logger.info(f"Iteration {iteration}: Executing {current_agent}")
            
            # Execute current agent
            agent = self.agents.get(current_agent)
            if not agent:
                self.logger.error(f"Agent {current_agent} not found")
                break
            
            result = await agent.execute(current_data)
            goal.results.append(result)
            
            # Check if execution was successful
            if not result.success:
                self.logger.error(f"Agent {current_agent} failed: {result.message}")
                break
            
            # Update current data with result
            current_data.update(result.data)
            
            # Determine next agent
            if current_agent == "PlannerAgent" and "plan" in result.data:
                goal.plan = result.data["plan"]
                current_agent = goal.plan[0] if goal.plan else None
            else:
                # Move to next agent in plan
                if goal.plan and goal.current_step < len(goal.plan) - 1:
                    goal.current_step += 1
                    current_agent = goal.plan[goal.current_step]
                else:
                    current_agent = None  # No more agents to execute
            
            self.logger.info(f"Next agent: {current_agent}")
        
        goal.is_complete = current_agent is None
        self.logger.info(f"Goal execution completed. Success: {goal.is_complete}")
        
        return goal
    
    def evaluate_goal_satisfaction(self, goal: Goal) -> Dict[str, Any]:
        """Evaluate if the goal was satisfied"""
        evaluation = {
            "goal_satisfied": goal.is_complete,
            "total_agents_executed": len(goal.results),
            "successful_agents": sum(1 for r in goal.results if r.success),
            "failed_agents": sum(1 for r in goal.results if not r.success),
            "agent_trajectory": [r.agent_name for r in goal.results],
            "final_result": goal.results[-1] if goal.results else None
        }
        
        # Calculate satisfaction score
        if goal.results:
            success_rate = evaluation["successful_agents"] / evaluation["total_agents_executed"]
            evaluation["satisfaction_score"] = success_rate * 100
        else:
            evaluation["satisfaction_score"] = 0
        
        return evaluation

# Example usage
async def main():
    """Main function demonstrating the multi-agent system"""
    system = MultiAgentSystem()
    
    # Example goals
    goals = [
        "Find the next SpaceX launch, check weather at that location, then summarize if it may be delayed",
        "Get news about SpaceX and summarize the current situation",
        "Check Bitcoin price and get related news"
    ]
    
    for goal_text in goals:
        print(f"\n{'='*60}")
        print(f"EXECUTING GOAL: {goal_text}")
        print(f"{'='*60}")
        
        goal = await system.execute_goal(goal_text)
        evaluation = system.evaluate_goal_satisfaction(goal)
        
        print(f"\nGOAL EVALUATION:")
        print(f"Satisfied: {evaluation['goal_satisfied']}")
        print(f"Satisfaction Score: {evaluation['satisfaction_score']:.1f}%")
        print(f"Agent Trajectory: {' -> '.join(evaluation['agent_trajectory'])}")
        
        if goal.results and goal.results[-1].success:
            final_result = goal.results[-1]
            if "summary" in final_result.data:
                print(f"\nFINAL SUMMARY:")
                print(final_result.data["summary"])

if __name__ == "__main__":
    asyncio.run(main())
