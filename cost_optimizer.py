"""
Cloud Cost Optimizer - Main Entry Point
AI-Powered Multi-Cloud Cost Optimization System
"""

from cli import CostOptimizerCLI


def main():
    """Main entry point for the application"""
    cli = CostOptimizerCLI()
    cli.run()


if __name__ == "__main__":
    main()