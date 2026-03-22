import sys
import subprocess
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("Mentor_Support_Suite")

import os

def run_script(script_name):
    logger.info(f"--- Generating Insights for {script_name} ---")
    # Get the directory of the current script (train_suite.py)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    script_path = os.path.join(script_dir, script_name)
    
    try:
        # Run the script as a subprocess
        result = subprocess.run(
            [sys.executable, script_path], 
            check=True,
            capture_output=True,
            text=True
        )
        logger.info(f"\u2705 {script_name} completed successfully.\n{result.stdout}")
    except subprocess.CalledProcessError as e:
        logger.error(f"\u274C {script_name} failed.\nError: {e.stderr}")

def main():
    logger.info("=====================================================")
    logger.info("= Initiating Academic Analytics Training Suite for Mentors =")
    logger.info("=====================================================")
    
    scripts = [
        "predict_burnout.py",
        "predict_pr_merge.py",
        "repo_health_score.py",
        "advanced_analytics.py"
    ]
    
    for script in scripts:
        run_script(script)
        
    logger.info("=====================================================")
    logger.info("=           Suite Execution Complete                =")
    logger.info("=  Check the current directory for model artifacts  =")
    logger.info("=====================================================")

if __name__ == "__main__":
    main()
