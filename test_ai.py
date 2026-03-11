import json
from proposal_ai import generate_proposal

def test_proposal_logic():
    print("Testing AI Proposal Logic...")
    
    # Test case parameters
    company = "EcoTest Corp"
    industry = "Manufacturing"
    budget = 100000
    goals = "Zero waste and energy efficiency"
    
    result = generate_proposal(company, industry, budget, goals)
    
    if not result['success']:
        print(f"FAILED: AI generation error: {result['error']}")
        return

    data = result['data']
    
    # 1. Check required keys
    required_keys = ['proposal_title', 'product_mix', 'budget_allocation', 'cost_breakdown', 'impact_summary']
    for key in required_keys:
        if key not in data:
            print(f"FAILED: Missing key: {key}")
            return
            
    # 2. Check budget constraint
    total_estimated = data['cost_breakdown']['total_estimated']
    if total_estimated > budget:
        print(f"FAILED: Total estimated cost {total_estimated} exceeds budget {budget}")
    else:
        print(f"PASSED: Total estimated cost {total_estimated} is within budget.")
        
    # 3. Check industry relevance (simple check)
    print(f"Proposal Title: {data['proposal_title']}")
    print(f"Impact Summary: {data['impact_summary'][:100]}...")

if __name__ == "__main__":
    test_proposal_logic()
