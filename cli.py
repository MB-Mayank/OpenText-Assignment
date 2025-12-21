"""
CLI Interface - Modern Interactive Version
Menu-driven command-line interface with enhanced visuals and JSON display
"""

import os
import sys
import json
import time
import webbrowser
from typing import Optional, Dict, Any
from llm_client import LLMClient
from profile_extractor import ProfileExtractor
from billing_generator import BillingGenerator
from cost_analyzer import CostAnalyzer
from html_report_generator import HTMLReportGenerator
from dotenv import load_dotenv
load_dotenv()


class Colors:
    """ANSI color codes for terminal output"""
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    
    # Additional colors
    PURPLE = '\033[35m'
    YELLOW = '\033[33m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    GREY = '\033[90m'


class CostOptimizerCLI:
    """Modern interactive CLI for Cloud Cost Optimizer"""
    
    def __init__(self):
        """Initialize CLI with all components"""
        self.outputs_dir = "outputs"
        self.ensure_outputs_directory()
        
        # Initialize components
        try:
            print(f"{Colors.CYAN}🔄 Initializing components...{Colors.ENDC}")
            self.llm = LLMClient()
            self.profile_extractor = ProfileExtractor(self.llm)
            self.billing_generator = BillingGenerator(self.llm)
            self.cost_analyzer = CostAnalyzer(self.llm)
            print(f"{Colors.OKGREEN}✅ All components initialized successfully{Colors.ENDC}\n")
        except ValueError as e:
            print(f"{Colors.FAIL}❌ Error: {e}{Colors.ENDC}")
            print(f"{Colors.WARNING}Please set GROQ_API_KEY in your .env file{Colors.ENDC}")
            sys.exit(1)
        
        self.current_profile = None
        self.current_billing = None
        self.current_report = None
    
    def ensure_outputs_directory(self):
        """Create outputs directory if it doesn't exist"""
        if not os.path.exists(self.outputs_dir):
            os.makedirs(self.outputs_dir)
    
    def clear_screen(self):
        """Clear the console screen"""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def print_box(self, text: str, color: str = Colors.OKBLUE, width: int = 70):
        """Print text in a colored box"""
        print(f"{color}{'═' * width}")
        padding = (width - len(text) - 2) // 2
        print(f"║{' ' * padding}{text}{' ' * (width - len(text) - padding - 2)}║")
        print(f"{'═' * width}{Colors.ENDC}")
    
    def print_section_header(self, text: str, emoji: str = "📋"):
        """Print a section header with styling"""
        print(f"\n{Colors.BOLD}{Colors.OKCYAN}{emoji} {text.upper()}{Colors.ENDC}")
        print(f"{Colors.GREY}{'─' * 70}{Colors.ENDC}")
    
    def print_json_preview(self, data: Any, title: str = "JSON Data", color: str = Colors.OKCYAN):
        """Print formatted JSON with syntax highlighting"""
        print(f"\n{color}{Colors.BOLD}📄 {title}:{Colors.ENDC}")
        print(f"{Colors.GREY}┌{'─' * 68}┐{Colors.ENDC}")
        
        json_str = json.dumps(data, indent=2, ensure_ascii=False)
        lines = json_str.split('\n')
        
        # Limit to first 25 lines for preview
        preview_lines = lines[:25]
        for line in preview_lines:
            # Color different JSON elements
            if '"' in line and ':' in line:
                # Keys in cyan, values in white
                parts = line.split(':', 1)
                if len(parts) == 2:
                    key_part = parts[0]
                    value_part = parts[1]
                    print(f"{Colors.GREY}│{Colors.ENDC} {Colors.CYAN}{key_part}{Colors.ENDC}:{Colors.WHITE}{value_part}{Colors.ENDC}")
                else:
                    print(f"{Colors.GREY}│{Colors.ENDC} {Colors.WHITE}{line}{Colors.ENDC}")
            else:
                print(f"{Colors.GREY}│{Colors.ENDC} {Colors.WHITE}{line}{Colors.ENDC}")
        
        if len(lines) > 25:
            print(f"{Colors.GREY}│{Colors.ENDC} {Colors.YELLOW}... ({len(lines) - 25} more lines){Colors.ENDC}")
        
        print(f"{Colors.GREY}└{'─' * 68}┘{Colors.ENDC}")
    
    def print_header(self):
        """Print application header"""
        self.clear_screen()
        print(f"\n{Colors.BOLD}{Colors.HEADER}")
        print("╔════════════════════════════════════════════════════════════════════╗")
        print("║                                                                    ║")
        print("║              ☁️  AI-POWERED CLOUD COST OPTIMIZER  ☁️               ║")
        print("║                                                                    ║")
        print("║                   🤖 LLM-Driven Multi-Cloud Analysis               ║")
        print("║                                                                    ║")
        print("╚════════════════════════════════════════════════════════════════════╝")
        print(f"{Colors.ENDC}")
        
        if self.current_profile:
            print(f"{Colors.OKGREEN}📊 Active Project: {Colors.BOLD}{self.current_profile['name']}{Colors.ENDC}")
            print(f"{Colors.OKGREEN}💰 Budget: ₹{self.current_profile['budget_inr_per_month']:,.2f}/month{Colors.ENDC}\n")
    
    def print_menu(self):
        """Print modern interactive menu"""
        print(f"{Colors.BOLD}{Colors.OKBLUE}╔════════════════════ MAIN MENU ═══════════════════════╗{Colors.ENDC}")
        
        options = [
            ("1", "📝", "Enter New Project Description", Colors.OKCYAN),
            ("2", "🚀", "Run Complete Cost Analysis", Colors.OKGREEN),
            ("3", "💡", "View Recommendations", Colors.YELLOW),
            ("4", "📊", "Export Report", Colors.PURPLE),
            ("5", "📂", "Load Existing Project", Colors.OKBLUE),
            ("6", "🔍", "View Current Data", Colors.CYAN),
            ("7", "❌", "Exit", Colors.FAIL)
        ]
        
        for num, emoji, text, color in options:
            print(f"{Colors.OKBLUE}║{Colors.ENDC} {color}{num}.{Colors.ENDC} {emoji}  {Colors.BOLD}{text:<47}{Colors.OKBLUE}║{Colors.ENDC}")
        
        print(f"{Colors.BOLD}{Colors.OKBLUE}╚══════════════════════════════════════════════════════╝{Colors.ENDC}\n")
    
    def animate_loading(self, message: str, duration: float = 1.5):
        """Show animated loading message"""
        frames = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
        end_time = time.time() + duration
        i = 0
        while time.time() < end_time:
            print(f"\r{Colors.CYAN}{frames[i % len(frames)]} {message}...{Colors.ENDC}", end='', flush=True)
            time.sleep(0.1)
            i += 1
        print(f"\r{Colors.OKGREEN}✓ {message}... Done!{Colors.ENDC}")
    
    def enter_project_description(self):
        """Handle project description input with modern UI"""
        self.print_section_header("PROJECT DESCRIPTION INPUT", "📝")
        
        print(f"\n{Colors.YELLOW}💬 Describe your cloud project in plain English{Colors.ENDC}")
        print(f"{Colors.GREY}   Include: budget, tech stack, requirements, and goals{Colors.ENDC}")
        print(f"{Colors.GREY}   Type '{Colors.BOLD}END{Colors.GREY}' on a new line when finished{Colors.ENDC}\n")
        
        print(f"{Colors.CYAN}Example:{Colors.ENDC}")
        print(f"{Colors.GREY}  I want to build an e-commerce app with React frontend,")
        print(f"  Node.js backend, MongoDB database. Budget is ₹5000/month.{Colors.ENDC}\n")
        
        print(f"{Colors.BOLD}{Colors.OKGREEN}Your Description:{Colors.ENDC}")
        print(f"{Colors.GREY}{'─' * 70}{Colors.ENDC}")
        
        lines = []
        line_num = 1
        while True:
            line = input(f"{Colors.GREY}{line_num:2d} │{Colors.ENDC} ")
            if line.strip().upper() == 'END':
                break
            lines.append(line)
            line_num += 1
        
        description = '\n'.join(lines).strip()
        
        if not description:
            print(f"\n{Colors.FAIL}❌ Description cannot be empty{Colors.ENDC}")
            return
        
        print(f"\n{Colors.GREY}{'─' * 70}{Colors.ENDC}")
        
        # Save description
        desc_path = os.path.join(self.outputs_dir, "project_description.txt")
        with open(desc_path, 'w', encoding='utf-8') as f:
            f.write(description)
        print(f"{Colors.OKGREEN}💾 Saved to: {desc_path}{Colors.ENDC}")
        
        # Show input being sent to LLM
        self.print_section_header("LLM INPUT - PROJECT DESCRIPTION", "🔄")
        self.print_json_preview({"description": description}, "Input to Profile Extractor", Colors.PURPLE)
        
        # Extract profile
        try:
            print(f"\n{Colors.CYAN}🤖 Sending to LLM for extraction...{Colors.ENDC}")
            time.sleep(0.5)
            
            self.current_profile = self.profile_extractor.extract_profile(description)
            
            # Show LLM output
            self.print_section_header("LLM OUTPUT - EXTRACTED PROFILE", "✨")
            self.print_json_preview(self.current_profile, "Generated Project Profile", Colors.OKGREEN)
            
            self.profile_extractor.validate_profile(self.current_profile)
            self.profile_extractor.save_profile(self.current_profile)
            
            # Success summary
            print(f"\n{Colors.BOLD}{Colors.OKGREEN}✅ PROJECT PROFILE CREATED SUCCESSFULLY!{Colors.ENDC}")
            print(f"{Colors.OKGREEN}┌{'─' * 50}┐{Colors.ENDC}")
            print(f"{Colors.OKGREEN}│{Colors.ENDC} {Colors.BOLD}Name:{Colors.ENDC} {self.current_profile['name']:<42}{Colors.OKGREEN}│{Colors.ENDC}")
            print(f"{Colors.OKGREEN}│{Colors.ENDC} {Colors.BOLD}Budget:{Colors.ENDC} ₹{self.current_profile['budget_inr_per_month']:,.2f}/month{' ' * 25}{Colors.OKGREEN}│{Colors.ENDC}")
            print(f"{Colors.OKGREEN}│{Colors.ENDC} {Colors.BOLD}Tech Stack:{Colors.ENDC} {len([k for k, v in self.current_profile.get('tech_stack', {}).items() if v])} technologies identified{' ' * 14}{Colors.OKGREEN}│{Colors.ENDC}")
            print(f"{Colors.OKGREEN}└{'─' * 50}┘{Colors.ENDC}")
            
        except Exception as e:
            print(f"\n{Colors.FAIL}❌ Error creating profile: {e}{Colors.ENDC}")
            self.current_profile = None
    
    def run_complete_analysis(self):
        """Run the full cost analysis pipeline with detailed output"""
        if not self.current_profile:
            print(f"\n{Colors.FAIL}❌ No project profile found{Colors.ENDC}")
            print(f"{Colors.WARNING}💡 Please enter a project description first (Option 1){Colors.ENDC}")
            return
        
        self.print_section_header("COMPLETE COST ANALYSIS PIPELINE", "🚀")
        
        try:
            # STEP 1: Generate Billing
            print(f"\n{Colors.BOLD}{Colors.OKCYAN}STEP 1/3: SYNTHETIC BILLING GENERATION{Colors.ENDC}")
            print(f"{Colors.GREY}{'═' * 70}{Colors.ENDC}")
            
            # Show input
            billing_input = {
                "project_name": self.current_profile['name'],
                "budget_inr_per_month": self.current_profile['budget_inr_per_month'],
                "tech_stack": self.current_profile['tech_stack']
            }
            self.print_json_preview(billing_input, "Input to Billing Generator", Colors.PURPLE)
            
            print(f"\n{Colors.CYAN}🤖 Generating realistic cloud billing data...{Colors.ENDC}")
            self.current_billing = self.billing_generator.generate_billing(self.current_profile)
            
            # Show output
            self.print_json_preview(self.current_billing[:5], f"Generated Billing Records (showing 5 of {len(self.current_billing)})", Colors.OKGREEN)
            
            self.billing_generator.validate_billing(self.current_billing)
            self.billing_generator.save_billing(self.current_billing)
            
            summary = self.billing_generator.get_billing_summary(self.current_billing)
            
            print(f"\n{Colors.OKGREEN}✅ Billing Generation Complete{Colors.ENDC}")
            print(f"{Colors.OKGREEN}│{Colors.ENDC} Records: {summary['record_count']}")
            print(f"{Colors.OKGREEN}│{Colors.ENDC} Total Cost: ₹{summary['total_cost']:,.2f}")
            print(f"{Colors.OKGREEN}│{Colors.ENDC} Services: {summary['unique_services']}")
            
            # STEP 2: Cost Analysis
            print(f"\n{Colors.BOLD}{Colors.OKCYAN}STEP 2/3: COST ANALYSIS{Colors.ENDC}")
            print(f"{Colors.GREY}{'═' * 70}{Colors.ENDC}")
            
            budget = self.current_profile['budget_inr_per_month']
            variance = summary['total_cost'] - budget
            
            analysis_input = {
                "budget": budget,
                "total_cost": summary['total_cost'],
                "variance": variance,
                "is_over_budget": variance > 0
            }
            self.print_json_preview(analysis_input, "Cost Analysis Metrics", Colors.PURPLE)
            
            if variance > 0:
                print(f"\n{Colors.WARNING}⚠️  OVER BUDGET by ₹{variance:,.2f} ({(variance/budget)*100:.1f}%){Colors.ENDC}")
            else:
                print(f"\n{Colors.OKGREEN}✅ UNDER BUDGET by ₹{abs(variance):,.2f} ({(abs(variance)/budget)*100:.1f}%){Colors.ENDC}")
            
            # STEP 3: Generate Recommendations
            print(f"\n{Colors.BOLD}{Colors.OKCYAN}STEP 3/3: OPTIMIZATION RECOMMENDATIONS{Colors.ENDC}")
            print(f"{Colors.GREY}{'═' * 70}{Colors.ENDC}")
            
            print(f"\n{Colors.CYAN}🤖 Analyzing costs and generating multi-cloud recommendations...{Colors.ENDC}")
            self.current_report = self.cost_analyzer.analyze_and_recommend(
                self.current_profile, 
                self.current_billing
            )
            
            # Show output
            self.print_json_preview(self.current_report, "Complete Cost Optimization Report", Colors.OKGREEN)
            
            self.cost_analyzer.validate_report(self.current_report)
            self.cost_analyzer.save_report(self.current_report)
            
            # Display interactive summary
            self.display_analysis_summary(self.current_report)
            
            print(f"\n{Colors.BOLD}{Colors.OKGREEN}🎉 ANALYSIS COMPLETE!{Colors.ENDC}")
            print(f"{Colors.OKGREEN}All reports saved to '{self.outputs_dir}/' directory{Colors.ENDC}")
            
        except Exception as e:
            print(f"\n{Colors.FAIL}❌ Error during analysis: {e}{Colors.ENDC}")
            import traceback
            traceback.print_exc()
    
    def display_analysis_summary(self, report: Dict[Any, Any]):
        """Display interactive analysis summary"""
        self.print_section_header("ANALYSIS SUMMARY", "📊")
        
        analysis = report["analysis"]
        
        # Cost Overview Box
        print(f"\n{Colors.BOLD}{Colors.OKBLUE}╔════════════════ COST OVERVIEW ════════════════╗{Colors.ENDC}")
        print(f"{Colors.OKBLUE}║{Colors.ENDC} {Colors.BOLD}Project:{Colors.ENDC} {report['project_name']:<38} {Colors.OKBLUE}║{Colors.ENDC}")
        print(f"{Colors.OKBLUE}║{Colors.ENDC} {Colors.BOLD}Budget:{Colors.ENDC} ₹{analysis['budget']:>12,.2f}                 {Colors.OKBLUE}║{Colors.ENDC}")
        print(f"{Colors.OKBLUE}║{Colors.ENDC} {Colors.BOLD}Actual:{Colors.ENDC} ₹{analysis['total_monthly_cost']:>12,.2f}                 {Colors.OKBLUE}║{Colors.ENDC}")
        
        variance_color = Colors.FAIL if analysis['is_over_budget'] else Colors.OKGREEN
        variance_symbol = "+" if analysis['is_over_budget'] else ""
        print(f"{Colors.OKBLUE}║{Colors.ENDC} {Colors.BOLD}Variance:{Colors.ENDC} {variance_color}₹{variance_symbol}{analysis['budget_variance']:>11,.2f}{Colors.ENDC}                 {Colors.OKBLUE}║{Colors.ENDC}")
        print(f"{Colors.OKBLUE}╚═══════════════════════════════════════════════╝{Colors.ENDC}")
        
        # Top Services
        print(f"\n{Colors.BOLD}{Colors.YELLOW}📈 TOP COST SERVICES:{Colors.ENDC}")
        sorted_services = sorted(analysis['service_costs'].items(), key=lambda x: x[1], reverse=True)[:5]
        
        max_cost = max([cost for _, cost in sorted_services]) if sorted_services else 1
        
        for service, cost in sorted_services:
            percentage = (cost / analysis['total_monthly_cost']) * 100
            bar_length = int((cost / max_cost) * 40)
            bar = "█" * bar_length
            print(f"{Colors.CYAN}  {service:<20}{Colors.ENDC} {Colors.OKGREEN}{bar}{Colors.ENDC} ₹{cost:>8,.2f} ({percentage:>5.1f}%)")
        
        # Savings Potential
        summary = report["summary"]
        total_savings_str = f"{summary['total_potential_savings']:,.2f}"
        savings_percentage_str = f"{summary['savings_percentage']:.1f}%"
        recommendations_str = str(summary['recommendations_count'])

        total_savings_padding = ' ' * (24 - len(total_savings_str))
        savings_percentage_padding = ' ' * (29 - len(savings_percentage_str))
        recommendations_padding = ' ' * (33 - len(recommendations_str))

        print(f"\n{Colors.BOLD}{Colors.OKGREEN}💰 SAVINGS POTENTIAL:{Colors.ENDC}")
        print(f"{Colors.OKGREEN}┌{'─' * 50}┐{Colors.ENDC}")
        print(f"{Colors.OKGREEN}│{Colors.ENDC} Total Potential Savings: {Colors.BOLD}₹{total_savings_str}{Colors.ENDC}{total_savings_padding}{Colors.OKGREEN}│{Colors.ENDC}")
        print(f"{Colors.OKGREEN}│{Colors.ENDC} Savings Percentage: {Colors.BOLD}{savings_percentage_str}{Colors.ENDC}{savings_percentage_padding}{Colors.OKGREEN}│{Colors.ENDC}")
        print(f"{Colors.OKGREEN}│{Colors.ENDC} Recommendations: {Colors.BOLD}{recommendations_str}{Colors.ENDC}{recommendations_padding}{Colors.OKGREEN}│{Colors.ENDC}")
        print(f"{Colors.OKGREEN}└{'─' * 50}┘{Colors.ENDC}")
    
    def view_recommendations(self):
        """Open recommendations as an HTML report in the browser"""
        if not self.current_report:
            report_path = os.path.join(self.outputs_dir, "cost_optimization_report.json")
            if os.path.exists(report_path):
                try:
                    self.current_report = self.cost_analyzer.load_report(report_path)
                except Exception as e:
                    print(f"\n{Colors.FAIL}❌ Error loading report: {e}{Colors.ENDC}")
                    return
            else:
                print(f"\n{Colors.FAIL}❌ No report found{Colors.ENDC}")
                print(f"{Colors.WARNING}💡 Please run complete analysis first (Option 2){Colors.ENDC}")
                return

        # Ensure profile and billing are available for HTML report
        if not self.current_profile:
            profile_path = os.path.join(self.outputs_dir, "project_profile.json")
            if os.path.exists(profile_path):
                try:
                    self.current_profile = self.profile_extractor.load_profile(profile_path)
                except Exception as e:
                    print(f"\n{Colors.FAIL}❌ Error loading profile for HTML view: {e}{Colors.ENDC}")
                    return
            else:
                print(f"\n{Colors.FAIL}❌ No project profile found for HTML view{Colors.ENDC}")
                print(f"{Colors.WARNING}💡 Please run complete analysis first (Option 2){Colors.ENDC}")
                return

        if not self.current_billing:
            billing_path = os.path.join(self.outputs_dir, "mock_billing.json")
            if os.path.exists(billing_path):
                try:
                    self.current_billing = self.billing_generator.load_billing(billing_path)
                except Exception as e:
                    print(f"\n{Colors.FAIL}❌ Error loading billing data for HTML view: {e}{Colors.ENDC}")
                    return
            else:
                print(f"\n{Colors.FAIL}❌ No billing data found for HTML view{Colors.ENDC}")
                print(f"{Colors.WARNING}💡 Please run complete analysis first (Option 2){Colors.ENDC}")
                return

        self.print_section_header("OPTIMIZATION RECOMMENDATIONS (HTML)", "💡")

        html_path = os.path.join(self.outputs_dir, "cost_optimization_report.html")
        try:
            HTMLReportGenerator.generate_html_report(
                self.current_profile,
                self.current_billing,
                self.current_report,
                html_path,
            )
            abs_path = os.path.abspath(html_path)
            print(f"\n{Colors.OKGREEN}✅ HTML recommendations report generated at:{Colors.ENDC} {abs_path}")
            print(f"{Colors.CYAN}🌐 Opening in your default browser...{Colors.ENDC}")
            webbrowser.open(f"file://{abs_path}")
        except Exception as e:
            print(f"\n{Colors.FAIL}❌ Error generating or opening HTML report: {e}{Colors.ENDC}")
    
    def view_current_data(self):
        """View all current loaded data"""
        self.print_section_header("CURRENT DATA VIEWER", "🔍")
        
        has_data = False
        
        if self.current_profile:
            print(f"\n{Colors.BOLD}{Colors.OKGREEN}✅ PROJECT PROFILE{Colors.ENDC}")
            self.print_json_preview(self.current_profile, "Project Profile", Colors.OKGREEN)
            has_data = True
        
        if self.current_billing:
            print(f"\n{Colors.BOLD}{Colors.OKGREEN}✅ BILLING RECORDS{Colors.ENDC}")
            summary = self.billing_generator.get_billing_summary(self.current_billing)
            print(f"\n{Colors.CYAN}Summary:{Colors.ENDC}")
            print(f"  • Total Records: {summary['record_count']}")
            print(f"  • Total Cost: ₹{summary['total_cost']:,.2f}")
            print(f"  • Unique Services: {summary['unique_services']}")
            
            self.print_json_preview(self.current_billing[:3], f"Billing Records (showing 3 of {len(self.current_billing)})", Colors.OKGREEN)
            has_data = True
        
        if self.current_report:
            print(f"\n{Colors.BOLD}{Colors.OKGREEN}✅ COST OPTIMIZATION REPORT{Colors.ENDC}")
            report_summary = {
                "project_name": self.current_report['project_name'],
                "total_cost": self.current_report['analysis']['total_monthly_cost'],
                "budget": self.current_report['analysis']['budget'],
                "recommendations": self.current_report['summary']['recommendations_count'],
                "potential_savings": self.current_report['summary']['total_potential_savings']
            }
            self.print_json_preview(report_summary, "Report Summary", Colors.OKGREEN)
            has_data = True
        
        if not has_data:
            print(f"\n{Colors.WARNING}⚠️  No data loaded yet{Colors.ENDC}")
            print(f"{Colors.GREY}Start by entering a project description (Option 1){Colors.ENDC}")
    
    def export_report(self):
        """Export report to various formats"""
        if not self.current_report:
            print(f"\n{Colors.FAIL}❌ No report found{Colors.ENDC}")
            print(f"{Colors.WARNING}💡 Please run complete analysis first (Option 2){Colors.ENDC}")
            return
        
        self.print_section_header("EXPORT REPORT", "📊")
        
        print(f"\n{Colors.BOLD}Export Options:{Colors.ENDC}")
        print(f"{Colors.OKBLUE}┌{'─' * 50}┐{Colors.ENDC}")
        print(f"{Colors.OKBLUE}│{Colors.ENDC}  1. {Colors.CYAN}JSON{Colors.ENDC} (already saved)                      {Colors.OKBLUE}│{Colors.ENDC}")
        print(f"{Colors.OKBLUE}│{Colors.ENDC}  2. {Colors.YELLOW}Text Summary{Colors.ENDC}                            {Colors.OKBLUE}│{Colors.ENDC}")
        print(f"{Colors.OKBLUE}│{Colors.ENDC}  3. {Colors.OKGREEN}Detailed Text Report{Colors.ENDC}                    {Colors.OKBLUE}│{Colors.ENDC}")
        print(f"{Colors.OKBLUE}│{Colors.ENDC}  4. {Colors.PURPLE}HTML Report{Colors.ENDC}                              {Colors.OKBLUE}│{Colors.ENDC}")
        print(f"{Colors.OKBLUE}│{Colors.ENDC}  5. {Colors.GREY}Back to Main Menu{Colors.ENDC}                       {Colors.OKBLUE}│{Colors.ENDC}")
        print(f"{Colors.OKBLUE}└{'─' * 50}┘{Colors.ENDC}\n")
        
        choice = input(f"{Colors.BOLD}Select option (1-5): {Colors.ENDC}").strip()
        
        if choice == '1':
            print(f"\n{Colors.OKGREEN}✅ Report already saved to:{Colors.ENDC}")
            print(f"   {self.outputs_dir}/cost_optimization_report.json")
        
        elif choice == '2':
            output_path = os.path.join(self.outputs_dir, "report_summary.txt")
            with open(output_path, 'w', encoding='utf-8') as f:
                import sys
                old_stdout = sys.stdout
                sys.stdout = f
                self.cost_analyzer.print_summary(self.current_report)
                sys.stdout = old_stdout
            print(f"\n{Colors.OKGREEN}✅ Summary exported to: {output_path}{Colors.ENDC}")
        
        elif choice == '3':
            output_path = os.path.join(self.outputs_dir, "report_detailed.txt")
            with open(output_path, 'w', encoding='utf-8') as f:
                import sys
                old_stdout = sys.stdout
                sys.stdout = f
                self.cost_analyzer.print_summary(self.current_report)
                self.cost_analyzer.print_recommendations(self.current_report, detailed=True)
                sys.stdout = old_stdout
            print(f"\n{Colors.OKGREEN}✅ Detailed report exported to: {output_path}{Colors.ENDC}")

        elif choice == '4':
            # Ensure we have profile and billing data; try loading if missing
            if not self.current_profile:
                profile_path = os.path.join(self.outputs_dir, "project_profile.json")
                if os.path.exists(profile_path):
                    try:
                        self.current_profile = self.profile_extractor.load_profile(profile_path)
                    except Exception as e:
                        print(f"\n{Colors.FAIL}❌ Error loading profile for HTML export: {e}{Colors.ENDC}")
                        return
                else:
                    print(f"\n{Colors.FAIL}❌ No project profile found for HTML export{Colors.ENDC}")
                    print(f"{Colors.WARNING}💡 Please run complete analysis first (Option 2){Colors.ENDC}")
                    return

            if not self.current_billing:
                billing_path = os.path.join(self.outputs_dir, "mock_billing.json")
                if os.path.exists(billing_path):
                    try:
                        self.current_billing = self.billing_generator.load_billing(billing_path)
                    except Exception as e:
                        print(f"\n{Colors.FAIL}❌ Error loading billing data for HTML export: {e}{Colors.ENDC}")
                        return
                else:
                    print(f"\n{Colors.FAIL}❌ No billing data found for HTML export{Colors.ENDC}")
                    print(f"{Colors.WARNING}💡 Please run complete analysis first (Option 2){Colors.ENDC}")
                    return

            html_path = os.path.join(self.outputs_dir, "cost_optimization_report.html")
            try:
                HTMLReportGenerator.generate_html_report(self.current_profile, self.current_billing, self.current_report, html_path)
                print(f"\n{Colors.OKGREEN}✅ HTML report exported to: {html_path}{Colors.ENDC}")
            except Exception as e:
                print(f"\n{Colors.FAIL}❌ Error generating HTML report: {e}{Colors.ENDC}")

        elif choice == '5':
            return
    
    def load_existing_project(self):
        """Load existing project files"""
        self.print_section_header("LOAD EXISTING PROJECT", "📂")
        
        profile_path = os.path.join(self.outputs_dir, "project_profile.json")
        billing_path = os.path.join(self.outputs_dir, "mock_billing.json")
        report_path = os.path.join(self.outputs_dir, "cost_optimization_report.json")
        
        loaded_items = []
        
        try:
            if os.path.exists(profile_path):
                self.current_profile = self.profile_extractor.load_profile(profile_path)
                print(f"{Colors.OKGREEN}✅ Loaded profile:{Colors.ENDC} {self.current_profile['name']}")
                loaded_items.append("profile")
            
            if os.path.exists(billing_path):
                self.current_billing = self.billing_generator.load_billing(billing_path)
                print(f"{Colors.OKGREEN}✅ Loaded billing:{Colors.ENDC} {len(self.current_billing)} records")
                loaded_items.append("billing")
            
            if os.path.exists(report_path):
                self.current_report = self.cost_analyzer.load_report(report_path)
                print(f"{Colors.OKGREEN}✅ Loaded report:{Colors.ENDC} {self.current_report['summary']['recommendations_count']} recommendations")
                loaded_items.append("report")
            
            if not loaded_items:
                print(f"{Colors.WARNING}⚠️  No existing project files found in '{self.outputs_dir}/' directory{Colors.ENDC}")
            else:
                print(f"\n{Colors.BOLD}{Colors.OKGREEN}Successfully loaded: {', '.join(loaded_items)}{Colors.ENDC}")
        
        except Exception as e:
            print(f"{Colors.FAIL}❌ Error loading project: {e}{Colors.ENDC}")
    
    def run(self):
        """Main CLI loop"""
        self.print_header()
        
        # Try to load existing project
        if os.path.exists(os.path.join(self.outputs_dir, "project_profile.json")):
            print(f"{Colors.CYAN}🔄 Found existing project files...{Colors.ENDC}")
            time.sleep(0.5)
            self.load_existing_project()
            print()
        
        while True:
            self.print_menu()
            choice = input(f"{Colors.BOLD}{Colors.OKGREEN}👉 Select option (1-7): {Colors.ENDC}").strip()
            
            if choice == '1':
                self.enter_project_description()
            
            elif choice == '2':
                self.run_complete_analysis()
            
            elif choice == '3':
                self.view_recommendations()
            
            elif choice == '4':
                self.export_report()
            
            elif choice == '5':
                self.load_existing_project()
            
            elif choice == '6':
                self.view_current_data()
            
            elif choice == '7':
                print(f"\n{Colors.BOLD}{Colors.HEADER}{'═' * 60}{Colors.ENDC}")
                print(f"{Colors.BOLD}{Colors.OKGREEN}👋 Thank you for using Cloud Cost Optimizer!{Colors.ENDC}")
                print(f"{Colors.GREY}   All your data is saved in the '{self.outputs_dir}/' directory{Colors.ENDC}")
                print(f"{Colors.BOLD}{Colors.HEADER}{'═' * 60}{Colors.ENDC}\n")
                break
            
            else:
                print(f"{Colors.FAIL}❌ Invalid option. Please select 1-7{Colors.ENDC}")
            
            input(f"\n{Colors.GREY}Press Enter to continue...{Colors.ENDC}")
            self.print_header()


if __name__ == "__main__":
    cli = CostOptimizerCLI()
    cli.run()