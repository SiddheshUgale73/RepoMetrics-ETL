from pathlib import Path
import sqlite3
import pandas as pd
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent
DB_NAME = BASE_DIR / "repo_metrics.db"
SCHEMA_FILE = BASE_DIR / "repo_metrics_schema.sql"

TABLES_TO_LOAD = [
    ("USER_TYPES", BASE_DIR / "user_types.csv"),
    ("USERS", BASE_DIR / "users.csv"),
    ("LANGUAGES", BASE_DIR / "languages.csv"),
    ("REPOSITORIES", BASE_DIR / "repositories.csv"),
    ("AUTHORS", BASE_DIR / "authors.csv"),
    ("COMMITS", BASE_DIR / "commits.csv"),
    ("PULL_REQUESTS", BASE_DIR / "pull_requests.csv")
]

NUMERIC_SUFFIXES = (
    "_id",
    "id",
    "_count",
    "count",
    "_number",
    "number",
    "followers",
    "following",
    "public_repos",
    "stargazers_count",
    "forks_count",
    "pr_number"
)

DATE_COLUMNS = ("created_at", "updated_at", "merged_at", "commit_date")


def resolve_table_columns(cursor, table_name: str) -> list[str]:
    cursor.execute(f"PRAGMA table_info({table_name})")
    return [row[1] for row in cursor.fetchall()]


def sanitize_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    # Normalize whitespace and empty strings
    for column in df.select_dtypes(include=["object"]):
        df[column] = df[column].astype(str).str.strip().replace({"": None, "NA": None, "N/A": None})

    # Convert integer-like columns to numeric when appropriate
    for column in df.columns:
        lower_name = column.lower()
        if any(lower_name.endswith(suffix) for suffix in NUMERIC_SUFFIXES):
            df[column] = pd.to_numeric(df[column], errors="coerce", downcast="integer")

    # Convert known date columns to string in ISO format if possible
    for column in df.columns:
        if column.lower() in DATE_COLUMNS:
            df[column] = pd.to_datetime(df[column], errors="coerce").dt.strftime("%Y-%m-%d %H:%M:%S")

    # Remove rows with no meaningful values
    df = df.dropna(how="all")
    return df


def load_schema(cursor: sqlite3.Cursor, schema_path: Path) -> None:
    if not schema_path.exists():
        raise FileNotFoundError(f"Schema file not found: {schema_path}")

    schema_sql = schema_path.read_text(encoding="utf-8")
    schema_sql = schema_sql.replace("CREATE TABLE ", "CREATE TABLE IF NOT EXISTS ")
    cursor.executescript(schema_sql)


def load_csv_to_table(conn: sqlite3.Connection, table_name: str, csv_path: Path) -> int:
    if not csv_path.exists():
        raise FileNotFoundError(f"CSV file not found: {csv_path}")

    df = pd.read_csv(csv_path, keep_default_na=False, na_values=["", "NA", "N/A"])
    df = sanitize_dataframe(df)
    if df.empty:
        logger.warning("%s is empty after sanitization. Skipping load.", csv_path.name)
        return 0

    cursor = conn.cursor()
    table_columns = resolve_table_columns(cursor, table_name)
    if not table_columns:
        raise ValueError(f"No schema defined for table {table_name}")

    lower_table_columns = {col.lower(): col for col in table_columns}
    lower_df_columns = {col.lower(): col for col in df.columns}

    matched_columns = [lower_df_columns[col] for col in lower_table_columns if col in lower_df_columns]
    if not matched_columns:
        raise ValueError(
            f"CSV file {csv_path.name} does not contain any columns matching table {table_name}"
        )

    aligned_df = pd.DataFrame()
    for target_column in table_columns:
        source_key = target_column.lower()
        if source_key in lower_df_columns:
            aligned_df[target_column] = df[lower_df_columns[source_key]]
        else:
            aligned_df[target_column] = None

    aligned_df.to_sql(table_name, conn, if_exists="append", index=False, method="multi")
    return len(aligned_df)


def migrate() -> None:
    """Migrate CSV files into SQLite using the local schema."""
    if not SCHEMA_FILE.exists():
        logger.error("Schema file not found: %s", SCHEMA_FILE)
        return

    try:
        with sqlite3.connect(DB_NAME) as conn:
            conn.execute("PRAGMA foreign_keys = ON")
            logger.info("Initializing SQLite database: %s", DB_NAME)
            load_schema(conn.cursor(), SCHEMA_FILE)

            for table_name, csv_path in TABLES_TO_LOAD:
                if not csv_path.exists():
                    logger.warning("Missing file %s, skipping %s.", csv_path.name, table_name)
                    continue

                logger.info("Loading %s into %s", csv_path.name, table_name)
                row_count = load_csv_to_table(conn, table_name, csv_path)
                total = conn.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()[0]
                logger.info(
                    "Loaded %d rows into %s (total rows after load: %d)",
                    row_count,
                    table_name,
                    total,
                )

        logger.info("Migration to SQLite completed successfully.")
    except Exception as error:
        logger.exception("Migration failed: %s", error)


if __name__ == "__main__":
    migrate()
