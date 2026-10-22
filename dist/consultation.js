(() => {
  const form = document.querySelector('.hub-consultation-form');
  if (!form) return;
  const fields = [...form.querySelectorAll('.hub-form-field input')];
  const status = form.querySelector('.hub-form-status');
  const button = form.querySelector('button[type="submit"]');
  const buttonText = button.textContent;
  let sending = false;
  form.noValidate = true;

  function validate(field) {
    const value = field.value.trim();
    let message = '';
    if (!value) message = `Enter your ${field.name === 'name' ? 'full name' : field.name === 'phone' ? 'phone number' : 'email address'}.`;
    else if (field.name === 'email' && field.validity.typeMismatch) message = 'Enter a valid email address, such as name@example.com.';
    else if (field.name === 'phone') {
      const digits = value.replace(/\D/g, '').length;
      if (!/^[+()\d\s.-]+$/.test(value) || digits < 7 || digits > 15) message = 'Enter a phone number with 7 to 15 digits.';
    }
    const error = document.getElementById(`${field.id}-error`);
    error.textContent = message;
    error.hidden = !message;
    if (message) field.setAttribute('aria-invalid', 'true');
    else field.removeAttribute('aria-invalid');
    return !message;
  }

  function showStatus(message, state) {
    status.textContent = message;
    status.dataset.state = state;
    status.setAttribute('role', state === 'error' ? 'alert' : 'status');
    status.hidden = false;
  }

  fields.forEach(field => field.addEventListener('input', () => {
    if (field.hasAttribute('aria-invalid')) validate(field);
  }));

  form.addEventListener('submit', async event => {
    event.preventDefault();
    if (sending) return;
    const results = fields.map(validate);
    if (results.includes(false)) {
      showStatus('Please check the fields above.', 'error');
      fields[results.indexOf(false)].focus();
      return;
    }
    fields.forEach(field => { field.value = field.value.trim(); });
    sending = true;
    button.disabled = true;
    button.textContent = 'Sending…';
    showStatus('Sending your request…', 'pending');

    const submissionOrigin = new URL(form.dataset.submissionOrigin).origin;
    if (location.origin !== submissionOrigin) {
      // Native navigation allows the Sites preview to submit to the same Netlify form.
      form.action = new URL(form.getAttribute('action'), submissionOrigin).href;
      HTMLFormElement.prototype.submit.call(form);
      return;
    }

    try {
      const response = await fetch(form.action, {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: new URLSearchParams(new FormData(form)).toString()
      });
      if (!response.ok) throw new Error('Submission failed');
      form.querySelector('.hub-form-fields').hidden = true;
      showStatus('Thank you. We’ve received your request and will contact you about your project.', 'success');
      form.reset();
      status.focus();
    } catch {
      showStatus('We couldn’t send your request. Please try again or call (818) 884-5464.', 'error');
      status.focus();
    } finally {
      sending = false;
      button.disabled = false;
      button.textContent = buttonText;
    }
  });
})();
