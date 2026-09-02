from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers.string import StrOutputParser
from dotenv import load_dotenv
import os

from app.data import get_df
from app.security import safe_eval_pandas
import pandas as pd
import logging

# Load environment variables from .env file
load_dotenv()

# Configure logging
log_level = os.getenv('LOG_LEVEL', 'INFO').upper()
logging.basicConfig(level=getattr(logging, log_level, logging.INFO))
logger = logging.getLogger(__name__)

chatgpt = ChatOpenAI(model="gpt-4o-mini", temperature=0)

FILTER_PROMPT = """
You are given a pandas DataFrame named df with the following schema:

#   Column                       Dtype
0   Food Name                    object
1   Glycemic Index               int64
2   Calories                     int64
3   Carbohydrates                float64
4   Protein                      float64
5   Fat                          float64
6   Suitable for Diabetes        int64
7   Suitable for Blood Pressure  int64
8   Sodium Content               int64
9   Potassium Content            int64
10  Magnesium Content            int64
11  Calcium Content              int64
12  Fiber Content                float64
13  ServingSize                    int64
14  GlycemicLoad                float64

Your task is to generate a valid pandas filtering query based on the user's natural language question.

Rules:
- Use ONLY the column names listed above.
- The dataframe name is df.
- Return ONLY a pandas query (no markdown, no explanation).
- Do NOT invent column names.
- When filtering by Food Name, always use:
df[df["Food Name"].str.contains("<food>", case=False, na=False)]

Decision logic (follow strictly in this order):

1. If a specific food is mentioned in the query:
   - ALWAYS filter ONLY by "Food Name".
   - DO NOT apply any suitability filters,
     even if diabetes or blood pressure is mentioned.
   - Return all matching food rows.

2. If NO food is mentioned and diabetes is mentioned:
   - Filter where "Suitable for Diabetes" == 1.

3. If NO food is mentioned and blood pressure or hypertension is mentioned:
   - Filter where "Suitable for Blood Pressure" == 1.

4. If no valid filters apply, return df.iloc[0:0].

Examples:

User Query: Can I eat potato chips if I have diabetes
Pandas Query: df[df["Food Name"].str.contains("potato chips", case=False, na=False)]

User Query: Can I eat potato chips if I have hypertension
Pandas Query: df[df["Food Name"].str.contains("potato chips", case=False, na=False)]

User Query: Is banana good for high blood pressure
Pandas Query: df[df["Food Name"].str.contains("banana", case=False, na=False)]

User Query: What foods are suitable for hypertension
Pandas Query: df[df["Suitable for Blood Pressure"] == 1]

User Query: What foods are suitable for diabetes
Pandas Query: df[df["Suitable for Diabetes"] == 1]


User Query: {user_query}

Pandas Query:
"""


prompt = ChatPromptTemplate.from_template(FILTER_PROMPT)

chain = prompt | chatgpt | StrOutputParser()

def extract_pandas_query(raw: str) -> str:
    lines = []

    for line in raw.splitlines():
        line = line.strip()

        # Skip empty lines and markdown/code formatting
        if not line:
            continue
        if line.startswith("```"):
            continue
        if line.lower() == "python":
            continue

        lines.append(line)

    if not lines:
        raise ValueError("No valid pandas query found")

    return lines[-1]

def run_food_query(user_query: str):
    raw = chain.invoke({"user_query": user_query})

    logger.debug(f"RAW LLM OUTPUT: {raw}")

    pandas_query = extract_pandas_query(raw)

    logger.info(f"Executing query: {pandas_query}")

    # USE THE SECURITY FUNCTION!
    result = safe_eval_pandas(pandas_query, get_df())
    logger.debug(f"Result type: {type(result)}")

     # Normalize result type
    if isinstance(result, pd.Series):
        if result.dtype == bool:
            result_df = result.to_frame().T
            
        else:
            result_df = result.to_frame()
    elif isinstance(result, pd.DataFrame):
        result_df = result
    else:
        result_df = pd.DataFrame()

    logger.debug(f"Result type: {type(result)}")

    if result_df.empty:
        return {"message": "No results found, try to rephrase your query."}

    # NaN/NaT (e.g. blank sheet cells) aren't valid JSON; convert to null
    result_df = result_df.astype(object).where(result_df.notna(), None)

    return {
        "query": pandas_query,
        "results": result_df.to_dict(orient="records")
    }
