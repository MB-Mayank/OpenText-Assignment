# ☁️ AI-Powered Cloud Cost Optimizer

> Live demo hosted on Hugging Face Spaces: https://huggingface.co/spaces/mb2136/cloud-cost-optimizer

Give a plain-English project description, let the tool generate a structured profile and synthetic billing, then get a full cost-optimization report (JSON, text, and a rich HTML dashboard-style report) in one flow.

> Note: The HTML report template was initially scaffolded with help from Claude, and GPT-based tools were used for debugging. The core application logic and flow are self-built based on the given project requirements.

## 🎯 Features

### Mandatory Features (Implemented)
- ✅ **Project Profile Extraction**: Converts plain-English descriptions into structured project profiles
- ✅ **Synthetic Billing Generation**: Creates realistic cloud billing data (12-20 records)
- ✅ **Cost Analysis**: Analyzes costs against budget with detailed breakdowns
- ✅ **Multi-Cloud Recommendations**: 6-10 actionable recommendations covering AWS, Azure, GCP, and open-source alternatives
- ✅ **Menu-Driven CLI**: User-friendly command-line interface

### Bonus Features (Implemented)
- ✅ **Retry Logic**: Automatic retry with stricter instructions on LLM failures
- ✅ **JSON Validation**: Comprehensive validation for all generated data
- ✅ **Multiple Export Formats**: JSON, text summary, detailed reports, and a modern HTML report

## 🏗️ Project Structure

```
cloud-cost-optimizer/
├── cost_optimizer.py          # Main entry point
├── llm_client.py              # Groq LLM integration with retry logic
├── profile_extractor.py       # Project profile extraction
├── billing_generator.py       # Synthetic billing data generation
├── cost_analyzer.py           # Cost analysis and recommendations
├── cli.py                     # Command-line interface (menu + exports)
├── html_report_generator.py   # Styled HTML report generator
├── .env                       # Environment variables (API keys)
├── requirements.txt           # Python dependencies
├── README.md                  # This file
└── outputs/                   # Generated files directory
    ├── project_description.txt
    ├── project_profile.json
    ├── mock_billing.json
    ├── cost_optimization_report.json
    ├── report_summary.txt
    ├── report_detailed.txt
    └── cost_optimization_report.html
```

## 🚀 Quick Start

### Prerequisites
- Python 3.10 or higher
- Groq API key (free at [console.groq.com](https://console.groq.com))

### Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd OpenText-Assignment
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Set up environment variables**

Create a `.env` file in the project root:
```bash
GROQ_API_KEY=your_groq_api_key_here
```

Get your free Groq API key from [console.groq.com](https://console.groq.com)

### Running the Application

```bash
python cost_optimizer.py
```


## 📖 Quick Usage & Flow

### 1. From Profile to Report (End‑to‑End)

1. **Start CLI**: `python cost_optimizer.py`
2. **Enter New Project Description (Option 1)**
  - Describe your app, budget, tech stack, and requirements.
  - Type `END` on a new line to finish.
  - The tool creates and saves `outputs/project_profile.json`.
3. **Run Complete Cost Analysis (Option 2)**
  - Generates realistic billing (`outputs/mock_billing.json`).
  - Calls the LLM for analysis + recommendations.
  - Saves `outputs/cost_optimization_report.json`.
4. **Export Report (Option 4 in main menu)**
  - Choose:
    - `1` JSON (already saved),
    - `2` Text summary,
    - `3` Detailed text report,
    - `4` **HTML Report** → generates `outputs/cost_optimization_report.html`.
5. **Open HTML Report**
  - Open `outputs/cost_optimization_report.html` in your browser for a modern, interactive-style dashboard (executive summary, budget bar, service breakdown, billing table, and all recommendations as cards).

### 2. Flow Chart (Textual)

1. **Input** → Plain‑English description (budget, stack, requirements)
2. **Profile Extractor** → `project_profile.json`
3. **Billing Generator** → synthetic billing `mock_billing.json`
4. **Cost Analyzer** → analysis + recommendations `cost_optimization_report.json`
5. **Export Layer (CLI)** → JSON / text / **HTML report** `cost_optimization_report.html`

### 3. Example CLI Session

```
Step 1: Enter Project Description
-----------------------------------
I want to build an e-commerce market analysis tool. 
The tool should track highest-selling products each month.
Frontend: React
Backend: Node.js
Database: MongoDB
Proxy: Nginx
Hosting: AWS
Budget: ₹3000 per month
END

Step 2: Run Complete Analysis
-----------------------------------
✅ Profile extracted
✅ 15 billing records generated
✅ 7 recommendations created

Step 3: View Recommendations
-----------------------------------
Shows detailed optimization strategies

Step 4: Export Report
-----------------------------------
Save to JSON / text / HTML dashboard
```

## 💡 Sample Input/Output

### Input: Project Description
```text
We are building a food delivery app for 10,000 users per month.
Budget: ₹50,000 per month.
Tech stack: Node.js backend, PostgreSQL database, object storage for images,
monitoring, and basic analytics.
Non-functional requirements: scalability, cost efficiency, uptime monitoring.
```

### Output: Project Profile (project_profile.json)
```json
{
  "name": "Food Delivery App",
  "budget_inr_per_month": 50000,
  "description": "A scalable food delivery platform serving ~10k monthly users.",
  "tech_stack": {
    "backend": "Node.js",
    "database": "PostgreSQL",
    "storage": "Object Storage",
    "monitoring": "Basic uptime & performance"
  },
  "non_functional_requirements": ["Scalability", "Cost efficiency", "Monitoring"]
}
```

### Output: Cost Optimization Report (excerpt)
```json
{
  "analysis": {
    "total_monthly_cost": 39000,
    "budget": 50000,
    "budget_variance": -11000,
    "is_over_budget": false
  },
  "recommendations": [
    {
      "title": "Switch to Reserved Instances",
      "service": "Compute",
      "current_cost": 15000,
      "potential_savings": 4000,
      "cloud_providers": ["AWS", "Azure", "GCP"]
    }
  ]
}
```

## 🔧 Technical Details

### LLM Integration
- **Provider**: Groq
- **Model**: llama-3.3-70b-versatile (default)
- **Features**:
  - JSON-only output mode
  - Automatic retry with stricter instructions
  - Markdown code block removal
  - Comprehensive error handling

### Data Generation
- **Profile Extraction**: LLM-based parsing of natural language
- **Billing Generation**: Realistic cloud service costs with proper distribution
- **Cost Analysis**: Budget-aware recommendations across multiple cloud providers

### Validation
- JSON schema validation for all generated data
- Budget variance calculations
- Service cost breakdowns
- Comprehensive error messages

## 📊 Output Files

### project_profile.json
Structured project information extracted from description

### mock_billing.json
12-20 realistic billing records with:
- Service names (EC2, RDS, S3, etc.)
- Resource IDs and regions
- Usage quantities and units
- Costs in INR

### cost_optimization_report.json
Comprehensive analysis including:
- Total costs and budget variance
- Service-wise cost breakdown
- 6-10 optimization recommendations
- Multi-cloud alternatives
- Implementation steps and effort levels

## 🛠️ Tools Used

- **Python 3.10+**: Core programming language
- **Groq API**: LLM inference for intelligent analysis
- **python-dotenv**: Environment variable management
- **Claude (Anthropic)**: Used for code generation and architecture design

