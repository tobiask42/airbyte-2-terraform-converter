from api_processing import download_from_airbyte_api
from core_config.static_values import TIMESTAMP_PATTERN
from gen_terra import generate_terra_src, generate_terra_dest, generate_terra_conn, generate_imports
from argparse import ArgumentParser, Namespace
import sys
from core_config import CustomPaths, ExitCode
from loguru import logger
from datetime import datetime

@logger.catch
def main(args: Namespace) -> int:
    exit_code = ExitCode.SUCCESS
    timestamp: str = datetime.now().strftime(TIMESTAMP_PATTERN)
    if not CustomPaths.LOG_PATH.exists():
        CustomPaths.LOG_PATH.mkdir()
    logger.add(CustomPaths.LOG_PATH / f"file_{timestamp}.log", rotation="5 MB")
    dl: bool = args.download
    ts: bool = args.airbyte2terraform_src
    td: bool = args.airbyte2terraform_dest
    tc: bool = args.airbyte2terraform_conn
    ci: bool = args.create_imports
    a: bool = args.all
    logger.debug(f"args.download = {args.download}, dl = {dl}")
    logger.debug(f"args.airbyte2terraform_src = {args.airbyte2terraform_src}, ts = {ts}")
    logger.debug(f"args.airbyte2terraform_dest = {args.airbyte2terraform_dest}, td = {td}")
    logger.debug(f"args.airbyte2terraform_conn = {args.airbyte2terraform_conn}, tc = {tc}")
    logger.debug(f"args.all = {args.all}, a = {a}")

    if a:
        logger.debug("triggered 'all' flag")
        dl = ts = td = tc = ci = True
        logger.debug("Set all parameters to True")
    if dl:  
            logger.info("Downloading data from Airbyte")  
            try:  
                download_from_airbyte_api()  
            except Exception:  
                logger.exception("Failed to download data")  
                exit_code |= ExitCode.DOWNLOAD_FAILED
    
    # Hier Filter anwenden -> Nach Nutzerparametern
    
    if ts:  
        logger.info("Converting source data into tf")  
        if not generate_terra_src():  
            exit_code |= ExitCode.SOURCE_TF_FAILED  

    if td:  
        logger.info("Converting destination data into tf")  
        if not generate_terra_dest():  
            exit_code |= ExitCode.DESTINATION_TF_FAILED  

    if tc:  
        logger.info("Converting connection data into tf")  
        if not generate_terra_conn():  
            exit_code |= ExitCode.CONNECTION_TF_FAILED  

    if ci and (ts or td or tc):  
        logger.info("Creating import tf files")  
        if not generate_imports():  
            exit_code |= ExitCode.IMPORT_FAILED  

    if exit_code != ExitCode.SUCCESS:  
        logger.warning(f"Finished with errors: {exit_code!r}")
    
    return int(exit_code)

if __name__ == "__main__":
    parser = ArgumentParser(
        description="Script for downloading data from Airbyte and converting it into Terraform Scripts",
        epilog="""Exit-Codes:  
                0:  Success  
                1:  Download failed  
                2:  Source TF generation failed  
                4:  Destination TF generation failed  
                8:  Connection TF generation failed  
                16: Import TF generation failed
                (combined codes are possible)"""
    )
    parser.add_argument("-dl","--download",action="store_true", help="Download Data from Airbyte and store it as json")
    parser.add_argument("-a2ts","--airbyte2terraform_src",action="store_true",help="Converts downloaded source data into tf files")
    parser.add_argument("-a2td","--airbyte2terraform_dest", action="store_true", help="Converts downloaded destination data into tf files")
    parser.add_argument("-a2tc","--airbyte2terraform_conn", action="store_true", help="Converts downloaded connection data into tf files")
    parser.add_argument("-ci", "--create-imports", action="store_true", help="Generates import blocks for existing Airbyte resources")
    parser.add_argument("-a", "--all",action="store_true", help="Performs all steps")
    args: Namespace = parser.parse_args()
    if not (args.download or args.airbyte2terraform_conn or args.airbyte2terraform_dest or args.airbyte2terraform_src or args.all):
        parser.error(
            "At least one parameter needs to be provided"
        )
    sys.exit(main(args))