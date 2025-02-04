(function renderTripPlanner() {
  const plannerEl = document.getElementById('trip-planner');

  if (!plannerEl) return;

  // Main container styling
  const container = document.createElement('div');
  Object.assign(container.style, {
      maxWidth: '1200px',
      margin: '2rem auto',
      padding: '2rem',
      backgroundColor: '#fff',
      borderRadius: '8px',
      boxShadow: '0 2px 8px rgba(0,0,0,0.1)'
  });

  // Title
  const title = document.createElement('h1');
  title.textContent = 'Plan Your Trip with an AI Agent';
  Object.assign(title.style, {
      textAlign: 'center',
      marginBottom: '2rem',
      color: '#003580'
  });
  container.appendChild(title);

  // Main form
  const form = document.createElement('form');
  form.style.display = 'grid';
  form.style.gap = '2rem';

  // First Row - Input Grid
  const inputGrid = document.createElement('div');
  Object.assign(inputGrid.style, {
      display: 'grid',
      gridTemplateColumns: 'repeat(4, 1fr)',
      gap: '1rem'
  });

  // Input Group Factory with Enhanced Styling
  const createInputGroup = (id, labelText, type = 'text') => {
    const group = document.createElement('div');
    group.style.display = 'flex';
    group.style.flexDirection = 'column';

    const label = document.createElement('label');
    label.textContent = labelText;
    label.htmlFor = id;
    label.style.fontWeight = 'bold';

    const input = document.createElement('input');
    input.type = type;
    input.id = id;
    input.style.width = '100%';
    input.style.padding = '0.8rem';
    input.style.border = '2px solid orange'; // Thicker border
    input.style.borderRadius = '8px'; // Rounded edges
    input.style.outline = 'none';
    input.style.transition = 'border-color 0.3s ease';

    // Add a hover/focus effect
    input.addEventListener('focus', () => {
        input.style.borderColor = '#FF4500'; // Darker orange on focus
    });
    input.addEventListener('blur', () => {
        input.style.borderColor = 'orange'; // Reset to default
    });

    group.append(label, input);
    return group;
  };


//   // Input Group Factory
//   const createInputGroup = (id, labelText, type = 'text') => {
//     const group = document.createElement('div');
//     const label = document.createElement('label');
//     label.textContent = labelText;
//     label.htmlFor = id;
//     const input = document.createElement('input');
//     input.type = type;
//     input.id = id;
//     input.style.width = '100%';
//     input.style.padding = '0.8rem';
//     group.append(label, input);
//     return group;
// };

  // Origin Input with Google Places
  const originGroup = createInputGroup('origin', 'Where from?');
  inputGrid.appendChild(originGroup);

  // Destination Input with Google Places
  const destGroup = createInputGroup('destination', 'Where to?');
  inputGrid.appendChild(destGroup);

  // Date Range Picker
  const dateGroup = document.createElement('div');
  dateGroup.style.display = 'flex';
  dateGroup.style.flexDirection = 'column';

  const dateLabel = document.createElement('label');
  dateLabel.textContent = 'Travel Dates';
  dateLabel.htmlFor = 'date-range';
  dateLabel.style.fontWeight = 'bold';

  const dateInput = document.createElement('input');
  dateInput.id = 'date-range';
  dateInput.placeholder = 'Select date range...';
  dateInput.style.width = '100%';
  dateInput.style.padding = '0.8rem';
  dateInput.style.border = '2px solid orange'; // Thicker border
  dateInput.style.borderRadius = '8px'; // Rounded edges
  dateInput.style.outline = 'none';
  dateInput.style.transition = 'border-color 0.3s ease';

  // Add hover/focus effect
  dateInput.addEventListener('focus', () => {
    dateInput.style.borderColor = '#FF4500'; // Darker orange on focus
  });
  dateInput.addEventListener('blur', () => {
    dateInput.style.borderColor = 'orange'; // Reset to default
  });

  dateGroup.append(dateLabel, dateInput);
  inputGrid.appendChild(dateGroup);


  // Travelers Input (Adults and Children)
  const travelersDiv = document.createElement('div');
  travelersDiv.style.display = 'grid';

  const travelersLabel = document.createElement('label');
  travelersLabel.textContent = 'Adults / Children';
  travelersLabel.style.display = 'block';
  travelersLabel.style.fontWeight = 'bold';

  const travelerFlex = document.createElement('div');
  Object.assign(travelerFlex.style, {
      display: 'flex',
      gap: '0.5rem',
      alignItems: 'center'
  });

  // Reusable function for traveler input with improved styling
  const createTravelerInput = (id, placeholder, min, defaultValue) => {
      const input = document.createElement('input');
      input.type = 'number';
      input.id = id;
      input.min = min;
      input.value = defaultValue;
      input.placeholder = placeholder;
      input.style.width = '100%';
      input.style.padding = '0.8rem';
      input.style.border = '2px solid orange'; // Thicker border
      input.style.borderRadius = '8px'; // Rounded edges
      input.style.outline = 'none';
      input.style.transition = 'border-color 0.3s ease';

      // Hover/focus effect
      input.addEventListener('focus', () => {
          input.style.borderColor = '#FF4500';
      });
      input.addEventListener('blur', () => {
          input.style.borderColor = 'orange';
      });

      return input;
  };

  const adultsInput = createTravelerInput('adults', 'Adults', '1', '1');
  const childrenInput = createTravelerInput('children', 'Children', '0', '0');

  // Append elements
  travelerFlex.append(adultsInput, childrenInput);
  travelersDiv.append(travelersLabel, travelerFlex);
  inputGrid.appendChild(travelersDiv);

  form.appendChild(inputGrid);

  // Initialize Flatpickr for date range
  const flatpickrInstance = flatpickr(dateInput, {
      mode: "range",
      minDate: "today",
      dateFormat: "Y-m-d",
      showMonths: 2,
      static: true
  });

  // Create a separate container for voice input outside the form
  const voiceContainer = document.createElement('div');
  Object.assign(voiceContainer.style, {
    position: 'fixed',
    left: '150px', // Move to left side
    top: '60%', // Center vertically
    // transform: 'translateY(-50%)', // Adjust to true center
    zIndex: '1000',
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    cursor: 'move' // Add cursor indication
  });

  // Microphone Label Container
  const micLabelContainer = document.createElement('div');
  Object.assign(micLabelContainer.style, {
    backgroundColor: '#f0f0f0',
    border: '2px solid #003580',
    borderRadius: '8px',
    padding: '10px',
    marginBottom: '15px',
    maxWidth: '200px',
    textAlign: 'center',
    boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
    cursor: 'move',
    userSelect: 'none',
    WebkitUserSelect: 'none'
  });

  // Microphone Label
  const micLabel = document.createElement('div');
  Object.assign(micLabel.style, {
    color: '#003580',
    fontWeight: 'bold',
    fontSize: '1rem'
  });
  micLabel.textContent = 'Tell Us More about Your Trip';

// Add label to container
micLabelContainer.appendChild(micLabel);

  // Drag functionality
  let isDragging = false;
  let initialX;
  let initialY;
  let initialLeft;
  let initialTop;

  const startDrag = (e) => {
    isDragging = true;
    initialX = e.clientX;
    initialY = e.clientY;
    const rect = voiceContainer.getBoundingClientRect();
    initialLeft = rect.left;
    initialTop = rect.top;
    
    document.addEventListener('mousemove', drag);
    document.addEventListener('mouseup', stopDrag);
    e.preventDefault();
  };
  
  const drag = (e) => {
    if (!isDragging) return;
    const deltaX = e.clientX - initialX;
    const deltaY = e.clientY - initialY;
    
    voiceContainer.style.left = `${initialLeft + deltaX}px`;
    voiceContainer.style.top = `${initialTop + deltaY}px`;
  };
  
  const stopDrag = () => {
    isDragging = false;
    document.removeEventListener('mousemove', drag);
    document.removeEventListener('mouseup', stopDrag);
  };

  // Add event listeners to mic label container
  micLabelContainer.addEventListener('mousedown', startDrag);

  // Microphone Button
  const micBtn = document.createElement('button');
  Object.assign(micBtn.style, {
    width: '80px',
    height: '80px',
    borderRadius: '50%',
    border: 'none',
    background: 'linear-gradient(45deg, #007bff, #ff6b35)',
    color: 'white',
    fontSize: '1.2rem',
    cursor: 'pointer',
    display: 'flex',
    justifyContent: 'center',
    alignItems: 'center',
    boxShadow: '0 4px 6px rgba(0,0,0,0.1)'
  });

  voiceContainer.appendChild(micLabelContainer);
  voiceContainer.appendChild(micBtn);


  const micIcon = document.createElement('i');
  micIcon.className = 'fas fa-microphone';
  micBtn.appendChild(micIcon);

  // // Append label before microphone button
  // voiceContainer.insertBefore(micLabel, micBtn);

  // Transcription Popup
  const transcriptPopup = document.createElement('div');
  Object.assign(transcriptPopup.style, {
    display: 'none',
    position: 'fixed',
    bottom: '100px',
    right: '-20px',
    width: '300px',
    padding: '1rem',
    backgroundColor: 'white',
    border: '2px solid orange',
    borderRadius: '8px',
    boxShadow: '0 4px 6px rgba(0,0,0,0.2)',
    zIndex: '1000'
  });

  const transcriptBox = document.createElement('textarea');
  Object.assign(transcriptBox.style, {
    width: '100%',
    height: '120px',
    padding: '0.5rem',
    border: '1px solid #ccc',
    borderRadius: '4px',
    resize: 'vertical'
  });
  transcriptBox.placeholder = 'Your voice input will appear here...';

  // Close button for popup
  const closeBtn = document.createElement('button');
  closeBtn.textContent = 'Close';
  Object.assign(closeBtn.style, {
    marginTop: '10px',
    padding: '0.5rem 1rem',
    backgroundColor: '#0071C2',
    color: 'white',
    border: 'none',
    borderRadius: '4px',
    cursor: 'pointer'
  });
  closeBtn.addEventListener('click', () => {
    transcriptPopup.style.display = 'none';
  });

  transcriptPopup.append(transcriptBox, closeBtn);

  // Speech Recognition Setup
  const recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
  recognition.lang = 'en-US';
  recognition.continuous = false;
  recognition.interimResults = false;

  recognition.onstart = () => {
    micIcon.className = 'fas fa-stop-circle';
    micBtn.style.background = 'linear-gradient(45deg, #ff6b35, #007bff)';
    transcriptBox.value = '';
  };

  recognition.onresult = (event) => {
    const transcript = event.results[0][0].transcript;
    transcriptBox.value = transcript;
  };

  recognition.onend = () => {
    micIcon.className = 'fas fa-microphone';
    micBtn.style.background = 'linear-gradient(45deg, #007bff, #ff6b35)';
    
    // Show popup only after recording is complete
    if (transcriptBox.value.trim()) {
      transcriptPopup.style.display = 'block';
    }
  };

  // Prevent form submission
  micBtn.addEventListener('click', (event) => {
    event.preventDefault();
    event.stopPropagation();
    
    if (micIcon.className.includes('fa-microphone')) {
      recognition.start();
    } else {
      recognition.stop();
    }
  });

  // Append to container
  voiceContainer.append(micBtn, transcriptPopup);
  plannerEl.appendChild(voiceContainer);

  // Email Input
  const emailGroup = createInputGroup('email', 'Enter your Email', 'email');
  emailGroup.querySelector('input').placeholder = 'example@mail.com';
  form.appendChild(emailGroup);

  // Send Button
  const submitBtn = document.createElement('button');
  submitBtn.type = 'button';
  submitBtn.textContent = 'Send';
  Object.assign(submitBtn.style, {
      padding: '1rem 2rem',
      backgroundColor: '#0071C2',
      color: 'white',
      border: 'none',
      borderRadius: '5px',
      cursor: 'pointer',
      fontSize: '1.1rem',
      transition: 'background-color 0.3s'
  });

  submitBtn.addEventListener('click', () => {
    const formData = {
      origin: document.getElementById('origin').value,
      destination: document.getElementById('destination').value,
      dates: flatpickrInstance.selectedDates.map(date => date.toISOString().split('T')[0]), // Convert dates to ISO strings,
      adults: document.getElementById('adults').value,
      children: document.getElementById('children').value,
      email: document.getElementById('email').value,
      voiceNotes: transcriptBox.value
    };
  
    // Check if required fields are filled
    if (!formData.origin || !formData.destination || !formData.dates.length || !formData.adults || !formData.email) {
      alert('Please fill in all required fields before submitting.');
      return;
    }
  
    // Send data to FastAPI using fetch
    fetch('/submit-trip', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(formData)  // Send data as JSON to backend
    })
    .then(response => response.json())  // Expecting JSON response from backend
    .then(data => {
      console.log('Response from backend:', data);
      window.location.href = '/thank-you';  // Redirect to thank-you page
    })
    .catch(error => {
      console.error('Error:', error);
      alert('There was an error submitting your form. Please try again.');
    });
    
  });
  

  form.appendChild(submitBtn);
  container.appendChild(form);
  plannerEl.appendChild(container);

  // Google Places Autocomplete
  function initAutocomplete() {
    const originInput = document.getElementById('origin');
    const destInput = document.getElementById('destination');
    
    if (window.google && window.google.maps && window.google.maps.places) {
      new google.maps.places.Autocomplete(originInput, { types: ['(cities)'] });
      new google.maps.places.Autocomplete(destInput, { types: ['(cities)'] });
    } else {
      console.error('Google Places API not loaded');
    }
  }
  
  window.initAutocomplete = initAutocomplete;



  function initAutocomplete() {
    const originInput = document.getElementById('origin');
    const destInput = document.getElementById('destination');

    new google.maps.places.Autocomplete(originInput, {types: ['(cities)'] } );
    new google.maps.places.Autocomplete(destInput, { types: ['(cities)'] });
  }
  window.initAutocomplete = initAutocomplete;
})();