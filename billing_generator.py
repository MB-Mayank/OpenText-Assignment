import json
from typing import Dict, Any, List
from llm_client import LLMClient


class BillingGenerator:
    def __init__(self, llm_client: LLMClient):
        self.llm = llm_client
        
    def generate_billing(self, profile: Dict[Any, Any]) -> List[Dict[Any, Any]]:
        system_prompt = """You are a cloud cost analyst. Generate realistic synthetic billing data for cloud projects . Budget given is just for comparison if budget is very low generate realistic over budget billing. You dont always need to be close to budget be realistic.
CRITICAL: Return ONLY valid JSON array, no markdown formatting, no explanations, no code blocks.
CRITICAL UNIQUENESS RULES (MUST FOLLOW):
1. Each billing record MUST be unique .
2. NO two records may share the same descroption or service.
3. Before returning the final output, internally verify that NO duplicates exist.
Generate 12-20 billing records covering(DOnot repeat all uniques should be there ):
- Compute (EC2, VMs, App Services)
- Database (RDS, MongoDB, PostgreSQL)
- Storage (S3, Blob Storage, Cloud Storage)
- Networking (Load Balancers, CDN, Data Transfer)
- Monitoring (CloudWatch, Azure Monitor, Stackdriver)
- Other services based on tech stack
Record schema:
{
  "month": "2025-01",
  "service": "Service Name",
  "resource_id": "resource-identifier",
  "region": "cloud-region",
  "usage_type": "usage category",
  "usage_quantity": <number>,
  "unit": "hours/GB/requests",
  "cost_inr": <number>,
  "desc": "Resource description"
}
Rules:
Rules:
1. Prioritize realistic cloud costs based on the project’s tech stack and expected usage.
2. Do NOT artificially reduce costs just to fit within the given budget.
3. If the budget is realistic, generate costs that are reasonably realistic .
4. If the budget is unrealistically low, generate minimum feasible cloud costs and allow
   the total cost to exceed the budget.
5. Distribute costs realistically across compute, database, storage, networking, and monitoring.
6. Ensure high-usage or critical services (e.g., compute, database) contribute the largest share.
7. Use realistic regions and identifiers (e.g., ap-south-1, valid resource IDs).
8. Include multiple usage types such as on-demand, reserved, and spot where applicable.
9. Ensure costs follow real-world cloud pricing patterns and trade-offs.
10. Return ONLY a valid JSON array with no extra text.
"""

        user_prompt = f"""Generate billing records for this project:
Name: {profile['name']}
Budget: ₹{profile['budget_inr_per_month']} per month
Tech Stack: {json.dumps(profile['tech_stack'], indent=2)}
Requirements: {', '.join(profile['non_functional_requirements'])}
Generate 12-20 realistic billing records."""

        print("Generating synthetic billing data...")
        billing_records = self.llm.generate_json(system_prompt, user_prompt)
        if isinstance(billing_records, dict) and "records" in billing_records:
            billing_records = billing_records["records"]
        elif isinstance(billing_records, dict) and "billing" in billing_records:
            billing_records = billing_records["billing"]
        
        if not isinstance(billing_records, list):
            raise ValueError("LLM did not return a list of billing records")
        
        print(f"Generated {len(billing_records)} billing records")
        
        return billing_records
    
    def save_billing(self, records: List[Dict[Any, Any]], output_path: str = "outputs/mock_billing.json"):
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(records, f, indent=2, ensure_ascii=False)
        print(f"Billing data saved to {output_path}")
    
    def load_billing(self, input_path: str = "outputs/mock_billing.json") -> List[Dict[Any, Any]]:
        with open(input_path, 'r', encoding='utf-8') as f:
            records = json.load(f)
        return records
    
    def validate_billing(self, records: List[Dict[Any, Any]]) -> bool:
        if not isinstance(records, list):
            raise ValueError("Billing data must be a list")
        
        if len(records) < 12 or len(records) > 20:
            print(f"Warning: Expected 12-20 records, got {len(records)}")
        
        required_fields = ["month", "service", "cost_inr"]
        
        for i, record in enumerate(records):
            for field in required_fields:
                if field not in record:
                    raise ValueError(f"Record {i} missing required field: {field}")
            
            if not isinstance(record["cost_inr"], (int, float)):
                raise ValueError(f"Record {i}: cost_inr must be a number")
        
        total_cost = sum(r["cost_inr"] for r in records)
        print(f"Billing validation passed - Total cost: ₹{total_cost:,.2f}")
        
        return True
    
    def get_billing_summary(self, records: List[Dict[Any, Any]]) -> Dict[str, Any]:
        total_cost = sum(r["cost_inr"] for r in records)
        
        service_costs = {}
        for record in records:
            service = record["service"]
            service_costs[service] = service_costs.get(service, 0) + record["cost_inr"]
        
        return {
            "total_cost": total_cost,
            "record_count": len(records),
            "service_costs": service_costs,
            "unique_services": len(service_costs)
        }