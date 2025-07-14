# Cover Letter Writing Agent System

An intelligent cover letter generation system powered by LangGraph and FastAPI that creates personalized, professional cover letters in English.

## Features

- **Multi-Agent Architecture**: Uses LangGraph to orchestrate specialized agents for different parts of cover letter generation
- **Resume Analysis**: Automatically extracts relevant information from PDF resumes
- **Company Research**: Searches and analyzes company information to create personalized content
- **Project Matching**: Intelligently matches your experience with job requirements
- **Web Interface**: User-friendly FastAPI web application
- **Document Generation**: Outputs professional Word documents ready for editing

## System Architecture

The system consists of three main agents working in parallel:

1. **Company Research Agent**: Analyzes company information and generates opening and closing sections
2. **Experience Matching Agent**: Customizes project descriptions to match job requirements
3. **Document Assembly Agent**: Combines all sections into a cohesive cover letter

## Installation

1. Clone the repository:
```bash
git clone https://github.com/Ziyan0219/specific-letter-writing-agent.git
cd specific-letter-writing-agent
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
cp .env.template .env
# Edit .env with your OpenAI API key and other configurations
```

## Usage

1. Start the web application:
```bash
python main.py
```

2. Open your browser and navigate to `http://localhost:8000`

3. Upload your PDF resume, enter company name and job description

4. Download your personalized cover letter as a Word document

## Project Structure

```
cover-letter-agent/
├── agents/                 # LangGraph agent implementations
├── templates/             # HTML templates for web interface
├── static/               # CSS, JS, and other static files
├── uploads/              # Temporary file storage
├── generated_letters/    # Output directory for cover letters
├── main.py              # FastAPI application entry point
├── requirements.txt     # Python dependencies
└── README.md           # This file
```

## Contributing

This project is designed for personal use but contributions are welcome. Please feel free to submit issues and enhancement requests.

## License

MIT License

