import json
import urllib.parse
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    logger.info("Received S3 Event: " + json.dumps(event, indent=2))

    bucket = event["Records"][0]["s3"]["bucket"]["name"]
    key = urllib.parse.unquote_plus(
        event["Records"][0]["s3"]["object"]["key"], encoding="utf-8"
    )

    logger.info(
        f"Ingestion event detected: File '{key}' successfully loaded into S3 bucket '{bucket}'."
    )

    if not (key.startswith("raw/") and key.endswith(".csv")):
        logger.warning(
            f"Validation Warning: File '{key}' does not match target raw input path format (raw/*.csv). Skipping ETL invocation."
        )
        return {
            "statusCode": 200,
            "body": json.dumps("File skipped: path validation failed."),
        }

    logger.info(
        f"ETL Execution Trigger: Initiating E-Commerce PySpark ETL job for raw data source: s3://{bucket}/{key}"
    )

    return {
        "statusCode": 200,
        "body": json.dumps(
            {
                "message": "S3 PUT event recorded successfully. ETL execution initiated.",
                "s3_source": f"s3://{bucket}/{key}",
            }
        ),
    }
