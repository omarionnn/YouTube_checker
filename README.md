# YouTube Video Q&A Tool

This web application allows users to ask questions about YouTube videos and get AI-generated answers based on the video's transcript.

## Features

- Extract transcripts from YouTube videos
- Answer questions about video content using Claude AI
- Include relevant timestamps in answers
- Support follow-up questions without reloading the transcript
- Clean, user-friendly interface

## Installation

### Prerequisites

- Python 3.8 or higher
- Anthropic API key (for Claude AI)

### Setup

1. Clone the repository:
   ```
   git clone <repository-url>
   cd youtube-answer
   ```

2. Create and activate a virtual environment (recommended):
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows, use: venv\Scripts\activate
   ```

3. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

4. Create a `.env` file with your Anthropic API key:
   ```
   cp .env.example .env
   ```
   Then edit the `.env` file and add your Anthropic API key.

## Usage

### Running Locally

1. Start the Flask application:
   ```
   python app.py
   ```

2. Open your browser and navigate to: `http://127.0.0.1:5000`

3. Enter a YouTube URL and your question, then click "Get Answer"

### Deployment

The application can be deployed to platforms like Heroku, Render, or PythonAnywhere.

For Heroku deployment:

1. Create a `Procfile` with the following content:
   ```
   web: gunicorn app:app
   ```

2. Deploy using the Heroku CLI or GitHub integration

## Configuration

- `ANTHROPIC_API_KEY`: Your Anthropic API key for accessing Claude AI

## Troubleshooting

- **No transcript available**: Some YouTube videos don't have transcripts or have disabled them
- **API rate limits**: If you're getting errors from Claude AI, you might be hitting rate limits
- **Video ID extraction errors**: Make sure you're using a valid YouTube URL format

## How It Works

1. **Transcript Extraction**: The application uses `youtube-transcript-api` to fetch the transcript from the video
2. **Context Management**: Video transcripts are stored in memory for follow-up questions
3. **AI Processing**: Claude AI analyzes the transcript to find relevant information
4. **Answer Generation**: Answers include relevant timestamps and information from the video

## License

This project is licensed under the MIT License - see the LICENSE file for details.
