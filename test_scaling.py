import json
from proposal_ai import generate_proposal

def test_scaling():
    print("Testing Budget Scaling...")
    # Give a tiny budget that will definitely be exceeded by the AI's suggestions
    result = generate_proposal("Tiny Corp", "Retail", 1000, "Buy everything expensive")
    
    if result['success']:
        data = result['data']
        total = data['cost_breakdown']['total_estimated']
        print(f"Budget Limit: 1000")
        print(f"Enforced Total: {total}")
        
        if total <= 1000:
            print("SUCCESS: Budget was strictly enforced.")
        else:
            print(f"FAILURE: Budget exceeded! Total: {total}")
            
        # Check quantities
        for item in data['product_mix']:
            print(f"Product: {item['product_name']}, Qty: {item['quantity']}, Total: {item['total_cost']}")
    else:
        print(f"Error: {result['error']}")

if __name__ == "__main__":
    test_scaling()
