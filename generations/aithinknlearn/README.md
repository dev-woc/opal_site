# Agentic Literacy Pipeline

## Project Overview

The Agentic Literacy Pipeline is a comprehensive system designed to enhance reading comprehension and critical thinking skills through AI-powered analysis and personalized learning pathways. This application integrates multiple AI agents working in tandem to provide intelligent document analysis, personalized recommendations, and adaptive learning experiences.

## Core Features

1. **Document Ingestion & Processing** - Intelligent system for uploading and parsing various document formats with automatic metadata extraction and content structuring

2. **AI-Powered Analysis** - Advanced NLP agents that analyze documents for key concepts, reading difficulty, thematic elements, and educational value

3. **Personalized Learning Pathways** - Adaptive recommendation engine that creates customized reading sequences based on user proficiency, interests, and learning objectives

4. **Interactive Comprehension Assessment** - Dynamic quiz generation and evaluation system that adapts to user performance and identifies knowledge gaps

5. **Progress Tracking & Analytics** - Comprehensive dashboard providing detailed insights into learning progress, comprehension improvements, and skill development over time

## Tech Stack

**Backend:**
- Python 3.10+
- Flask/FastAPI for REST API
- PostgreSQL for data persistence
- Redis for caching

**Frontend:**
- React 18+ with TypeScript
- Tailwind CSS for styling
- Plotly for analytics visualizations

**AI/ML:**
- OpenAI API for language models
- Anthropic Claude for advanced analysis
- LangChain for agent orchestration
- Hugging Face for NLP utilities

## Project Structure

```
aithinknlearn/
├── README.md                 # Project documentation
├── init.sh                   # Development setup script
├── .gitignore               # Git ignore patterns
├── backend/
│   ├── app.py              # Flask/FastAPI application
│   ├── requirements.txt     # Python dependencies
│   ├── agents/             # AI agent implementations
│   ├── models/             # Database models
│   ├── routes/             # API endpoints
│   └── config.py           # Configuration settings
├── frontend/
│   ├── package.json        # Node dependencies
│   ├── src/
│   │   ├── components/     # React components
│   │   ├── pages/          # Page components
│   │   ├── App.tsx         # Main app component
│   │   └── index.tsx       # Entry point
│   └── public/             # Static assets
├── docs/                    # Documentation
└── tests/                   # Test suite
```

## Getting Started

### Prerequisites

- Python 3.10 or higher
- Node.js 16 or higher
- PostgreSQL 12 or higher
- API keys for OpenAI and Anthropic Claude

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/aithinknlearn.git
cd aithinknlearn
```

2. Run the initialization script:
```bash
chmod +x init.sh
./init.sh
```

3. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your API keys and database credentials
```

### Development

Start the development server:
```bash
./init.sh
```

This will:
- Install Python dependencies
- Install Node.js dependencies
- Start the Flask/FastAPI backend server
- Start the React development server

### Testing

Run the test suite:
```bash
# Backend tests
python -m pytest tests/

# Frontend tests
npm test --prefix frontend/
```

## Documentation

Detailed documentation is available in the `/docs` directory:
- [Architecture Overview](./docs/architecture.md)
- [API Reference](./docs/api.md)
- [Agent Design](./docs/agents.md)
- [Database Schema](./docs/schema.md)

## Contributing

Please follow these guidelines:
1. Create a feature branch from `main`
2. Commit with clear, descriptive messages
3. Submit a pull request with documentation
4. Ensure all tests pass before submission

## License

This project is licensed under the MIT License - see LICENSE file for details.

## Support

For questions or issues, please open a GitHub issue or contact the development team.
