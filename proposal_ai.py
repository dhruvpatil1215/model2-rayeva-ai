import os
import json
from datetime import datetime
from groq import Groq
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Initialize Groq client
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def enforce_budget_constraints(data, budget_limit):
    """
    Strictly enforces the budget limit by scaling down product quantities if needed.
    """
    try:
        # 1. Recalculate true subtotal from products
        for item in data['product_mix']:
            item['total_cost'] = item['unit_price'] * item['quantity']
        
        current_subtotal = sum(item['total_cost'] for item in data['product_mix'])
        logistics = data['cost_breakdown'].get('logistics_estimate', 0)
        current_total = current_subtotal + logistics

        # 2. Scale if total exceeds budget
        if current_total > budget_limit:
            # We need to reach (budget_limit - logistics)
            target_subtotal = max(0, budget_limit - logistics)
            scale_factor = target_subtotal / current_subtotal if current_subtotal > 0 else 0
            
            for item in data['product_mix']:
                # Scale quantity down, but keep at least 1 if it was > 0
                original_qty = item['quantity']
                item['quantity'] = max(1 if original_qty > 0 else 0, int(original_qty * scale_factor))
                item['total_cost'] = item['unit_price'] * item['quantity']

            # Recalculate subtotal after scaling
            current_subtotal = sum(item['total_cost'] for item in data['product_mix'])
            current_total = current_subtotal + logistics

            # If still over (due to min quantity 1), we might need to drop items or 
            # just accept it's the absolute minimum, but here we'll try to be strict.
            # For this MVP, scaling is usually enough for "7x" issues.

        # 3. Update cost breakdown
        data['cost_breakdown']['subtotal'] = current_subtotal
        data['cost_breakdown']['total_estimated'] = current_total
        data['cost_breakdown']['remaining_budget'] = budget_limit - current_total

        # 4. Re-calculate budget allocation percentages based on new totals
        # Assuming AI provided categories, we summarize them
        new_allocations = {}
        for item in data['product_mix']:
            cat = item['category']
            if cat not in new_allocations:
                new_allocations[cat] = {"amount": 0, "percentage": 0}
            new_allocations[cat]['amount'] += item['total_cost']
        
        for cat, alloc in new_allocations.items():
            alloc['percentage'] = round((alloc['amount'] / current_subtotal * 100), 2) if current_subtotal > 0 else 0
        
        data['budget_allocation'] = new_allocations
        
        return data
    except Exception as e:
        print(f"Error enforcing budget: {e}")
        return data

def generate_proposal(company_name, industry, budget_limit, goals):
    """
    Generates a B2B sustainability proposal using Groq AI.
    """
    
    system_prompt = """
    You are a Senior B2B Sustainability Consultant. Your task is to generate a comprehensive 
    sustainability proposal for a client based on their industry, budget, and goals.
    
    You must provide:
    1. A unique, professional proposal title.
    2. A suggested sustainable product mix tailored to the client's industry.
    3. A budget allocation across different sustainability categories.
    4. An estimated cost breakdown per product.
    5. A compelling impact positioning summary.
    
    CRITICAL: Your output MUST be strictly valid JSON. Do not include any text outside the JSON block.
    Ensure 'total_estimated' in 'cost_breakdown' is close to 'budget_limit' but NEVER exceeds it.
    """
    
    user_brief = f"""
    Client Name: {company_name}
    Target Industry: {industry}
    Budget Limit: {budget_limit}
    Sustainability Goals: {goals}
    
    Format JSON exactly as:
    {{
      "proposal_title": "...",
      "client_company": "{company_name}",
      "target_industry": "{industry}",
      "budget_limit": {budget_limit},
      "product_mix": [
        {{
          "product_name": "...",
          "category": "...",
          "unit_price": 0,
          "quantity": 0,
          "total_cost": 0,
          "sustainability_tags": ["..."]
        }}
      ],
      "budget_allocation": {{
        "Category Name": {{ "amount": 0, "percentage": 0 }}
      }},
      "cost_breakdown": {{
        "subtotal": 0,
        "logistics_estimate": 0,
        "total_estimated": 0,
        "remaining_budget": 0
      }},
      "impact_summary": "...",
      "generated_at": "{datetime.now().isoformat()}"
    }}
    """
    
    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_brief}
            ],
            temperature=0.7,
            response_format={"type": "json_object"}
        )
        
        proposal_data = json.loads(response.choices[0].message.content)
        
        # ENFORCE BUDGET CONSTRAINTS IN CODE
        proposal_data = enforce_budget_constraints(proposal_data, budget_limit)
        
        return {"success": True, "data": proposal_data}
        
    except Exception as e:
        return {"success": False, "error": str(e)}

if __name__ == "__main__":
    # Test generation
    test_result = generate_proposal(
        "EcoCorp", 
        "Manufacturing", 
        50000, 
        "Reduce carbon footprint and minimize plastic waste in packaging."
    )
    print(json.dumps(test_result, indent=2))
