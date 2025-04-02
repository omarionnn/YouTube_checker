import os
import re
from urllib.parse import urlparse, parse_qs
from flask import Flask, render_template, request, jsonify
import anthropic
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Initialize Anthropic client
client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

# Store video context for follow-up questions
video_context = {}

def extract_video_id(youtube_url):
    """Extract the video ID from a YouTube URL."""
    parsed_url = urlparse(youtube_url)
    
    if parsed_url.hostname in ('youtu.be', 'www.youtu.be'):
        return parsed_url.path[1:]
    
    if parsed_url.hostname in ('youtube.com', 'www.youtube.com'):
        if parsed_url.path == '/watch':
            return parse_qs(parsed_url.query)['v'][0]
        elif parsed_url.path.startswith('/embed/'):
            return parsed_url.path.split('/')[2]
        elif parsed_url.path.startswith('/v/'):
            return parsed_url.path.split('/')[2]
    
    # If we get here, it's not a valid YouTube URL
    raise ValueError("Could not extract video ID from URL")

def get_youtube_transcript(video_id):
    """Get the transcript for a YouTube video."""
    try:
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
        
        # Format the transcript with timestamps
        formatted_transcript = ""
        for entry in transcript_list:
            minutes = int(entry['start'] // 60)
            seconds = int(entry['start'] % 60)
            timestamp = f"{minutes:02d}:{seconds:02d}"
            formatted_transcript += f"[{timestamp}] {entry['text']}\n"
        
        # Also create a structured version for Claude to reference
        structured_transcript = []
        for entry in transcript_list:
            structured_transcript.append({
                "timestamp": entry['start'],
                "text": entry['text']
            })
        
        return {
            "success": True,
            "transcript": formatted_transcript,
            "structured": structured_transcript
        }
    except (TranscriptsDisabled, NoTranscriptFound):
        return {
            "success": False,
            "error": "No transcript available for this video."
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Error retrieving transcript: {str(e)}"
        }

def create_claude_prompt(question, transcript, video_id, conversation_history=None):
    """Create a prompt for Claude based on the video transcript and user question."""
    system_prompt = f"""
    You are an assistant that answers questions about YouTube videos based solely on their transcript.
    The transcript below is from YouTube video ID: {video_id}
    
    When answering:
    1. Only use information contained in the transcript
    2. If the answer isn't in the transcript, say "The transcript doesn't contain information about this."
    3. Include relevant timestamps from the video in your answers
    4. Be concise but thorough
    5. Do not make up information or use external knowledge
    6. Format timestamps as [MM:SS] in your response
    
    Transcript:
    {transcript}
    """
    
    # Add conversation history if it exists
    if conversation_history:
        messages = conversation_history + [{"role": "user", "content": question}]
    else:
        messages = [{"role": "user", "content": question}]
    
    return system_prompt, messages

def query_claude(system_prompt, messages):
    """Send a query to Claude and get the response."""
    try:
        response = client.messages.create(
            model="claude-3-opus-20240229",
            system=system_prompt,
            messages=messages,
            max_tokens=1024,
            temperature=0.0,
        )
        return {"success": True, "message": response.content[0].text}
    except Exception as e:
        return {"success": False, "error": f"Error from Claude API: {str(e)}"}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/ask', methods=['POST'])
def ask():
    data = request.json
    youtube_url = data.get('youtube_url')
    question = data.get('question')
    session_id = data.get('session_id')
    
    if not youtube_url or not question:
        return jsonify({"success": False, "error": "Both YouTube URL and question are required"})
    
    try:
        video_id = extract_video_id(youtube_url)
        
        # Check if we already have the transcript
        if session_id not in video_context:
            transcript_result = get_youtube_transcript(video_id)
            if not transcript_result["success"]:
                return jsonify(transcript_result)
            
            # Store the context for future questions
            video_context[session_id] = {
                "video_id": video_id,
                "transcript": transcript_result["transcript"],
                "conversation": []
            }
        
        # Get the stored context
        context = video_context[session_id]
        
        # Create the prompt for Claude
        system_prompt, messages = create_claude_prompt(
            question, 
            context["transcript"], 
            context["video_id"],
            context["conversation"]
        )
        
        # Get response from Claude
        claude_response = query_claude(system_prompt, messages)
        
        if claude_response["success"]:
            # Update conversation history
            context["conversation"].append({"role": "user", "content": question})
            context["conversation"].append({"role": "assistant", "content": claude_response["message"]})
            
            # Keep conversation context manageable
            if len(context["conversation"]) > 10:
                # Remove oldest Q&A pair (2 entries)
                context["conversation"] = context["conversation"][2:]
            
            return jsonify({
                "success": True,
                "answer": claude_response["message"],
                "session_id": session_id
            })
        else:
            return jsonify(claude_response)
    
    except ValueError as e:
        return jsonify({"success": False, "error": str(e)})
    except Exception as e:
        return jsonify({"success": False, "error": f"An unexpected error occurred: {str(e)}"})

if __name__ == '__main__':
    app.run(debug=True)
