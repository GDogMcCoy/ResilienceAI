"""
ResilienceAI - Pipeline Orchestrator
Runs the full data → features → EDA → training → agent pipeline.
"""
import argparse
import sys
import time


def run_pipeline(steps=None, force_download=False):
    """Run pipeline steps in order."""
    all_steps = ["download", "features", "eda", "train", "agent"]
    if steps is None:
        steps = all_steps

    print("=" * 60)
    print("ResilienceAI - Full Pipeline")
    print(f"Steps: {', '.join(steps)}")
    print("=" * 60)

    start = time.time()

    if "download" in steps:
        print("\n>>> Step 1/5: Data Acquisition")
        from src.download_data import download_all
        download_all(force=force_download)

    if "features" in steps:
        print("\n>>> Step 2/5: Feature Engineering")
        from src.feature_engineering import run_feature_engineering
        run_feature_engineering()

    if "eda" in steps:
        print("\n>>> Step 3/5: Exploratory Data Analysis")
        from src.pipeline.eda import run_eda
        run_eda()

    if "train" in steps:
        print("\n>>> Step 4/5: Model Training")
        from src.train_models import train_and_evaluate
        train_and_evaluate()

    if "agent" in steps:
        print("\n>>> Step 5/5: Agent Configuration")
        from src.agent import export_agent_config
        export_agent_config()

    elapsed = time.time() - start
    print(f"\n{'=' * 60}")
    print(f"Pipeline complete! Total time: {elapsed:.1f}s")
    print(f"{'=' * 60}")
    print("\nNext steps:")
    print("  1. Review outputs in outputs/figures/")
    print("  2. Launch dashboard: streamlit run app/dashboard.py")
    print("  3. Configure Archia agent with models/agent_config.json")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="ResilienceAI Pipeline")
    parser.add_argument("--steps", nargs="+",
                        choices=["download", "features", "eda", "train", "agent"],
                        help="Specific steps to run (default: all)")
    parser.add_argument("--force", action="store_true",
                        help="Force re-download of data")
    args = parser.parse_args()
    run_pipeline(steps=args.steps, force_download=args.force)
