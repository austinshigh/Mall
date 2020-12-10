document.addEventListener('DOMContentLoaded', function() {
    // By default, load all functions
    changePhoto();
    reviewCount();
    changeQuant();
    checkOut();
});

function checkOut(){
    // Verify that user is on Cart page
    if (document.querySelector('#check-out')){

        // Listen for click on checkout button
        const submitBtn = document.querySelector('#check-out');
        submitBtn.addEventListener('click', function() {

            // Hide cart view on submit and display loading view
            document.querySelector('#cart-view').style.display='none';
            const loadingView = document.querySelector('#loading-view');
            loadingView.style.display='block';

            // Create reference to CSRF token
            const token = document.querySelector(`input[name="csrfmiddlewaretoken"]`).value;

            // Make get request to perform checkout process in views.py
            fetch("/checkout")
            .then(response => response.json())
            .then(result => {
                // If checkout successful, return invoice number and show order received view
                document.querySelector('#invoice-number').innerHTML='#' + result;
                loadingView.style.display='none';
                document.querySelector('#received-view').style.display='block';
            }).catch(() => {
                console.log('Cart Submit failed.');
            });    
        });
    }
}


// Function changes the source of the visible photo to the hidden photo's source
function photoOn(){
    const photoId = this.dataset.photo;
    const photo = document.querySelector(`.hidden[data-photo="${photoId}"]`);
    if (photo != null){
        const temp = this.src;
        this.src = photo.src;
        photo.src = temp;
    }
}


// Function reverts source of visible photo back to its original
function photoAway(){
    const photoId = this.dataset.photo;
    const photo = document.querySelector(`.hidden[data-photo="${photoId}"]`);
    if (photo != null){
        const temp = this.src;
        this.src = photo.src;
        photo.src = temp;
    }
}


// Triggers photoOn and photoAway when user mouses over and mouses off image
function changePhoto(){
    document.querySelectorAll('.listing-photo').forEach(img => {
        img.addEventListener('mouseover', photoOn);
        img.addEventListener('mouseout', photoAway);
    });
}


function changeQuant(){
    // Generate event listener for each Update Quantity button
    document.querySelectorAll('.update-q').forEach(changeQ => {
        changeQ.addEventListener('click', function(event) {
            event.preventDefault();

            // Get current listing.id
            const listId = changeQ.dataset.listing;

            // Create variable referencing quantity input box
            const inputBox = document.querySelector(`.quant-input[data-listing="${listId}"]`);

            // Get value of number entered into quantity box
            let quantity = inputBox.value;

            // Create reference to cart total div
            const total = document.querySelector('#total');

            console.log(listId);

            // Show customer alert if quantity entered is greater than 999
            if (quantity > 999){
                alert("Quantity must be less than 1000");
            }
            else{
                if (quantity == 0){
                    // If quantity is zero, hide item and qty submit button to display the empty cart
                    const currentItem = document.querySelector(`.item[data-listing="${listId}"]`);
                    currentItem.style.display='none';
                    quantity = 0;
                }
                if (quantity >= 0){
                    // If quantity is a valid value, perform JSON PUT request

                    // Create reference to CSRF token
                    const token = document.querySelector(`input[name="csrfmiddlewaretoken"]`).value;
                
                    // Make PUT request to update cart in database
                    fetch('/change-quant/' + listId, {
                        method: "PUT",
                        headers: {
                            'X-CSRFToken': token,
                        },
                        body: JSON.stringify({
                            quantity: quantity
                        })
                    })
                    .then(response => response.json())
                    .then(result => {
                        // Set new total, or label cart as empty if cart empty.
                        if (result == 0){
                            total.innerHTML = 'Cart Empty.';
                            const checkOut = document.querySelector('#check-out');
                            checkOut.style.display='none';
                        }else{
                            total.innerHTML = 'Total = $' + result;
                        }
                    }).catch(() => {
                        console.log('Quantity change failed');
                    });
                }
            }
        });
    });
}


function reviewCount(){
    // Listen for click on like on each review
    document.querySelectorAll('.like').forEach(div => {
        div.addEventListener('click', function() {
                
            // Create reference to like counter
            const reviewId = div.dataset.review;
            const counter = document.querySelector(`.counter[data-review="${reviewId}"]`);

            // Create reference to CSRF token
            const token = document.querySelector(`input[name="csrfmiddlewaretoken"]`).value; 

            // Send post request to generate new 'like' instance in database
            fetch('/feedback', {
                method: 'POST',
                headers: {
                    'X-CSRFToken': token,
                },
                body: JSON.stringify({
                    review: reviewId
                })
            })
            .then(response => response.json())
            .then(result => {
                // Set innerHTML of counter to new total count value
                counter.innerHTML = result.newCount;
            }).catch(() => {
                console.log('Quantity change failed.');
            });
        });
    });
}
