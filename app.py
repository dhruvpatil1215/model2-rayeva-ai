from flask import Flask, render_template, request, jsonify, send_file
import json
from io import BytesIO
from dotenv import load_dotenv
from proposal_ai import generate_proposal
from database import init_db, save_proposal, get_all_proposals, get_proposal_by_id

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Initialize database
init_db()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    company_name = request.form.get('company_name')
    industry = request.form.get('industry')
    goals = request.form.get('goals')

    try:
        budget_str = request.form.get('budget', '0')
        budget = float(budget_str) if budget_str else 0.0
    except ValueError:
        return render_template('index.html', error="Invalid budget value.")

    # Validate required fields
    if not company_name or not industry or not goals:
        return render_template('index.html', error="Please fill all required fields.")

    try:
        result = generate_proposal(company_name, industry, budget, goals)
    except Exception as e:
        return render_template('index.html', error=f"AI generation failed: {str(e)}")

    if result.get("success"):
        proposal_id = save_proposal(company_name, industry, budget, goals, result["data"])
        return render_template(
            'index.html',
            proposal=result["data"],
            proposal_id=proposal_id
        )
    else:
        return render_template('index.html', error=result.get("error", "Unknown error"))

@app.route('/history')
def history():
    proposals = get_all_proposals()
    return render_template('history.html', proposals=proposals)

@app.route('/proposal/<int:proposal_id>')
def view_proposal(proposal_id):
    proposal = get_proposal_by_id(proposal_id)
    if proposal:
        return render_template(
            'index.html',
            proposal=proposal,
            proposal_id=proposal_id
        )
    return "Proposal not found", 404

@app.route('/download/<int:proposal_id>')
def download_json(proposal_id):
    proposal = get_proposal_by_id(proposal_id)
    if proposal:
        json_data = json.dumps(proposal, indent=2)
        return send_file(
            BytesIO(json_data.encode()),
            mimetype='application/json',
            as_attachment=True,
            download_name=f'proposal_{proposal_id}.json'
        )
    return "Proposal not found", 404

# Optional API endpoint for JSON testing
@app.route('/api/proposal', methods=['POST'])
def api_generate():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Missing JSON body"}), 400

    company = data.get("company_name")
    industry = data.get("industry")
    goals = data.get("goals")

    try:
        budget = float(data.get("budget", 0))
    except ValueError:
        return jsonify({"error": "Invalid budget value"}), 400

    result = generate_proposal(company, industry, budget, goals)
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True, port=5000)