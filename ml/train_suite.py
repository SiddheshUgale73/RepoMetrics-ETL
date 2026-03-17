import sys
import subprocess
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("Engineering_Analytics_Suite")

def run_script(script_name):
    logger.info(f"--- Training {script_name} ---")
    try:
        # Run the script as a subprocess
        result = subprocess.run(
            [sys.executable, script_name], 
            check=True,
            capture_output=True,
            text=True
        )
        logger.info(f"\u2705 {script_name} completed successfully.\n{result.stdout}")
    except subprocess.CalledProcessError as e:
        logger.error(f"\u274C {script_name} failed.\nError: {e.stderr}")

def main():
    logger.info("=====================================================")
    logger.info("= Initiating Engineering Analytics ML Training Suite =")
    logger.info("=====================================================")
    
    scripts = [
        "predict_burnout.py",
        "predict_pr_merge.py",
        "repo_health_score.py"
    ]
    
    for script in scripts:
        run_script(script)
        
    logger.info("=====================================================")
    logger.info("=           Suite Execution Complete                =")
    logger.info("=  Check the current directory for model artifacts  =")
    logger.info("=====================================================")

if __name__ == "__main__":
    main()
