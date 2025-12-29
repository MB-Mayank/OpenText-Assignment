import json
from typing import Dict, Any, List
from llm_client import LLMClient


class CostAnalyzer:
    def __init__(self, llm_client: LLMClient):
        self.llm = llm_client
        
    def analyze_and_recommend(
        self, 
        profile: Dict[Any, Any], 
        billing: List[Dict[Any, Any]]
    ) -> Dict[Any, Any]:
        total_cost = sum(r["cost_inr"] for r in billing)
        budget = profile["budget_inr_per_month"]
        
        service_costs = {}
        for record in billing:
            service = record["service"]
            service_costs[service] = service_costs.get(service, 0) + record["cost_inr"]
        
        sorted_services = sorted(service_costs.items(), key=lambda x: x[1], reverse=True)
        high_cost_services = dict(sorted_services[:3])
        
        system_prompt = """You are a multi-cloud cost optimization expert. Generate actionable cost optimization recommendations.

CRITICAL: Return ONLY valid JSON, no markdown formatting, no explanations, no code blocks.

Output schema:
{
  "project_name": "Project Name",
  "analysis": {
    "total_monthly_cost": <number>,
    "budget": <number>,
    "budget_variance": <number>,
    "service_costs": {"service": cost},
    "high_cost_services": {"service": cost},
    "is_over_budget": <boolean>
  },
  "recommendations": [
    {
      "title": "Recommendation Title",
      "service": "Service Name",
      "current_cost": <number>,
      "potential_savings": <number>,
      "recommendation_type": "optimization|right_sizing|reserved_instances|free_tier|open_source|alternative_provider",
      "description": "Detailed description",
      "implementation_effort": "low|medium|high",
      "risk_level": "low|medium|high",
      "steps": ["step1", "step2", "step3"],
      "cloud_providers": ["AWS", "Azure", "GCP", "Open Source"]
    }
  ],
  "summary": {
    "total_potential_savings": <number>,
    "savings_percentage": <number>,
    "recommendations_count": <number>,
    "high_impact_recommendations": <number>
  }
}

Rules:
1. Generate 6-10 diverse recommendations covering multiple services
2. Include multi-cloud alternatives (AWS, Azure, GCP)
3. Consider open-source/free-tier options
4. Recommendations must be specific and actionable
5. Calculate realistic potential savings (10-50% per recommendation)
6. Include implementation steps
7. High impact = savings > 500 INR or savings > 20% of service cost
8. Return pure JSON only"""

        user_prompt = f"""Analyze costs and generate recommendations:

PROJECT:
Name: {profile['name']}
Budget: ₹{budget} per month
Tech Stack: {json.dumps(profile['tech_stack'], indent=2)}

CURRENT COSTS:
Total: ₹{total_cost}
Variance: ₹{total_cost - budget}
Over Budget: {total_cost > budget}

Service Breakdown:
{json.dumps(service_costs, indent=2)}

High Cost Services:
{json.dumps(high_cost_services, indent=2)}

Generate 6-10 optimization recommendations with multi-cloud alternatives."""

        print("Analyzing costs and generating recommendations...")
        report = self.llm.generate_json(system_prompt, user_prompt, temperature=0.8)
        print(f"Generated {len(report.get('recommendations', []))} recommendations")
        
        return report
    
    def save_report(self, report: Dict[Any, Any], output_path: str = "outputs/cost_optimization_report.json"):
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        print(f"Report saved to {output_path}")
    
    def load_report(self, input_path: str = "outputs/cost_optimization_report.json") -> Dict[Any, Any]:
        with open(input_path, 'r', encoding='utf-8') as f:
            report = json.load(f)
        return report
    
    def validate_report(self, report: Dict[Any, Any]) -> bool:
        required_sections = ["project_name", "analysis", "recommendations", "summary"]
        
        for section in required_sections:
            if section not in report:
                raise ValueError(f"Missing required section: {section}")
        
        if not isinstance(report["recommendations"], list):
            raise ValueError("recommendations must be an array")
        
        if len(report["recommendations"]) < 6:
            print(f"Warning: Expected 6-10 recommendations, got {len(report['recommendations'])}")
        
        print("Report validation passed")
        return True
    
    def print_summary(self, report: Dict[Any, Any]):
        print("\n" + "="*60)
        print(f"COST OPTIMIZATION REPORT: {report['project_name']}")
        print("="*60)
        
        analysis = report["analysis"]
        print(f"\nCOST ANALYSIS:")
        print(f"   Total Monthly Cost: ₹{analysis['total_monthly_cost']:,.2f}")
        print(f"   Budget: ₹{analysis['budget']:,.2f}")
        print(f"   Variance: ₹{analysis['budget_variance']:,.2f}")
        print(f"   Status: {'OVER BUDGET' if analysis['is_over_budget'] else 'WITHIN BUDGET'}")
        
        print(f"\nTOP SERVICES BY COST:")
        for service, cost in list(analysis['high_cost_services'].items())[:5]:
            print(f"   • {service}: ₹{cost:,.2f}")
        
        summary = report["summary"]
        print(f"\nRECOMMENDATIONS SUMMARY:")
        print(f"   Total Recommendations: {summary['recommendations_count']}")
        print(f"   High Impact: {summary.get('high_impact_recommendations', 0)}")
        print(f"   Potential Savings: ₹{summary['total_potential_savings']:,.2f}")
        print(f"   Savings Percentage: {summary['savings_percentage']:.1f}%")
        
        print("\n" + "="*60 + "\n")
    
    def print_recommendations(self, report: Dict[Any, Any], detailed: bool = False):
        print("\n" + "="*60)
        print("COST OPTIMIZATION RECOMMENDATIONS")
        print("="*60 + "\n")
        
        for i, rec in enumerate(report["recommendations"], 1):
            print(f"{i}. {rec['title']}")
            print(f"   Service: {rec['service']}")
            print(f"   Current Cost: ₹{rec['current_cost']:,.2f}")
            print(f"   Potential Savings: ₹{rec['potential_savings']:,.2f}")
            print(f"   Type: {rec['recommendation_type']}")
            print(f"   Effort: {rec['implementation_effort']} | Risk: {rec['risk_level']}")
            print(f"   Cloud Providers: {', '.join(rec['cloud_providers'])}")
            
            if detailed:
                print(f"\n   Description: {rec['description']}")
                print(f"\n   Implementation Steps:")
                for step_num, step in enumerate(rec['steps'], 1):
                    print(f"      {step_num}. {step}")
            
            print()
        
        print("="*60 + "\n")