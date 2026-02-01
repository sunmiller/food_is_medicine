from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers.string import StrOutputParser
from dotenv import load_dotenv

from app.data import df
from app.security import safe_eval_pandas

# Load environment variables from .env file
load_dotenv()

chatgpt = ChatOpenAI(model="gpt-4o-mini", temperature=0)

FILTER_PROMPT = """Given the following schema of a dataframe table,
            your task is to figure out the best pandas query to
            filter the dataframe based on the user query which
            will be in natural language.

            The schema is as follows:

            #   Column                       Non-Null Count  Dtype
            ---  ------                       --------------  -----
            0   Food Name                    502 non-null    object
            1   Glycemic Index               502 non-null    int64
            2   Calories                     502 non-null    int64
            3   Carbohydrates                502 non-null    float64
            4   Protein                      502 non-null    float64
            5   Fat                          502 non-null    float64
            6   Suitable for Diabetes        502 non-null    object
            7   Suitable for Blood Pressure  502 non-null    int64
            8   Sodium Content               502 non-null    int64
            9   Potassium Content            502 non-null    int64
            10  Magnesium Content            502 non-null    int64
            11  Calcium Content              502 non-null    int64
            12  Fiber Content                501 non-null    float64


            You will try to figure out the pandas query focusing
            only on "Food Name" if the user mentions
            anything about these in their natural language query.
            If you find the food name in the dataframe simply return it.
            Do not make up column names, only use the above.
            If not then return an empty data frame.
            Remember the dataframe name is df.

            Just return only the pandas query and nothing else.
            Do not return the results as markdown, just return the query

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

    # ✅ USE THE SECURITY FUNCTION!
    result_df = safe_eval_pandas(pandas_query, df)

    if result_df.empty:
        return {"message": "No results found"}

    return {
        "query": pandas_query,
        "results": result_df.to_dict(orient="records")
    }
