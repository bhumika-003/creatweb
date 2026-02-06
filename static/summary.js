document.addEventListener('DOMContentLoaded', () => {
    const productListDiv = document.getElementById('product-list');
    const summaryDisplay = document.getElementById('summary-display');
    const summaryProductTitle = document.getElementById('summary-product-title');
    const summaryText = document.getElementById('summary-text');

    // Fetch all products that have summaries and create buttons
    fetch('/products')
        .then(response => response.json())
        .then(data => {
            if (data.products && data.products.length > 0) {
                data.products.forEach(productName => {
                    const button = document.createElement('button');
                    button.textContent = productName.replace(/-/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
                    button.dataset.product = productName;
                    button.addEventListener('click', () => fetchSummary(productName));
                    productListDiv.appendChild(button);
                });
            } else {
                productListDiv.innerHTML = '<p>No summaries available yet. Submit some reviews first!</p>';
            }
        })
        .catch(error => {
            console.error('Error fetching products:', error);
            productListDiv.innerHTML = '<p class="negative">Could not load product list.</p>';
        });

    // Function to fetch and display a summary
    function fetchSummary(productName) {
        // First, trigger the summarization process on the backend
        fetch(`/summarize/${productName}`, { method: 'POST' })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Summarization failed.');
                }
                return response.json();
            })
            .then(summaryData => {
                // Then, display the new summary
                summaryProductTitle.textContent = productName.replace(/-/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
                summaryText.textContent = summaryData.summary;
                summaryDisplay.style.display = 'block';
            })
            .catch(error => {
                console.error('Error fetching summary:', error);
                summaryText.textContent = 'Could not load summary for this product.';
            });
    }
});