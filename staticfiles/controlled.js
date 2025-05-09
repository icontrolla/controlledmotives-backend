console.log("Username:", username);


        document.addEventListener('DOMContentLoaded', () => {
            const modal = document.getElementById('painting-modal');
            const modalImage = document.getElementById('modal-image');
            const modalTitle = document.getElementById('modal-title');
            const modalFlowers = document.getElementById('modal-flowers');
            const closeButton = document.querySelector('.close-button');

            const thumbnails = document.querySelectorAll('.painting-thumbnail');

            thumbnails.forEach(thumbnail => {
                thumbnail.addEventListener('click', () => {
                    const imageSrc = thumbnail.getAttribute('data-image');
                    const title = thumbnail.getAttribute('data-title');
                    const flowers = thumbnail.getAttribute('data-flowers');

                    modalImage.src = imageSrc;
                    modalTitle.textContent = title;
                    modalFlowers.textContent = `${flowers} flowers`;

                    modal.classList.add('active');
                });
            });

            closeButton.addEventListener('click', () => {
                modal.classList.remove('active');
            });

            modal.addEventListener('click', (e) => {
                if (e.target === modal) {
                    modal.classList.remove('active');
                }
            });
        });
    </script>

    <script>
                            document.querySelectorAll('.flower-button').forEach(button => {
                                button.addEventListener('click', function () {
                                    const artworkId = this.dataset.artworkId;
                                    const csrfToken = getCookie('csrftoken');

                                    console.log('Flower button clicked for artwork:', artworkId);
                                    console.log('CSRF Token:', csrfToken);

                                    fetch('/profiles/toggle-flower/', {
                                        method: 'POST',
                                        headers: {
                                            'Content-Type': 'application/json',
                                            'X-CSRFToken': csrfToken,
                                        },
                                        body: JSON.stringify({ artworkId: artworkId }),
                                    })
                                        .then(response => response.json())
                                        .then(data => {
                                            console.log('Server Response:', data);
                                            if (data.flowered) {
                                                this.classList.add('flowered');
                                            } else {
                                                this.classList.remove('flowered');
                                            }
                                            document.querySelector(`#flower-count-${artworkId}`).textContent = data.flowerCount;
                                        })
                                        .catch(error => {
                                            console.error('Error during AJAX request:', error);
                                        });
                                    });
                                    });

                                    function getCookie(name) {
                                    let cookieValue = null;
                                    if (document.cookie && document.cookie !== '') {
                                    const cookies = document.cookie.split(';');
                                    for (let i = 0; i < cookies.length; i++) {
                                        const cookie = cookies[i].trim();
                                        if (cookie.startsWith(name + '=')) {
                                            cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                                            break;
                                        }
                                    }
                                    }
                                    return cookieValue;
                                    }

                            function toggleFlower(artworkId) {
                                const flowerCountElement = document.getElementById(`flower-count-${artworkId}`);
                                const flowerButton = document.getElementById(`flower-button-${artworkId}`);
                                const flowerAnimationContainer = document.getElementById(`flower-animation-container-${artworkId}`);

                                fetch('/profiles/toggle-flower/', {
                                    method: 'POST',
                                    headers: {
                                        'Content-Type': 'application/json',
                                        'X-CSRFToken': getCookie('csrf_token'),
                                    },
                                    body: JSON.stringify({ artwork_id: artworkId }),
                                })
                                .then(response => {
                                    if (response.ok) {
                                        return response.json();
                                    } else {
                                        throw new Error('Failed to toggle flower');
                                    }
                                })
                                .then(data => {
                                    if (data.success) {
                                        // Update the flower count
                                        flowerCountElement.textContent = data.flowers;

                                        // Add or remove the flowered class
                                        if (data.flowered) {
                                            flowerButton.classList.add('flowered');
                                            createFlowerBubble(flowerAnimationContainer);
                                        } else {
                                            flowerButton.classList.remove('flowered');
                                        }
                                    } else {
                                        console.error('Error:', data.error);
                                    }
                                })
                                .catch(error => console.error('Error:', error));
                            }

                            // Helper function to create artistic flower bubbles
                            function createFlowerBubble(container) {
                                const bubble = document.createElement('div');
                                bubble.className = 'flower-bubble';
                                bubble.textContent = '🌸'; // Use a flower emoji

                                // Randomize size and position for a natural effect
                                const size = Math.random() * 20 + 20; // Size between 20px and 40px
                                bubble.style.width = `${size}px`;
                                bubble.style.height = `${size}px`;
                                bubble.style.left = `${Math.random() * 80}%`;

                                container.appendChild(bubble);

                                // Animate the bubble upward and fade out
                                setTimeout(() => {
                                    bubble.style.transform = `translateY(-200px)`;
                                    bubble.style.opacity = 0;
                                }, 50);

                                // Remove the bubble after animation
                                setTimeout(() => {
                                    bubble.remove();
                                }, 2000);
                            }

                            // Helper function to get CSRF token
                            function getCookie(name) {
                                const value = `; ${document.cookie}`;
                                const parts = value.split(`; ${name}=`);
                                if (parts.length === 2) return parts.pop().split(';').shift();
                            }
