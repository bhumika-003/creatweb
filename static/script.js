const feedbackForm = document.getElementById('feedback-form');
const feedbackText = document.getElementById('feedback-text');
const ratingInput = document.getElementById('rating-input');
const resultDiv = document.getElementById('result');

// The API is now on your backend
const apiUrl = 'https://creatweb-8kd2.onrender.com/analyze-sentiment';

feedbackForm.addEventListener('submit', async (e) => {
    e.preventDefault();

    const feedback = feedbackText.value;
    const rating = ratingInput.value;

    if (!feedback || !rating) {
        resultDiv.textContent = 'Please provide both feedback and a rating.';
        return;
    }

    try {
        const response = await fetch(apiUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                'text': feedback,
            }),
        });

        if (!response.ok) {
            throw new Error(`API request failed with status ${response.status}`);
        }

        const data = await response.json();
        if (data.error) {
            throw new Error(data.error);
        }
        
        const highestScoreLabel = data.scored_labels.reduce((prev, current) => (prev.score > current.score) ? prev : current);
        const sentimentResult = highestScoreLabel.label;
        const score = highestScoreLabel.score;

        resultDiv.textContent = `Sentiment: ${sentimentResult} (Score: ${score.toFixed(2)})`;

    } catch (error) {
        console.error('Error:', error);
        resultDiv.textContent = 'An error occurred while analyzing sentiment.';
    }
});