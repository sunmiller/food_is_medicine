from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers.string import StrOutputParser
from dotenv import load_dotenv

from app.data import df
from app.security import safe_eval_pandas

# Load environment variables from .env file
load_dotenv()

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

Your task is to generate a valid pandas filtering query based on the user's natural language question.

Rules:
- Use ONLY the column names listed above.
- The dataframe name is df.
- Return ONLY a pandas query (no markdown, no explanation).
- Do NOT invent column names.
- When filtering by Food Name, always use:
  df["Food Name"].str.contains("<food>", case=False, na=False)

Decision logic:
1. If the user mentions a specific food, filter by "Food Name".
2. If the user mentions diabetes, filter where "Suitable for Diabetes" == 1.
3. If the user mentions blood pressure or hypertension, filter where "Suitable for Blood Pressure" == 1.
3. If BOTH a food and diabetes are mentioned, apply BOTH filters together.
4. If the user mentions diabetes without a food, return all foods suitable for diabetes.
5. If no valid filters apply, return an empty dataframe using df.iloc[0:0].

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

    print("RAW QUERY FROM LLM:")
    print(raw)

    pandas_query = extract_pandas_query(raw)

    print("EXECUTING:")
    print(pandas_query)

    # USE THE SECURITY FUNCTION!
    result_df = safe_eval_pandas(pandas_query, df)
    print(result_df)

    if result_df.empty:
        return {"message": "No results found, try to rephrase your query."}

    return {
        "query": pandas_query,
        "results": result_df.to_dict(orient="records")
    }
