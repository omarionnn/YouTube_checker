document.addEventListener('DOMContentLoaded', function() {
    // Elements
    const youtubeUrlInput = document.getElementById('youtube-url');
    const questionInput = document.getElementById('question');
    const submitBtn = document.getElementById('submit-btn');
    const followUpBtn = document.getElementById('follow-up-btn');
    const followUpQuestion = document.getElementById('follow-up-question');
    const loadingIndicator = document.getElementById('loading');
    const resultSection = document.getElementById('result-section');
    const answerContainer = document.getElementById('answer-container');
    const errorContainer = document.getElementById('error-container');
    
    // Session ID for follow-up questions
    let sessionId = generateSessionId();
    
    // Event listeners
    submitBtn.addEventListener('click', handleSubmit);
    followUpBtn.addEventListener('click', handleFollowUp);
    
    // Handle main question submission
    async function handleSubmit() {
        const youtubeUrl = youtubeUrlInput.value.trim();
        const question = questionInput.value.trim();
        
        if (!youtubeUrl) {
            showError('Please enter a YouTube URL');
            return;
        }
        
        if (!question) {
            showError('Please enter a question');
            return;
        }
        
        // Reset for new video
        sessionId = generateSessionId();
        showLoading();
        await submitQuestion(youtubeUrl, question, sessionId);
    }
    
    // Handle follow-up question
    async function handleFollowUp() {
        const question = followUpQuestion.value.trim();
        const youtubeUrl = youtubeUrlInput.value.trim();
        
        if (!question) {
            showError('Please enter a follow-up question');
            return;
        }
        
        showLoading();
        await submitQuestion(youtubeUrl, question, sessionId);
        followUpQuestion.value = '';
    }
    
    // Submit question to backend
    async function submitQuestion(youtubeUrl, question, sessionId) {
        try {
            const response = await fetch('/api/ask', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    youtube_url: youtubeUrl,
                    question: question,
                    session_id: sessionId
                })
            });
            
            const data = await response.json();
            
            if (data.success) {
                hideLoading();
                displayAnswer(data.answer);
            } else {
                showError(data.error);
            }
        } catch (error) {
            showError('An error occurred while processing your request');
            console.error('Error:', error);
        }
    }
    
    // Display the answer with formatted timestamps
    function displayAnswer(answer) {
        // Format timestamps in the answer
        const formattedAnswer = answer.replace(/\[(\d{2}:\d{2})\]/g, 
            '<span class="timestamp">[$1]</span>');
        
        answerContainer.innerHTML = formattedAnswer;
        resultSection.classList.remove('hidden');
        errorContainer.classList.add('hidden');
        window.scrollTo({ top: resultSection.offsetTop, behavior: 'smooth' });
    }
    
    // Show loading indicator
    function showLoading() {
        loadingIndicator.classList.remove('hidden');
        errorContainer.classList.add('hidden');
    }
    
    // Hide loading indicator
    function hideLoading() {
        loadingIndicator.classList.add('hidden');
    }
    
    // Display error message
    function showError(message) {
        errorContainer.textContent = message;
        errorContainer.classList.remove('hidden');
        loadingIndicator.classList.add('hidden');
    }
    
    // Generate random session ID
    function generateSessionId() {
        return Date.now().toString(36) + Math.random().toString(36).substr(2);
    }
});
