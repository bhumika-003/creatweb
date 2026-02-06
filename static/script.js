const feedbackForm = document.getElementById('feedback-form');
const productSelect = document.getElementById('product-select');
const feedbackText = document.getElementById('feedback-text');
const ratingInput = document.getElementById('rating-input');
const resultDiv = document.getElementById('result');

feedbackForm.addEventListener('submit', async (e) => {
    e.preventDefault();

    const reviewData = {
        product_name: productSelect.value,
        review_text: feedbackText.value,
        rating: parseInt(ratingInput.value, 10)
    };

    if (!reviewData.review_text || !reviewData.rating) {
        resultDiv.innerHTML = `<p class="negative">Please provide both feedback and a rating.</p>`;
        return;
    }

    try {
        const response = await fetch('/submit-review', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(reviewData),
        });

        if (!response.ok) {
            throw new Error(`API request failed with status ${response.status}`);
        }

        const data = await response.json();
        const highestScoreLabel = data.scored_labels.reduce((prev, current) => (prev.score > current.score) ? prev : current);
        const sentimentResult = highestScoreLabel.label;

        let responseMessage = '';
        let responseClass = '';

        if (sentimentResult === 'positive' || (sentimentResult.startsWith('LABEL_') && highestScoreLabel.score > 0.5)) {
            responseMessage = "Thanks for the appreciation! Your review has been submitted.";
            responseClass = 'positive';
        } else if (sentimentResult === 'negative' || (sentimentResult.startsWith('LABEL_') && highestScoreLabel.score < 0.5)) {
            responseMessage = "We regret the inconvenience. Your feedback has been recorded and we will look into this matter.";
            responseClass = 'negative';
        } else {
            responseMessage = "Thank you for your feedback. It has been submitted.";
            responseClass = 'neutral';
        }

        resultDiv.innerHTML = `<p class="${responseClass}">${responseMessage}</p>`;
        feedbackForm.reset(); // Clear the form

    } catch (error) {
        console.error('Error:', error);
        resultDiv.innerHTML = `<p class="negative">An error occurred while submitting your review.</p>`;
    }
});