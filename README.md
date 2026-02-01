# Food Suitability Search API

A FastAPI-based intelligent food search system that allows users to query nutritional information and food suitability using natural language processing powered by OpenAI's GPT models and LangChain.

## Features

- **Natural Language Queries**: Search for foods using plain English (e.g., "show me low-carb foods suitable for diabetes")
- **Nutritional Database**: Access to comprehensive food nutritional data including:
  - Glycemic Index
  - Calories, Carbohydrates, Protein, Fat
  - Suitability for Diabetes and Blood Pressure conditions
  - Mineral content (Sodium, Potassium, Magnesium, Calcium)
- **Web Interface**: Clean, responsive web UI for easy interaction
- **RESTful API**: JSON API endpoints for programmatic access
- **Intelligent Filtering**: AI-powered query interpretation to filter the food database

## Technology Stack

- **Backend**: FastAPI (Python web framework)
- **AI/ML**: LangChain + OpenAI GPT-4o-mini
- **Data Processing**: Pandas
- **Frontend**: HTML/CSS/JavaScript with Jinja2 templates
- **Server**: Uvicorn ASGI server

## Prerequisites

- Python 3.8+
- OpenAI API key
- Internet connection for AI model access

## Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd food_search_api
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   Create a `.env` file in the project root:
   ```env
   OPENAI_API_KEY=your_openai_api_key_here
   ```

## Usage

### Starting the Server

```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`

### Web Interface

Navigate to `http://localhost:8000` in your browser to access the interactive web interface.

### API Endpoints

#### GET /
- **Description**: Web interface homepage
- **Response**: HTML page with search functionality

#### POST /search
- **Description**: Search for foods using natural language
- **Request Body**:
  ```json
  {
    "query": "show me foods with low glycemic index suitable for diabetes"
  }
  ```
- **Response**: Filtered food data based on the query

#### GET /debug/df (Development Only)
- **Description**: Check dataframe status and basic info
- **Response**: DataFrame shape, columns, and sample count

### Example Queries

- "Show me low-carb foods"
- "Find foods suitable for diabetes with less than 200 calories"
- "What foods are good for blood pressure?"
- "Foods high in protein but low in sodium"
- "Low glycemic index foods under 150 calories"

## Project Structure

```
food_search_api/
├── app/
│   ├── main.py           # FastAPI application and routes
│   ├── chain.py          # LangChain integration and AI processing
│   ├── data.py           # Data loading and management
│   ├── security.py       # Security utilities for safe evaluation
│   └── pred_food.csv     # Food nutritional database
├── templates/
│   └── index.html        # Web interface template
├── requirements.txt      # Python dependencies
├── create_search_results_table.sql  # Database schema
└── README.md            # This file
```

## Data Schema

The food database includes the following columns:

| Column | Type | Description |
|--------|------|-------------|
| Food Name | string | Name of the food item |
| Glycemic Index | int | Glycemic index value |
| Calories | int | Calories per serving |
| Carbohydrates | float | Carbohydrate content (g) |
| Protein | float | Protein content (g) |
| Fat | float | Fat content (g) |
| Suitable for Diabetes | string | Diabetes suitability indicator |
| Suitable for Blood Pressure | int | Blood pressure suitability (0/1) |
| Sodium Content | int | Sodium content (mg) |
| Potassium Content | int | Potassium content (mg) |
| Magnesium Content | int | Magnesium content (mg) |
| Calcium Content | int | Calcium content (mg) |

## Development

### Running in Development Mode

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Environment Variables

- `OPENAI_API_KEY`: Required for AI functionality

### Security Notes

- The `/debug/df` endpoint should be removed or secured in production
- Consider implementing authentication for production deployments
- Review and secure any eval operations in the codebase

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

For support, please open an issue in the GitHub repository or contact the development team.

## Version History

- **1.0.0**: Initial release with natural language food search functionality